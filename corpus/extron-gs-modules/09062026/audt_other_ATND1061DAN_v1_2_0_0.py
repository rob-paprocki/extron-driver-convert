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
            'DeviceMute': { 'Status': {}},
            'InputMute': {'Parameters':['Channel'], 'Status': {}},
            'OutputLevel': {'Parameters':['Channel'], 'Status': {}},
            'OutputMute': {'Parameters':['Channel'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'g_mute 0000 \S{2} NC ([01]) \r'), self.__MatchDeviceMute, None)
            self.AddMatchString(re.compile(b'GICM 0000 \S{2} NC ([0-6]),([01]) \r'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'GOCL 0000 \S{2} NC ([01]),(\d+) \r'), self.__MatchOutputLevel, None)
            self.AddMatchString(re.compile(b'GOCM 0000 \S{2} NC ([01]),([01]) \r'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'NAK ([09][0-59]) \r'), self.__MatchError, None)

        self.faderTableSet = {
            -120: 1, -118: 2, -116: 3, -114: 4, -112: 5, -110: 6, -108: 7, -106: 8, -104: 9, -102: 10, -100: 11, -98: 13,
            -96: 15, -94: 17, -92: 19, -90: 21, -88: 23, -86: 25, -84: 27, -82: 29, -80: 31, -78: 35, -76: 38, -74: 43,
            -72: 47, -70: 51, -68: 55, -66: 59, -64: 63, -62: 67, -60: 71, -58: 75, -56: 79, -54: 83, -52: 87, -50: 91,
            -48: 95, -46: 99, -44: 103, -42: 107, -40: 111, -38: 121, -36: 131, -34: 141, -32: 151, -30: 161, -28: 171,
            -26: 181, -24: 191, -22: 201, -20: 211, -18: 231, -16: 251, -14: 271, -12: 291, -10: 311, -8: 331, -6: 351,
            -4: 371, -2: 391, 0: 411, 2: 431, 4: 451, 6: 471, 8: 491, 10: 511
        }

        self.faderTableMatch = {
            1: -120, 2: -118, 3: -116, 4: -114, 5: -112, 6: -110, 7: -108, 8: -106, 9: -104, 10: -102, 11: -100, 13: -98,
            15: -96, 141: -34, 17: -94, 19: -92, 21: -90, 23: -88, 25: -86, 411: 0, 231: -18, 29: -82, 31: -80, 161: -30,
            35: -78, 38: -76, 291: -12, 43: -74, 47: -72, 27: -84, 351: -6, 51: -70, 181: -26, 55: -68, 371: -4, 87: -52,
            59: -66, 151: -32, 63: -64, 311: -10, 67: -62, 71: -60, 201: -22, 75: -58, 79: -56, 271: -14, 83: -54, 471: 6,
            331: -8, 91: -50, 95: -48, 107: -42, 171: -28, 99: -46, 131: -36, 103: -44, 431: 2, 491: 8, 451: 4, 111: -40,
            211: -20, 391: -2, 251: -16, 121: -38, 191: -24, 511: 10
        }

    def SetDeviceMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            DeviceMuteCmdString = 's_mute S 0000 00 NC {} \r'.format(ValueStateValues[value])
            self.__SetHelper('DeviceMute', DeviceMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceMute')

    def UpdateDeviceMute(self, value, qualifier):

        DeviceMuteCmdString = 'g_mute O 0000 00 NC \r'
        self.__UpdateHelper('DeviceMute', DeviceMuteCmdString, value, qualifier)

    def __MatchDeviceMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceMute', value, None)

    def SetInputMute(self, value, qualifier):

        ChannelStates = {
            '1'      : '0',
            '2'      : '1',
            '3'      : '2',
            '4'      : '3',
            '5'      : '4',
            '6'      : '5',
            'Analog' : '6'
        }

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            InputMuteCmdString = 'SICM S 0000 00 NC {0},{1} \r'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        ChannelStates = {
            '1'      : '0',
            '2'      : '1',
            '3'      : '2',
            '4'      : '3',
            '5'      : '4',
            '6'      : '5',
            'Analog' : '6'
        }

        if qualifier['Channel'] in ChannelStates:
            InputMuteCmdString = 'GICM O 0000 00 NC {} \r'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ChannelStates = {
            '0' : '1',
            '1' : '2',
            '2' : '3',
            '3' : '4',
            '4' : '5',
            '5' : '6',
            '6' : 'Analog'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetOutputLevel(self, value, qualifier):

        ChannelStates = {
            'Analog Out' : '0',
            'Auto Mix'   : '1'
        }

        if qualifier['Channel'] in ChannelStates and value in self.faderTableSet:
            OutputLevelCmdString = 'SOCL S 0000 00 NC {0},{1} \r'.format(ChannelStates[qualifier['Channel']], self.faderTableSet[value])
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier) # Query delay not needed, based on testing v1_2_0
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        ChannelStates = {
            'Analog Out' : '0',
            'Auto Mix'   : '1'
        }

        if qualifier['Channel'] in ChannelStates:
            OutputLevelCmdString = 'GOCL O 0000 00 NC {} \r'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):

        ChannelStates = {
            '0' : 'Analog Out',
            '1' : 'Auto Mix'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = self.faderTableMatch[int(match.group(2))]
        if -120 <= value <= 10:
            self.WriteStatus('OutputLevel', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ChannelStates = {
            'Analog Out' : '0',
            'Auto Mix'   : '1'
        }

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            OutputMuteCmdString = 'SOCM S 0000 00 NC {0},{1} \r'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        ChannelStates = {
            'Analog Out' : '0',
            'Auto Mix'   : '1'
        }

        if qualifier['Channel'] in ChannelStates:
            OutputMuteCmdString = 'GOCM O 0000 00 NC {} \r'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ChannelStates = {
            '0' : 'Analog Out',
            '1' : 'Auto Mix'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetRecallCmdString = 'CALLP S 0000 00 NC {} \r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier) # Query delay not needed, based on testing v1_2_0
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetSaveCmdString = 'REGIP S 0000 00 NC {} \r'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier) # Query delay not needed, based on testing v1_2_0
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):
        self.counter = 0

        ERROR_CODES = {
            '01' : 'Syntax error',
            '02' : 'Invalid command',
            '03' : 'Splitting transmission error',
            '04' : 'Parameter error',
            '90' : 'Busy',
            '92' : 'Busy(Save mode)',
            '99' : 'Other errors'
        }

        error = match.group(1).decode()
        self.Error(['An error occurred. Error Code {0}: {1}.'.format(error, ERROR_CODES[error])])

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()