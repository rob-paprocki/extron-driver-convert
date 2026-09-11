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
        self.Models = {
            'PowerZone Connect 122': self.blza_31_6359_2,
            'PowerZone Connect 252': self.blza_31_6359_2,
            'PowerZone Connect 122D': self.blza_31_6359_2D,
            'PowerZone Connect 504': self.blza_31_6359_4,
            'PowerZone Connect 254': self.blza_31_6359_4,
            'PowerZone Connect 504D': self.blza_31_6359_4D,
            'PowerZone Connect 508': self.blza_31_6359_8,
            'PowerZone Connect 1008': self.blza_31_6359_8
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'OutputGain': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'OutputSource': {'Parameters': ['Output'], 'Status': {}},
            'OutputSourceChannel': {'Parameters':['Output'], 'Status': {}},
            'Power': { 'Status': {}},
            'ZoneGain': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneMute': {'Parameters': ['Zone'], 'Status': {}},
            'ZonePrimarySource': {'Parameters':['Zone'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\+IN-10([0-7])\.GAIN (-?\d+\.\d+)\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'\+OUT(?:PUT)?-([1-8])\.GAIN (-?\d+\.\d+)\n'), self.__MatchOutputGain, None)
            self.AddMatchString(re.compile(b'\+OUT(?:PUT)?-([1-8])\.MUTE ([01])\n'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'\+OUT(?:PUT)?-([1-8])\.SRC "([A-H])"\n'), self.__MatchOutputSource, None)
            self.AddMatchString(re.compile(b'\+OUT(?:PUT)?-([1-8])\.SRC_CHANNEL "(L|R|S)"\n'), self.__MatchOutputSourceChannel, None)
            self.AddMatchString(re.compile(b'\+SYSTEM\.STATUS\.STATE "(INIT|STANDBY|ON|FAULT)"\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\+ZONE-([A-H])\.GAIN (-?\d+\.\d+)\n'), self.__MatchZoneGain, None)
            self.AddMatchString(re.compile(b'\+ZONE-([A-H])\.MUTE ([01])\n'), self.__MatchZoneMute, None)
            self.AddMatchString(re.compile(b'\+ZONE-([A-H])\.PRIMARY_SRC (\d+)\n'), self.__MatchZonePrimarySource, None)

    def SetInputGain(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= self.InputMax and -15 <= value <= 15:
            InputGainCmdString = 'SET IN-10{}.GAIN {:.1f}\n'.format(input_ - 1, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= self.InputMax:
            InputGainCmdString = 'GET IN-10{}.GAIN\n'.format(input_ - 1)
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        qualifier = {
            'Input': str(int(match.group(1).decode()) + 1)
        }

        value = float(match.group(2).decode())

        if -15 <= value <= 15:
            self.WriteStatus('InputGain', value, qualifier)

    def SetOutputGain(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= self.OutputMax and -30 <= value <= 15:
            OutputGainCmdString = 'SET OUT-{}.GAIN {:.1f}\n'.format(output, value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= self.OutputMax:
            OutputGainCmdString = 'GET OUT-{}.GAIN\n'.format(output)
            self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        qualifier = {
            'Output': match.group(1).decode()
        }

        value = float(match.group(2).decode())

        if -30 <= value <= 15:
            self.WriteStatus('OutputGain', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        output = int(qualifier['Output'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= output <= self.OutputMax and value in ValueStateValues:
            OutputMuteCmdString = 'SET OUT-{}.MUTE {}\n'.format(output, ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= self.OutputMax:
            OutputMuteCmdString = 'GET OUT-{}.MUTE\n'.format(output)
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Output': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetOutputSource(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= self.OutputMax and value in self.ZoneStates:
            OutputSourceCmdString = 'SET OUT-{}.SRC {}\n'.format(output, value)
            self.__SetHelper('OutputSource', OutputSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputSource')

    def UpdateOutputSource(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= self.OutputMax:
            OutputSourceCmdString = 'GET OUT-{}.SRC\n'.format(output)
            self.__UpdateHelper('OutputSource', OutputSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputSource')

    def __MatchOutputSource(self, match, tag):

        qualifier = {
            'Output': match.group(1).decode()
        }

        value = match.group(2).decode()
        self.WriteStatus('OutputSource', value, qualifier)

    def SetOutputSourceChannel(self, value, qualifier):

        output = int(qualifier['Output'])

        ValueStateValues = {
            'Left': 'L',
            'Right': 'R',
            'Sum': 'S'
            }

        if 1 <= output <= self.OutputMax and value in ValueStateValues:
            OutputSourceChannelCmdString = 'SET OUT-{}.SRC_CHANNEL {}\n'.format(output, ValueStateValues[value])
            self.__SetHelper('OutputSourceChannel', OutputSourceChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputSourceChannel')

    def UpdateOutputSourceChannel(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= self.OutputMax:
            OutputSourceChannelCmdString = 'GET OUT-{}.SRC_CHANNEL\n'.format(output)
            self.__UpdateHelper('OutputSourceChannel', OutputSourceChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputSourceChannel')

    def __MatchOutputSourceChannel(self, match, tag):

        ValueStateValues = {
            'L': 'Left',
            'R': 'Right',
            'S': 'Sum'
            }

        qualifier = {
            'Output': match.group(1).decode()
        }
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputSourceChannel', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            PowerCmdString = 'POWER_{}\n'.format(value.upper())
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'GET SYSTEM.STATUS.STATE\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        value = match.group(1).decode().title()
        if value == 'Standby':
            value = 'Off'

        self.WriteStatus('Power', value, None)

    def SetZoneGain(self, value, qualifier):

        zone = qualifier['Zone']

        if zone in self.ZoneStates and -80 <= value <= 0:
            ZoneGainCmdString = 'SET ZONE-{}.GAIN {:.1f}\n'.format(zone, value)
            self.__SetHelper('ZoneGain', ZoneGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneGain')

    def UpdateZoneGain(self, value, qualifier):

        zone = qualifier['Zone']

        if zone in self.ZoneStates:
            ZoneGainCmdString = 'GET ZONE-{}.GAIN\n'.format(zone)
            self.__UpdateHelper('ZoneGain', ZoneGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneGain')

    def __MatchZoneGain(self, match, tag):

        qualifier = {
            'Zone': match.group(1).decode()
        }

        value = float(match.group(2).decode())

        if -80 <= value <= 0:
            self.WriteStatus('ZoneGain', value, qualifier)

    def SetZoneMute(self, value, qualifier):

        zone = qualifier['Zone']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if zone in self.ZoneStates and value in ValueStateValues:
            ZoneMuteCmdString = 'SET ZONE-{}.MUTE {}\n'.format(zone, ValueStateValues[value])
            self.__SetHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneMute')

    def UpdateZoneMute(self, value, qualifier):

        zone = qualifier['Zone']

        if zone in self.ZoneStates:
            ZoneMuteCmdString = 'GET ZONE-{}.MUTE\n'.format(zone)
            self.__UpdateHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneMute')

    def __MatchZoneMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Zone': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ZoneMute', value, qualifier)

    def SetZonePrimarySource(self, value, qualifier):

        zone = qualifier['Zone']

        if zone in self.ZoneStates and value in self.InputSources:
            ZonePrimarySourceCmdString = 'SET ZONE-{}.PRIMARY_SRC {}\n'.format(zone, self.InputSources[value])
            self.__SetHelper('ZonePrimarySource', ZonePrimarySourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZonePrimarySource')

    def UpdateZonePrimarySource(self, value, qualifier):

        zone = qualifier['Zone']

        if zone in self.ZoneStates:
            ZonePrimarySourceCmdString = 'GET ZONE-{}.PRIMARY_SRC\n'.format(zone)
            self.__UpdateHelper('ZonePrimarySource', ZonePrimarySourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZonePrimarySource')

    def __MatchZonePrimarySource(self, match, tag):

        qualifier = {
            'Zone': match.group(1).decode()
        }
        value = self.MatchInputSources[match.group(2).decode()]
        self.WriteStatus('ZonePrimarySource', value, qualifier)

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

    def blza_31_6359_2(self):

        self.InputMax = 4
        self.OutputMax = 2
        self.ZoneStates = ('A', 'B')
        self.InputSources = {
            'Unused Input': '0',
            'Analog Input 1': '100',
            'Analog Input 2': '101',
            'Analog Input 3': '102', 
            'Analog Input 4': '103', 
            'SPDIF 1 (Left)': '200', 
            'SPDIF 2 (Right)': '201', 
            'Noise Generator': '400', 
            'Mix 1': '500', 
            'Mix 2': '501',
            }
        self.MatchInputSources = {
            '0': 'Unused Input',
            '100': 'Analog Input 1',
            '101': 'Analog Input 2',
            '102': 'Analog Input 3',
            '103': 'Analog Input 4', 
            '200': 'SPDIF 1 (Left)',
            '201': 'SPDIF 2 (Right)',
            '400': 'Noise Generator',
            '500': 'Mix 1',
            '501': 'Mix 2',
            }

    def blza_31_6359_2D(self):

        self.InputMax = 4
        self.OutputMax = 2
        self.ZoneStates = ('A', 'B')
        self.InputSources = {
            'Unused Input': '0',
            'Analog Input 1': '100',
            'Analog Input 2': '101',
            'Analog Input 3': '102', 
            'Analog Input 4': '103', 
            'SPDIF 1 (Left)': '200', 
            'SPDIF 2 (Right)': '201', 
            'Dante 1': '300', 
            'Dante 2': '301',
            'Dante 3': '302', 
            'Dante 4': '303', 
            'Noise Generator': '400', 
            'Mix 1': '500', 
            'Mix 2': '501',
            }
        self.MatchInputSources = {
            '0': 'Unused Input',
            '100': 'Analog Input 1',
            '101': 'Analog Input 2',
            '102': 'Analog Input 3',
            '103': 'Analog Input 4', 
            '200': 'SPDIF 1 (Left)',
            '201': 'SPDIF 2 (Right)',
            '300': 'Dante 1',
            '301': 'Dante 2',
            '302': 'Dante 3',
            '303': 'Dante 4',
            '400': 'Noise Generator',
            '500': 'Mix 1',
            '501': 'Mix 2',
            }


    def blza_31_6359_4(self):

        self.InputMax = 4
        self.OutputMax = 4
        self.ZoneStates = ('A', 'B', 'C', 'D')
        self.InputSources = {
            'Unused Input': '0',
            'Analog Input 1': '100',
            'Analog Input 2': '101',
            'Analog Input 3': '102', 
            'Analog Input 4': '103', 
            'SPDIF 1 (Left)': '200', 
            'SPDIF 2 (Right)': '201', 
            'Noise Generator': '400', 
            'Mix 1': '500', 
            'Mix 2': '501',
            'Mix 3': '502', 
            'Mix 4': '503'
            }
        self.MatchInputSources = {
            '0': 'Unused Input',
            '100': 'Analog Input 1',
            '101': 'Analog Input 2',
            '102': 'Analog Input 3',
            '103': 'Analog Input 4', 
            '200': 'SPDIF 1 (Left)',
            '201': 'SPDIF 2 (Right)',
            '400': 'Noise Generator',
            '500': 'Mix 1',
            '501': 'Mix 2',
            '502': 'Mix 3',
            '503': 'Mix 4'
            }

    def blza_31_6359_4D(self):

        self.InputMax = 4
        self.OutputMax = 4
        self.ZoneStates = ('A', 'B', 'C', 'D')
        self.InputSources = {
            'Unused Input': '0',
            'Analog Input 1': '100',
            'Analog Input 2': '101',
            'Analog Input 3': '102', 
            'Analog Input 4': '103', 
            'SPDIF 1 (Left)': '200', 
            'SPDIF 2 (Right)': '201', 
            'Dante 1': '300', 
            'Dante 2': '301',
            'Dante 3': '302', 
            'Dante 4': '303', 
            'Noise Generator': '400', 
            'Mix 1': '500', 
            'Mix 2': '501',
            'Mix 3': '502', 
            'Mix 4': '503'
            }
        
        self.MatchInputSources = {
            '0': 'Unused Input',
            '100': 'Analog Input 1',
            '101': 'Analog Input 2',
            '102': 'Analog Input 3',
            '103': 'Analog Input 4', 
            '200': 'SPDIF 1 (Left)',
            '201': 'SPDIF 2 (Right)',
            '300': 'Dante 1',
            '301': 'Dante 2',
            '302': 'Dante 3',
            '303': 'Dante 4',
            '400': 'Noise Generator',
            '500': 'Mix 1',
            '501': 'Mix 2',
            '502': 'Mix 3',
            '503': 'Mix 4'
            }

    def blza_31_6359_8(self):

        self.InputMax = 8
        self.OutputMax = 8
        self.ZoneStates = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
        self.InputSources = {
            'Unused Input': '0',
            'Analog Input 1': '100',
            'Analog Input 2': '101',
            'Analog Input 3': '102', 
            'Analog Input 4': '103',
            'Analog Input 5': '104',
            'Analog Input 6': '105',
            'Analog Input 7': '106', 
            'Analog Input 8': '107', 
            'SPDIF 1 (Left)': '200', 
            'SPDIF 2 (Right)': '201', 
            'Noise Generator': '400', 
            'Mix 1': '500', 
            'Mix 2': '501',
            'Mix 3': '502', 
            'Mix 4': '503',
            'Mix 5': '504', 
            'Mix 6': '505',
            'Mix 7': '506', 
            'Mix 8': '507',
            }
        self.MatchInputSources = {
            '0': 'Unused Input',
            '100': 'Analog Input 1',
            '101': 'Analog Input 2',
            '102': 'Analog Input 3',
            '103': 'Analog Input 4',
            '104': 'Analog Input 5',
            '105': 'Analog Input 6',
            '106': 'Analog Input 7',
            '107': 'Analog Input 8',
            '200': 'SPDIF 1 (Left)',
            '201': 'SPDIF 2 (Right)',
            '400': 'Noise Generator',
            '500': 'Mix 1',
            '501': 'Mix 2',
            '502': 'Mix 3',
            '503': 'Mix 4',
            '504': 'Mix 5',
            '505': 'Mix 6',
            '506': 'Mix 7',
            '507': 'Mix 8'
            }

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