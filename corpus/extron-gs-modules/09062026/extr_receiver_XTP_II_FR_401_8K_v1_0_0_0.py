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
            'AudioMute': { 'Status': {}},
            'AutoSwitchMode': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Firmware': { 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters':['Input'], 'Status': {}},
            'HDCPOutputStatus': { 'Status': {}},
            'Input': { 'Status': {}},
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}}
        }

        self.VerboseEnabled = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Amt([0-3])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'Exe([0-1])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Bld(\d.\d{2}.\d{4})\r\n'), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(b'HdcpE([1-2])\*([0-1])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI([0-2])([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO([0-7])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'In([1-2])\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Frq([0-1])([0-1])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vol(\d{1,3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'E(\d{2})\r\n'), self.__MatchError, None)
    
    def SetAudioMute(self, value, qualifier):
        
        ValueStateValues = {
            'Off': '0',
            'Digital': '1',
            'Analog': '2',
            'Analog + HDMI': '3'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = '{}Z'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        self.__UpdateHelper('AudioMute', 'Z', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Digital',
            '2': 'Analog',
            '3': 'Analog + HDMI'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Highest Active Priority': '1',
            'Lowest Active Input': '2'
            }

        if value in ValueStateValues:
            AutoSwitchModeCmdString = 'w{}AUSW\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSwitchMode')

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Highest Active Priority',
            '2': 'Lowest Active Input'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{}X'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def UpdateFirmware(self, value, qualifier):

        FirmwareCmdString = '*q'
        self.__UpdateHelper('Firmware', FirmwareCmdString, value, qualifier)

    def __MatchFirmware(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Firmware', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if 1 <= int(qualifier['Input']) <= 2 and value in ValueStateValues:
            HDCPInputAuthorizationCmdString = 'wE{}*{}HDCP\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 2:
            HDCPInputAuthorizationCmdString = 'wE{0}HDCP\r'.format(qualifier['Input'])
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {
            'Input': str(int(match.group(1).decode()))
        }
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):

        HDCPInputStatusCmdString = 'wIHDCP\r'
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Device Detected',
            '1': 'Source Detected with HDCP',
            '2': 'Source Detected without HDCP'
            }

        in1 = ValueStateValues[match.group(1).decode()]
        in2 = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', in1, {'Input': '1'})
        self.WriteStatus('HDCPInputStatus', in2, {'Input': '2'})

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'wOHDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Sink Device Detected',
            '2': 'No Sink Device Detected',
            '4': 'No Sink Device Detected',
            '6': 'No Sink Device Detected',
            '1': 'Sink Detected without Output Encrypt',
            '3': 'Sink Detected without Output Encrypt',
            '5': 'Sink Detected without Output Encrypt',
            '7': 'Sink Detected with Output Encrypt'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetInput(self, value, qualifier):

        if 1 <= int(value) <= 2:
            InputCmdString = '{}!'.format(value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = '0LS'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
            }

        in1 = ValueStateValues[match.group(1).decode()]
        in2 = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputSignalStatus', in1, {'Input': '1'})
        self.WriteStatus('InputSignalStatus', in2, {'Input': '2'})

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Video': '1',
            'Video & Sync': '2',
            'Off': '0'
            }

        if value in ValueStateValues:
            VideoMuteCmdString = '{}B'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '2': 'Video & Sync',
            '1': 'Video',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 64:
            VolumeCmdString = '{}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 64:
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True        
        self.Send(commandstring)

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

            self.Send(commandstring)
    
    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input channel number',
            'E06': 'Invalid input selection during auto-input switching',   
            'E10': 'Invalid Command',
            'E13': 'Invalid value(out of range)',
            'E14': 'Not valid for this configuration',
            'E17': 'Invalid command for signal type',
        }  

        value = match.group(1).decode()
        self.Error(['An error occurred: ' + DEVICE_ERROR_CODES.get(value, value + ': Unknown error')])

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