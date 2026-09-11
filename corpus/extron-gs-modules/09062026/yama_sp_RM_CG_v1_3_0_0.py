from extronlib.interface import EthernetClientInterface
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
            'BeamDirectionPhiMeter': { 'Status': {}},
            'BeamDirectionThetaMeter': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'NearEndOutputFaderLevel': {'Parameters':['Channel'], 'Status': {}},
            'NearEndOutputMute': {'Parameters':['Channel'], 'Status': {}},
            'LEDBrightness': { 'Status': {}},
            'VoiceDetectionStatus': { 'Status': {}}
        }

        self.RunModeDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'NOTIFY mtr RM:BeamDirection raw (\w+) (\w+) 0?([01])\n'), self.__MatchBeamDirectionPhiMeter, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devstatus error "(none|fault|error|warning).*"\n'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:NeOut_Fader/Ch/Level ([01]) 0 (-?[0-9]{1,5}).*?\n'), self.__MatchNearEndOutputFaderLevel, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:NeOut_Mute/Ch/On ([01]) 0 ([01]).*?\n'), self.__MatchNearEndOutputMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:Led/Brightness 0 0 ([0-3]).*?\n'), self.__MatchLEDBrightness, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devstatus runmode "normal"\n'), self.__MatchRunMode, None)
        
    def __MatchRunMode(self, match, tag):

        self.RunModeDisabled = False

        self.Send('scpmode encoding ascii\n')

        self.Send('scpmode valuetype raw\n')

    def UpdateBeamDirectionPhiMeter(self, value, qualifier):

        BeamDirectionPhiMeterCmdString = 'mtrstart RM:BeamDirection 500\n'
        self.__UpdateHelper('BeamDirectionPhiMeter', BeamDirectionPhiMeterCmdString, value, qualifier)

    def __MatchBeamDirectionPhiMeter(self, match, tag):

        phi_value = (int(match.group(1).decode(), 16) * 2) - 180
        if -180 <= phi_value <= 180:
            self.WriteStatus('BeamDirectionPhiMeter', phi_value, None)
            
        theta_value = int(match.group(2).decode(), 16) / 2
        if 0 <= theta_value <= 90:
            self.WriteStatus('BeamDirectionThetaMeter', theta_value, None)

        ValueStateValues = {
            1: 'Active',
            0: 'Inactive'
        }

        value = ValueStateValues[int(match.group(3).decode())]
        self.WriteStatus('VoiceDetectionStatus', value, None)

    def UpdateBeamDirectionThetaMeter(self, value, qualifier):

        self.UpdateBeamDirectionPhiMeter(None, qualifier)

    def UpdateVoiceDetectionStatus(self, value, qualifier):

        self.UpdateBeamDirectionPhiMeter(None, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'devstatus error\n'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            'none':    'Normal',
            'error':   'Error',
            'fault':   'Fault',
            'warning': 'Warning'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetNearEndOutputFaderLevel(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1',
            }

        ValueConstraints = {
            'Min': -138.05,
            'Max': 10,
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in ChannelStates:
            temp_value1 = -327.68 if value == -138.05 else value
            if -138.00 <= temp_value1 <= -20.00:
                temp_value = int(round(temp_value1, 1) * 100)
            else:
                temp_value = int(round(temp_value1, 2) * 100)
            NearEndOutputFaderLevelCmdString = 'set RM:NeOut_Fader/Ch/Level {} 0 {}\n'.format(
                                                  ChannelStates[channel_val], temp_value)  
            self.__SetHelper('NearEndOutputFaderLevel', NearEndOutputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNearEndOutputFaderLevel')

    def UpdateNearEndOutputFaderLevel(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1',
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            NearEndOutputFaderLevelCmdString = 'get RM:NeOut_Fader/Ch/Level {} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('NearEndOutputFaderLevel', NearEndOutputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateNearEndOutputFaderLevel')

    def __MatchNearEndOutputFaderLevel(self, match, tag):

        ChannelStates = {
            '0': '1',
            '1': '2',
            }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        if int(match.group(2).decode()) == -32768:
            value = -138.05
        else: 
            value = int(match.group(2).decode()) / 100
        if -138.05 <= value <= 10:
            self.WriteStatus('NearEndOutputFaderLevel', value, qualifier)

    def SetNearEndOutputMute(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1'
            }

        ValueStateValues = {
            'On': '0',
            'Off': '1'
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and value in ValueStateValues:
            NearEndOutputMuteCmdString = 'set RM:NeOut_Mute/Ch/On {} 0 {}\n'.format(
                                                  ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('NearEndOutputMute', NearEndOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNearEndOutputMute')

    def UpdateNearEndOutputMute(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1'
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            NearEndOutputMuteCmdString = 'get RM:NeOut_Mute/Ch/On {} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('NearEndOutputMute', NearEndOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateNearEndOutputMute')

    def __MatchNearEndOutputMute(self, match, tag):

        ChannelStates = {
            '0': '1',
            '1': '2'
            }

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
            }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('NearEndOutputMute', value, qualifier)

    def SetLEDBrightness(self, value, qualifier):

        ValueStateValues = {
            'High': '0',
            'Medium': '1',
            'Low': '2',
            'Off': '3'
            }

        if value in ValueStateValues:
            LEDBrightnessCmdString = 'set RM:Led/Brightness 0 0 {}\n'.format(ValueStateValues[value])
            self.__SetHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDBrightness')

    def UpdateLEDBrightness(self, value, qualifier):

        LEDBrightnessCmdString = 'get RM:Led/Brightness 0 0\n'
        self.__UpdateHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)

    def __MatchLEDBrightness(self, match, tag):

        ValueStateValues = {
            '0': 'High',
            '1': 'Medium',
            '2': 'Low',
            '3': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LEDBrightness', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.RunModeDisabled:
            self.Send('devstatus runmode\n')

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.RunModeDisabled:
                self.Send('devstatus runmode\n')

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

        self.RunModeDisabled = True

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