# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import pack

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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x03\x0C\xF1\x03\x0C\xF5\x08\xF0\x02\x00\x00\xF1([\x00\x01])\x00\x00[\x11\x10]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x03\x0C\xF1\x03\x0C\xF5\x08\xF0\x04\x00\x00\xF1([\x00\x47\x48\x49\x4A])\x00\x00[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x03\x0C\xF1\x03\x0C\xF5\x08\xF0\x00\x00\x00\xF1([\x00\x04\x05])\x00\x00[\x13\x0F\x0E]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x03\x0C\xF1\x03\x0C\xF5\x08\xF0\x01\x00\x00\xF1([\x00-\x64])\x00\x00[\x00-\xFF]'), self.__MatchVolume, None)

    def build(self, cmd1, cmd2, cmd3, value):
    
        command_string = pack('6B', 0x08, 0x22, cmd1, cmd2, cmd3, value)
        checksum = bytes([(~sum(command_string) & 0xFF) + 1])

        return command_string + checksum
    
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3':      0x04,
            '16:9':     0x00,
            'Custom':   0x0B
        }

        if value in ValueStateValues:
            AspectRatioCmdString = self.build(0x0B, 0x0A, 0x01, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = self.build(0x0D, 0x00, 0x00, 0x0F)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = self.build(0xF0, 0x02, 0x00, 0x00)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x01,
            'Down': 0x02
        }

        if value in ValueStateValues:
            ChannelStepCmdString = self.build(0x03, 0x00, ValueStateValues[value], 0x00)
            self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV':       (0x00, 0x00),
            'HDMI 1':   (0x05, 0x00),
            'HDMI 2':   (0x05, 0x01),
            'HDMI 3':   (0x05, 0x02),
            'HDMI 4':   (0x05, 0x03)
        }

        if value in ValueStateValues:
            InputCmdString = self.build(0x0A, 0x00, ValueStateValues[value][0], ValueStateValues[value][1])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.build(0xF0, 0x04, 0x00, 0x00)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'TV',
            b'\x47': 'HDMI 1',
            b'\x48': 'HDMI 2',
            b'\x49': 'HDMI 3',
            b'\x4A': 'HDMI 4'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': 0x11,
            '1': 0x04,
            '2': 0x05,
            '3': 0x06,
            '4': 0x08,
            '5': 0x09,
            '6': 0x0A,
            '7': 0x0C,
            '8': 0x0D,
            '9': 0x0E
            }

        if 0 <= int(value) <= 9:
            KeypadCmdString = self.build(0x0D, 0x00, 0x00, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':     0x60,
            'Down':   0x61,
            'Left':   0x65,
            'Right':  0x62,
            'Menu':   0x1A,
            'Enter':  0x2E,
            'Return': 0x58,
            'Exit':   0x2D,
            'Home':   0x76
            }

        if value in ValueStateValues:
            MenuNavigationCmdString = self.build(0x0D, 0x00, 0x00, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   (0x0D, 0x02),
            'Off':  (0x00, 0x01)
        }

        if value in ValueStateValues:
            PowerCmdString = self.build(ValueStateValues[value][0], 0x00, 0x00, ValueStateValues[value][1])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.build(0xF0, 0x00, 0x00, 0x00)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x05': 'On',
            b'\x04': 'Off',
            b'\x00': 'Off'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = self.build(0x01, 0x00, 0x00, int(value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.build(0xF0, 0x01, 0x00, 0x00)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1))
        if 0 <= value <= 100:
            self.WriteStatus('Volume', value, None)

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()