from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, findall, search

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
            'ExecutiveMode': { 'Status': {}},
            'FIXEDOutputMute': {'Parameters':['Output'], 'Status': {}},
            'GroupLineInputGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMicInputGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMixpointGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMute': {'Parameters':['Group'], 'Status': {}},
            'GroupFIXEDOutputGain': {'Parameters':['Group'], 'Status': {}},
            'GroupVARIABLEOutputAttenuation': {'Parameters':['Group'], 'Status': {}},
            'LineInputGain': {'Parameters':['Input'], 'Status': {}},
            'MicInputGain': {'Parameters':['Input'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'MixpointGain': {'Parameters':['Input','Output'], 'Status': {}},
            'MixpointMute': {'Parameters':['Input','Output'], 'Status': {}},
            'FIXEDOutputGain': {'Parameters': ['Output'], 'Status': {}},
            'VARIABLEOutputAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'VARIABLEOutputMute': {'Parameters':['Output'], 'Status': {}},
            'VariableOutputVolume': { 'Status': {}},
        }

        self.GroupFunction = {}  # This is to maintain a global dictionary of groups and their assigned functions

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'GrpmD([0-9]{1,2})\*([0-9+-]{1,5})\r\n'), self.__MatchGroup, None)
            self.AddMatchString(compile(b'DsG(4000[0-3])\*([0-9+-]{1,5})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'DsM(4000[0-3])\*(0|1)\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'DsG2([0-3]{2})([0-1]{2})\*([0-9+-]{1,5})\r\n'), self.__MatchMixpointGain, None)
            self.AddMatchString(compile(b'DsM2([0-3]{2})([0-1]{2})\*(0|1)\r\n'), self.__MatchMixpointMute, None)
            self.AddMatchString(compile(b'DsM(6000[0-1])\*(0|1)\r\n'), self.__MatchVARIABLEOutputMute, None)
            self.AddMatchString(compile(b'DsM(6010[2-3])\*(0|1)\r\n'), self.__MatchFIXEDOutputMute, None)
            self.AddMatchString(compile(b'DsG(6000[0-1])\*([0-9+-]{1,5})\r\n'), self.__MatchVARIABLEOutputAttenuation, None)
            self.AddMatchString(compile(b'DsG(6010[2-3])\*([0-9+-]{1,5})\r\n'), self.__MatchFIXEDOutputGain, None)
            self.AddMatchString(compile(b'V([0-9]{1,3})\r\n'), self.__MatchVariableOutputVolume, None)
            self.AddMatchString(compile(b'E([0-9]{2})\r\n'), self.__MatchError, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeValues = {
            'Off' : '0', 
            'Mode 1' : '1', 
            'Mode 2' : '2', 
            }

        self.__SetHelper('ExecutiveMode','{0}X'.format(ExecutiveModeValues[value]), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier): 

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeStateNames = {
           '0' : 'Off', 
           '1' : 'Mode 1', 
           '2' : 'Mode 2', 
           }

        self.WriteStatus('ExecutiveMode', ExecutiveModeStateNames[match.group(1).decode()], None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False
    
    def SetGroupLineInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16 and -18 <= value <= 24:
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupLineInputGain'
            self.__SetHelper('GroupLineInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupLineInputGain')

    def UpdateGroupLineInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupLineInputGain'
            self.__UpdateHelper('GroupLineInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupLineInputGain')

    def SetGroupMicInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16 and -18 <= value <= 60:
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupMicInputGain'
            self.__SetHelper('GroupMicInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMicInputGain')

    def UpdateGroupMicInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupMicInputGain'
            self.__UpdateHelper('GroupMicInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMicInputGain')

    def SetGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16 and -100 <= value <= 12:
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__SetHelper('GroupMixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMixpointGain')

    def UpdateGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__UpdateHelper('GroupMixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMixpointGain')

    def SetGroupMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}*{1}grpm\r\n'.format(group, ValueStateValues[value])
            self.GroupFunction[group] = 'GroupMute'
            self.__SetHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupMute'
            self.__UpdateHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupVARIABLEOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16 and -100 <= value <= 0:
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupVARIABLEOutputAttenuation'
            self.__SetHelper('GroupVARIABLEOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupVARIABLEOutputAttenuation')

    def UpdateGroupVARIABLEOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupVARIABLEOutputAttenuation'
            self.__UpdateHelper('GroupVARIABLEOutputAttenuation', commandString, value, qualifier)

    def SetGroupFIXEDOutputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16 and -24 <= value <= 12:
            level = round(value * 10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupFIXEDOutputGain'
            self.__SetHelper('GroupFIXEDOutputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupFIXEDOutputGain')

    def UpdateGroupFIXEDOutputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 16:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupFIXEDOutputGain'
            self.__UpdateHelper('GroupFIXEDOutputGain', commandString, value, qualifier)

    def __MatchGroup(self, match, tag):

        group = str(int(match.group(1)))
        if group in self.GroupFunction:
            command = self.GroupFunction[group]
            if command == 'GroupMute':
                GroupMuteStateNames = {
                    '1': 'On',
                    '0': 'Off'
                }
                qualifier = {'Group': group}
                value = match.group(2).decode()[-1]
                self.WriteStatus(command, GroupMuteStateNames[value], qualifier)
            elif command in ['GroupLineInputGain', 'GroupMicInputGain', 'GroupVARIABLEOutputAttenuation', 
                             'GroupMixpointGain', 'GroupFIXEDOutputGain'
                             ]:
                qualifier = {'Group': group}
                value = int(match.group(2)) / 10
                self.WriteStatus(command, value, qualifier)

    def SetLineInputGain(self, value, qualifier):

        channel = {
            'Left': '40002',
            'Right': '40003'
        }

        if qualifier['Input'] in ['Left', 'Right'] and -18 <= value <= 24:
            value = round(value, 1)
            level = int(value * 10)
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel[qualifier['Input']], level)
            self.__SetHelper('LineInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInputGain')

    def UpdateLineInputGain(self, value, qualifier):

        channel = {
            'Left': '40002',
            'Right': '40003'
        }
        if qualifier['Input'] in ['Left', 'Right']:
            commandString = 'wG{0}AU\r\n'.format(channel[qualifier['Input']])
            self.__UpdateHelper('LineInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLineInputGain')

    def SetMicInputGain(self, value, qualifier):

        if qualifier['Input'] in ['1', '2'] and -18 <= value <= 60:
            value = round(value, 10)
            level = int(value * 10)
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(int(qualifier['Input']) + 39999, level)
            self.__SetHelper('MicInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicInputGain')

    def UpdateMicInputGain(self, value, qualifier):

        if qualifier['Input'] in ['1', '2']:
            commandString = 'wG{0}AU\r\n'.format(int(qualifier['Input']) + 39999)
            self.__UpdateHelper('MicInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicInputGain')

    def __MatchInputGain(self, match, tag):

        channel = str(int(match.group(1)) - 39999)
        channels = {
                '1': '1',
                '2': '2',
                '3': 'Left',
                '4': 'Right'
            }
        qualifier = {'Input': channels[channel]}
        value = int(match.group(2)) / 10
        if channel in ['1', '2']:
            self.WriteStatus('MicInputGain', value, qualifier)
        elif channel in ['3', '4']:
            self.WriteStatus('LineInputGain', value, qualifier)
    
    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }
        
        channels = {
            'Mic 1': 1,
            'Mic 2': 2,
            'Line Left': 3,
            'Line Right': 4
        }

        if qualifier['Input'] in ['Mic 1', 'Mic 2', 'Line Left', 'Line Right']:
            commandString = 'wM{0}*{1}AU\r\n'.format(channels[qualifier['Input']] + 39999, ValueStateValues[value])
            self.__SetHelper('InputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        channels = {
            'Mic 1': 1,
            'Mic 2': 2,
            'Line Left': 3,
            'Line Right': 4
        }
        if qualifier['Input'] in ['Mic 1', 'Mic 2', 'Line Left', 'Line Right']:
            commandString = 'wM{0}AU\r\n'.format(int(channels[qualifier['Input']]) + 39999)
            self.__UpdateHelper('InputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        
        channels = {
            '1': 'Mic 1',
            '2': 'Mic 2',
            '3': 'Line Left',
            '4': 'Line Right'
        }

        channel = str(int(match.group(1)) - 39999)
        qualifier = {'Input': channels[channel]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetMixpointGain(self, value, qualifier):

        MixpointGainInputStateValues = {
            'Mic 1': '00', 'Mic 2': '01', 'Line Left': '02', 'Line Right': '03',
        }

        MixpointOutputStateValues = {
            'Left': '00', 'Right': '01',
        }

        Input, Output = qualifier['Input'], qualifier['Output']
        if -100 <= value <= 12:
            inputValue = MixpointGainInputStateValues[Input]
            outputValue = MixpointOutputStateValues[Output]
            level = round(value * 10)
            commandString = 'wG2{0}{1}*{2:05d}AU\r\n'.format(inputValue, outputValue, level)
            self.__SetHelper('MixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointGain')

    def UpdateMixpointGain(self, value, qualifier):

        MixpointGainInputStateValues = {
            'Mic 1': '00', 'Mic 2': '01', 'Line Left': '02', 'Line Right': '03',
        }

        MixpointOutputStateValues = {
            'Left': '00', 'Right': '01',
        }

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = MixpointGainInputStateValues[Input]
        outputValue = MixpointOutputStateValues[Output]
        commandString = 'wG2{0}{1}AU\r\n'.format(inputValue, outputValue)
        self.__UpdateHelper('MixpointGain', commandString, value, qualifier)

    def __MatchMixpointGain(self, match, tag):

        MixpointGainInputStateNames = {
            '00': 'Mic 1', '01': 'Mic 2', '02': 'Line Left', '03': 'Line Right',
        }

        MixpointOutputStateNames = {
            '00': 'Left', '01': 'Right',
        }

        if 0 <= int(match.group(1).decode()) <= 36:
            Input = MixpointGainInputStateNames[match.group(1).decode()]
            Output = MixpointOutputStateNames[match.group(2).decode()]
            value = (int(match.group(3))) / 10
            qualifier = {'Input': Input, 'Output': Output}
            self.WriteStatus('MixpointGain', value, qualifier)

    def SetMixpointMute(self, value, qualifier):

        MixpointInputStateValues = {
            'Mic 1': '00', 'Mic 2': '01', 'Line Left': '02', 'Line Right': '03',
        }

        MixpointOutputStateValues = {
            'Left': '00', 'Right': '01',
        }

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = MixpointInputStateValues[Input]
        outputValue = MixpointOutputStateValues[Output]
        commandString = 'wM2{0}{1}*{2}AU\r\n'.format(inputValue, outputValue, ValueStateValues[value])
        self.__SetHelper('MixpointMute', commandString, value, qualifier)

    def UpdateMixpointMute(self, value, qualifier):

        MixpointInputStateValues = {
            'Mic 1': '00', 'Mic 2': '01', 'Line Left': '02', 'Line Right': '03',
        }

        MixpointOutputStateValues = {
            'Left': '00', 'Right': '01',
        }

        Input, Output = qualifier['Input'], qualifier['Output']
        inputValue = MixpointInputStateValues[Input]
        outputValue = MixpointOutputStateValues[Output]
        commandString = 'wM2{0}{1}AU\r\n'.format(inputValue, outputValue)
        self.__UpdateHelper('MixpointMute', commandString, value, qualifier)

    def __MatchMixpointMute(self, match, tag):

        MixpointInputStateNames = {
            '00': 'Mic 1', '01': 'Mic 2', '02': 'Line Left', '03': 'Line Right',
        }

        MixpointOutputStateNames = {
            '00': 'Left', '01': 'Right',
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if 0 <= int(match.group(1).decode()) <= 36:
            Input = MixpointInputStateNames[match.group(1).decode()]
            Output = MixpointOutputStateNames[match.group(2).decode()]
            value = ValueStateValues[match.group(3).decode()]
            qualifier = {'Input': Input, 'Output': Output}
            self.WriteStatus('MixpointMute', value, qualifier)

    def SetVARIABLEOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        channel = {
            'Left': 60000,
            'Right': 60001,       
            }
        if qualifier['Output'] in ['Left', 'Right']:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('VARIABLEOutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVARIABLEOutputMute')

    def UpdateVARIABLEOutputMute(self, value, qualifier):

        channel = {
            'Left': 60000,
            'Right': 60001,       
            }
        if qualifier['Output'] in ['Left', 'Right']:
            commandString = 'wM{0}AU\r\n'.format(channel[qualifier['Output']])
            self.__UpdateHelper('VARIABLEOutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVARIABLEOutputMute')

    def __MatchVARIABLEOutputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        channel = str(int(match.group(1)) - 59999)
        channels = {
            '1' : 'Left',
            '2': 'Right'
        }
        qualifier = {'Output': channels[channel]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VARIABLEOutputMute', value, qualifier)

    def SetFIXEDOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
        }

        channel = {
            'Left': 60102,
            'Right': 60103,       
            }
        if qualifier['Output'] in ['Left', 'Right']:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('FIXEDOutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFIXEDOutputMute')

    def UpdateFIXEDOutputMute(self, value, qualifier):

        channel = {
            'Left': 60102,
            'Right': 60103,       
            }
        if qualifier['Output'] in ['Left', 'Right']:
            commandString = 'wM{0}AU\r\n'.format(channel[qualifier['Output']])
            self.__UpdateHelper('FIXEDOutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFIXEDOutputMute')

    def __MatchFIXEDOutputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        channel = str(int(match.group(1)) - 60101)
        channels = {
            '1' : 'Left',
            '2': 'Right'
        }
        qualifier = {'Output': channels[channel]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FIXEDOutputMute', value, qualifier)

    def SetVARIABLEOutputAttenuation(self, value, qualifier):

        channel = {
            'Left': 60000,
            'Right': 60001,       
            }
        if qualifier['Output'] in ['Left', 'Right'] and -100 <= value <= 0:
            level = round(value * 10)
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel[qualifier['Output']], level)
            self.__SetHelper('VARIABLEOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVARIABLEOutputAttenuation')

    def UpdateVARIABLEOutputAttenuation(self, value, qualifier):

        channel = {
            'Left': 60000,
            'Right': 60001,       
            }
        if qualifier['Output'] in ['Left', 'Right']:
            commandString = 'wG{0}AU\r\n'.format(channel[qualifier['Output']])
            self.__UpdateHelper('VARIABLEOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVARIABLEOutputAttenuation')

    def __MatchVARIABLEOutputAttenuation(self, match, tag):

        channel = str(int(match.group(1)) - 59999)
        channels = {
            '1': 'Left',
            '2': 'Right',       
            }
        qualifier = {'Output': channels[channel]}
        value = (int(match.group(2))) / 10
        self.WriteStatus('VARIABLEOutputAttenuation', value, qualifier)

    def SetFIXEDOutputGain(self, value, qualifier):

        channel = {
            'Left': 60102,
            'Right': 60103,       
            }
        if qualifier['Output'] in ['Left', 'Right'] and -24 <= value <= 12:
            level = round(value * 10)
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel[qualifier['Output']], level)
            self.__SetHelper('FIXEDOutputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFIXEDOutputGain')

    def UpdateFIXEDOutputGain(self, value, qualifier):

        channel = {
            'Left': 60102,
            'Right': 60103,       
            }
        if qualifier['Output'] in ['Left', 'Right']:
            commandString = 'wG{0}AU\r\n'.format(channel[qualifier['Output']])
            self.__UpdateHelper('FIXEDOutputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFIXEDOutputGain')

    def __MatchFIXEDOutputGain(self, match, tag):

        channel = str(int(match.group(1)) - 60101)
        channels = {
            '1': 'Left',
            '2': 'Right',       
            }
        qualifier = {'Output': channels[channel]}
        value = (int(match.group(2))) / 10
        self.WriteStatus('FIXEDOutputGain', value, qualifier)

    def SetVariableOutputVolume(self, value, qualifier): 
  
        VariableOutputVolumeConstraints = {
            'Min' : 0,
            'Max' : 100,
            }    

        if VariableOutputVolumeConstraints['Min'] <= value <= VariableOutputVolumeConstraints['Max']:
            VariableOutputVolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('VariableOutputVolume', VariableOutputVolumeCmdString, value, qualifier) 
        else:   
            self.Discard('Invalid Command for SetVariableOutputVolume') 
           

    def UpdateVariableOutputVolume(self, value, qualifier):  

        VariableOutputVolumeCmdString = 'V'   
        self.__UpdateHelper('VariableOutputVolume', VariableOutputVolumeCmdString, value, qualifier)   

    def __MatchVariableOutputVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VariableOutputVolume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True        
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
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

            if self.VerboseDisabled:
                self.Send('w3cv\r\n')
                self.Send(commandstring)
            else:
                self.Send(commandstring)
    
    def __MatchError(self, match, tag):

        self.counter = 0

        DeviceErrorCodes = {
            '10': 'Invalid command',
            '11': 'Invalid preset',
            '12': 'Invalid port number',
            '13': 'Invalid parameter (number is out of range)',
            '14': 'Not valid for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System timed out',
            '22': 'Busy',
            '25': 'Device is not present'
        }

        if match.group(1).decode() in DeviceErrorCodes:
            self.Error([DeviceErrorCodes[match.group(1).decode()]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode()])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True

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
                result = search(regexString, self.__receiveBuffer)
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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