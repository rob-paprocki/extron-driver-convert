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
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'AutoCECMode': {'Parameters': ['Output'], 'Status': {}},
            'CECPower': {'Parameters': ['Output'], 'Status': {}},
            'CECPowerOffDelayTime': {'Parameters': ['Output'], 'Status': {}},
            'InputEDID': {'Parameters': ['Input'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output'], 'Status': {}},
            'Reboot': { 'Status': {}},
            'Version': { 'Status': {}},
        }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'MUTE (audioout1|audioout2|hdmiaudioout1|hdmiaudioout2|spdifaudioout1|spdifaudioout2) (on|off)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'AUTOCEC_FN out([12]) (on|off)\r\n'), self.__MatchAutoCECMode, None)
            self.AddMatchString(re.compile(b'AUTOCEC_D out([12]) (\d+)\r\n'), self.__MatchCECPowerOffDelayTime, None)
            self.AddMatchString(re.compile(b'EDID GET in([1-4]) ([1-9]|1[01])\r\n'), self.__MatchInputEDID, None)
            self.AddMatchString(re.compile(b'MP in([1-4]) out([12])\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(re.compile(b'VER (.*)\r\n'), self.__MatchVersion, None)

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            'Audio Out 1'       : 'audioout1',
            'Audio Out 2'       : 'audioout2',
            'HDMI Audio Out 1'  : 'hdmiaudioout1',
            'HDMI Audio Out 2'  : 'hdmiaudioout2',
            'S/PDIF Audio Out 1': 'spdifaudioout1',
            'S/PDIF Audio Out 2': 'spdifaudioout2'
        }

        ValueStateValues = {
            'On' : 'on',
            'Off': 'off'
        }

        if qualifier['Output'] in OutputStates and value in ValueStateValues:
            self.__SetHelper('AudioMute', 'SET MUTE {o} {x}\r\n'.format(o=OutputStates[qualifier['Output']], x=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        OutputStates = {
            'Audio Out 1'       : 'audioout1',
            'Audio Out 2'       : 'audioout2',
            'HDMI Audio Out 1'  : 'hdmiaudioout1',
            'HDMI Audio Out 2'  : 'hdmiaudioout2',
            'S/PDIF Audio Out 1': 'spdifaudioout1',
            'S/PDIF Audio Out 2': 'spdifaudioout2'
        }

        if qualifier['Output'] in OutputStates:
            self.__UpdateHelper('AudioMute', 'GET MUTE {o}\r\n'.format(o=OutputStates[qualifier['Output']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        OutputStates = {
            'audioout1'     : 'Audio Out 1',
            'audioout2'     : 'Audio Out 2',
            'hdmiaudioout1' : 'HDMI Audio Out 1',
            'hdmiaudioout2' : 'HDMI Audio Out 2',
            'spdifaudioout1': 'S/PDIF Audio Out 1',
            'spdifaudioout2': 'S/PDIF Audio Out 2',
        }

        ValueStateValues = {
            'on' : 'On',
            'off': 'Off'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAutoCECMode(self, value, qualifier):

        ValueStateValues = {
            'On' : 'on',
            'Off': 'off'
        }

        if qualifier['Output'] in ['1', '2'] and value in ValueStateValues:
            self.__SetHelper('AutoCECMode', 'SET AUTOCEC_FN out{o} {x}\r\n'.format(o=qualifier['Output'], x=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoCECMode')

    def UpdateAutoCECMode(self, value, qualifier):

        if qualifier['Output'] in ['1', '2']:
            self.__UpdateHelper('AutoCECMode', 'GET AUTOCEC_FN out{o}\r\n'.format(o=qualifier['Output']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutoCECMode')

    def __MatchAutoCECMode(self, match, tag):

        ValueStateValues = {
            'on' : 'On',
            'off': 'Off'
        }

        qualifier = {}
        qualifier['Output'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutoCECMode', value, qualifier)

    def SetCECPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'on',
            'Off': 'off'
        }

        if qualifier['Output'] in ['1', '2'] and value in ValueStateValues:
            self.__SetHelper('CECPower', 'SET CEC_PWR out{o} {x}\r\n'.format(o=qualifier['Output'], x=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECPower')

    def SetCECPowerOffDelayTime(self, value, qualifier):

        if qualifier['Output'] in ['1', '2'] and 1 <= int(value) <= 60:
            self.__SetHelper('CECPowerOffDelayTime', 'SET AUTOCEC_D out{o} {t}\r\n'.format(o=qualifier['Output'], t=value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECPowerOffDelayTime')

    def UpdateCECPowerOffDelayTime(self, value, qualifier):

        if qualifier['Output'] in ['1', '2']:
            self.__UpdateHelper('CECPowerOffDelayTime', 'GET AUTOCEC_D out{o}\r\n'.format(o=qualifier['Output']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCECPowerOffDelayTime')

    def __MatchCECPowerOffDelayTime(self, match, tag):

        qualifier = {}
        qualifier['Output'] = match.group(1).decode()
        value = match.group(2).decode()
        self.WriteStatus('CECPowerOffDelayTime', value, qualifier)

    def SetInputEDID(self, value, qualifier):

        ValueStateValues = {
            'Default'                 : '1',
            'Output 1'                : '2',
            'Output 2'                : '3',
            '4K@60Hz (2.0ch with HDR)': '4',
            '4K@60Hz (5.1ch with HDR)': '5',
            '4K@60Hz (7.1ch with HDR)': '6',
            '4K@30Hz (2.0ch with HDR)': '7',
            '4K@30Hz (7.1ch with HDR)': '8',
            '1080p@60Hz (2.0ch)'      : '9',
            '1080p@60Hz (5.1ch)'      : '10',
            '1080p@60Hz (7.1ch)'      : '11'
        }

        if 1 <= int(qualifier['Input']) <= 4 and value in ValueStateValues:
            self.__SetHelper('InputEDID', 'SET EDID in{i} {r}\r\n'.format(i=qualifier['Input'], r=ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputEDID')

    def UpdateInputEDID(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            self.__UpdateHelper('InputEDID', 'GET EDID in{i}\r\n'.format(i=qualifier['Input']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputEDID')

    def __MatchInputEDID(self, match, tag):

        ValueStateValues = {
            '1' : 'Default',
            '2' : 'Output 1',
            '3' : 'Output 2',
            '4' : '4K@60Hz (2.0ch with HDR)',
            '5' : '4K@60Hz (5.1ch with HDR)',
            '6' : '4K@60Hz (7.1ch with HDR)',
            '7' : '4K@30Hz (2.0ch with HDR)',
            '8' : '4K@30Hz (7.1ch with HDR)',
            '9' : '1080p@60Hz (2.0ch)',
            '10': '1080p@60Hz (5.1ch)',
            '11': '1080p@60Hz (7.1ch)'
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputEDID', value, qualifier)

    def SetMatrixTieCommand(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4 and qualifier['Output'] in ['1', '2', 'All']:
            output = 'all' if not qualifier['Output'].isdigit() else 'out{}'.format(qualifier['Output'])
            self.__SetHelper('MatrixTieCommand', 'SET SW in{i} {o}\r\n'.format(i=qualifier['Input'], o=output), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def UpdateOutputTieStatus(self, value, qualifier):

        if qualifier['Output'] in ['1', '2']:
            self.__UpdateHelper('OutputTieStatus', 'GET MP out{o}\r\n'.format(o=qualifier['Output']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputTieStatus')

    def __MatchOutputTieStatus(self, match, tag):

        qualifier = {}
        qualifier['Output'] = match.group(2).decode()
        value = match.group(1).decode()
        self.WriteStatus('OutputTieStatus', value, qualifier)

    def SetReboot(self, value, qualifier):

        self.__SetHelper('Reboot', 'REBOOT\r\n', value, qualifier)

    def UpdateVersion(self, value, qualifier):

        self.__UpdateHelper('Version', 'GET VER\r\n', value, qualifier)

    def __MatchVersion(self, match, tag):

        self.WriteStatus('Version', match.group(1).decode(), None)

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