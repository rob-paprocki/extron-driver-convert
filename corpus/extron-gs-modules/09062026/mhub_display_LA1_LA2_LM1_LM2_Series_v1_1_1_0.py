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
            'AspectRatio': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
            'SceneMode': { 'Status': {}},
            'ScreenModeSwitching': { 'Status': {}},
            'TemperatureMode': { 'Status': {}},
            'Volume': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x55{7}\xC0\x01\x03\x00\xD1\x01\xD0\x0E\xC2\x00\x00\xFF{17}\x00\x01\x00(\x01|\x02|\x03|\x04)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x55{7}\xC0\x01\x03\x00\xD1\x01\xD0\x1E\xC2\x00\x00\xFF{17}\x00\x01\x00([\x00-\x64])[\x00-\xFF]'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'\x55{7}\xC0\x01\x03\x00\xD1\x01\xD0\x12\xC2\x00\x00\xFF{17}\x00\x01\x00(\x00|\x02|\x03|\x04)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x55{7}\xC0\x01\x03\x00\xD1\x01\xD0\x06\xC0\x00\x00\xFF{17}\x00\x01\x00(\x80|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x55{7}\xC0\x01\x03\x00\xD1\x01\xD0\x44\xC2\x00\x00\xFF{17}\x00\x01\x00(\x00|\x01|\x02|\x03)[\x00-\xFF]'), self.__MatchSceneMode, None)
            self.AddMatchString(re.compile(b'\x55{7}\xC0\x01\x03\x00\xD1\x01\xD0\x02\xC2\x00\x00\xFF{17}\x00\x01\x00([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3':      b'\x01\x68',
            '16:9':     b'\x02\x69',
            'Full':     b'\x03\x6A',
            'Original': b'\x04\x6B'
            }

        if value in ValueStateValues:
            AspectRatioCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x0F\xC2\x00\x00' + 
                                    b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                                    b'\x00\x01\x00' + ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x0D\xC2\x00\x00' + 
                                b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                                b'\x00\x00\x00\x64')
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x01': '4:3',
            b'\x02': '16:9',
            b'\x03': 'Full',
            b'\x04': 'Original'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AspectRatio', value, None)

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            checkSum = (value + 119).to_bytes(1,'big')
            BrightnessCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x1F\xC2\x00\x00' + 
                                   b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                                   b'\x00\x01\x00' + value.to_bytes(1,'big') + checkSum)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')
    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x1D\xC2\x00\x00' + 
                               b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                               b'\x00\x00\x00\x74')
        self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)

    def __MatchBrightness(self, match, tag):

        value = ord(match.group(1))
        if 0 <= value <= 100:
            self.WriteStatus('Brightness', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Android': b'\x00\x6B',
            'HDMI 1':  b'\x02\x6D',
            'HDMI 2':  b'\x03\x6E',
            'HDMI 3':  b'\x04\x6F'
            }

        if value in ValueStateValues:
            InputCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x13\xC2\x00\x00' + 
                              b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                              b'\x00\x01\x00' + ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x11\xC2\x00\x00' + 
                          b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                          b'\x00\x00\x00\x68')
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Android',
            b'\x02': 'HDMI 1',
            b'\x03': 'HDMI 2',
            b'\x04': 'HDMI 3'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x5E\xB7',
            'Off': b'\x5F\xB8'
            }

        if value in ValueStateValues:
            PowerCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x03\xC0\x00\x00' + 
                              b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                              b'\x00\x01\x00' + ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):


        PowerCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x05\xC0\x00\x00' + 
                          b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                          b'\x00\x00\x00\x5A')
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x80': 'On',
            b'\x00': 'Off'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetSceneMode(self, value, qualifier):

        ValueStateValues = {
            'Meeting':       b'\x00\x9D',
            'Presentation':  b'\x01\x9E',
            'Energy Saving': b'\x02\x9F',
            'Custom':        b'\x03\xA0'
            }

        if value in ValueStateValues:
            SceneModeCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x45\xC2\x00\x00' + 
                                  b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                                  b'\x00\x01\x00' + ValueStateValues[value])
            self.__SetHelper('SceneMode', SceneModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneMode')
            
    def UpdateSceneMode(self, value, qualifier):

        SceneModeCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x43\xC2\x00\x00' + 
                              b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                              b'\x00\x00\x00\x9A')
        self.__UpdateHelper('SceneMode', SceneModeCmdString, value, qualifier)

    def __MatchSceneMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Meeting',
            b'\x01': 'Presentation',
            b'\x02': 'Energy Saving',
            b'\x03': 'Custom'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('SceneMode', value, None)

    def SetScreenModeSwitching(self, value, qualifier):

        ValueStateValues = {
            'Full Screen': b'\x00\xA1',
            'Center':      b'\x01\xA2',
            'Duplicate':   b'\x02\xA3',
            'Custom':      b'\x20\xC1'
            }

        if value in ValueStateValues:
            ScreenModeSwitchingCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x49\xC2\x00\x00' + 
                                            b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                                            b'\x00\x01\x00' + ValueStateValues[value])
            self.__SetHelper('ScreenModeSwitching', ScreenModeSwitchingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenModeSwitching')

    def SetTemperatureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'\x01\x74',
            'Warm':     b'\x02\x75',
            'Cold':     b'\x03\x76',
            'Custom':   b'\x04\x77'
            }

        if value in ValueStateValues:
            TemperatureModeCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x1B\xC2\x00\x00' + 
                                        b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                                        b'\x00\x01\x00' + ValueStateValues[value])
            self.__SetHelper('TemperatureMode', TemperatureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTemperatureMode')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            checkSum = (value + 91).to_bytes(1,'big')
            VolumeCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x03\xC2\x00\x00' + 
                               b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                               b'\x00\x01\x00' + value.to_bytes(1,'big') + checkSum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = (b'\x55\x55\x55\x55\x55\x55\x55\xC0\x01\x03\x01\xD0\x00\xD1\x01\xC2\x00\x00' + 
                           b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' +
                           b'\x00\x00\x00\x58')
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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