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
            'AmpOutputAttenuation': {'Parameters':['Output'], 'Status': {}},
            'ATOutputAttenuation': {'Parameters':['Output'], 'Status': {}},
            'DCProtectionFault': { 'Status': {}},
            'DigitalClip': {'Parameters':['Output'], 'Status': {}},
            'FanSpeed': {'Parameters':['L + R'], 'Status': {}},
            'FanStatus': {'Parameters':['L + R'], 'Status': {}},
            'GroupMicLineInputGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMixpointGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMute': {'Parameters':['Group'], 'Status': {}},
            'GroupOutputAttenuation': {'Parameters':['Group'], 'Status': {}},
            'GroupPostMixerTrim': {'Parameters':['Group'], 'Status': {}},
            'GroupPreMixerGain': {'Parameters':['Group'], 'Status': {}},
            'InputGain': {'Parameters':['Input'], 'Status': {}},
            'LineOutputAttenuation': {'Parameters':['Output'], 'Status': {}},
            'LossofAC': { 'Status': {}},
            'MainPowerSupply': { 'Status': {}},
            'OverTempFault': { 'Status': {}},
            'OverloadProtect': {'Parameters':['Output'], 'Status': {}},
            'PoEStatus': { 'Status': {}},
            'PremixerGain': {'Parameters':['Input'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'SignalPresence': {'Parameters':['Output'], 'Status': {}},
            'Temperature': { 'Status': {}},
            'ThermalLimiting': {'Parameters':['Output'], 'Status': {}},
            'ATInputPremixerGain': {'Parameters':['Input'], 'Status': {}}
        }

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.SendNotify = True

        self.GroupFunction = {} #This is to maintain a global dictionary of groups and their assigned functions

        self.LevelTypes = {
            'GroupMicLineInputGain'     : {'Min' : -18,  'Max' : 24},
            'GroupMixpointGain'         : {'Min' : -100,  'Max' : 12},
            'GroupOutputAttenuation'    : {'Min' : -100, 'Max' : 0},
            'GroupPostMixerTrim'        : {'Min' : -12,  'Max' : 12},
            'GroupPreMixerGain'         : {'Min' : -100, 'Max' : 12},
            'InputGain'                 : {'Min' : -18,  'Max' : 24},
            'PremixerGain'              : {'Min' : -100, 'Max' : 12},
            'ATInputPremixerGain'         : {'Min' : -100, 'Max' : 12},
            'AmpOutputAttenuation'         : {'Min' : -100, 'Max' : 0},
            'ATOutputAttenuation'         : {'Min' : -100, 'Max' : 0},
            'LineOutputAttenuation'         : {'Min' : -100, 'Max' : 0}
        }

        self.OutputAttenuationStates = {
            '60000': 'Amp Output 1',
            '60001': 'Amp Output 2',
            '60002': 'Amp Output 3',
            '60003': 'Amp Output 4',
            '60008': 'Line Output 1',
            '60009': 'Line Output 2',
            '60010': 'Line Output 3',
            '60011': 'Line Output 4',
            '60016': 'AT Output 1',
            '60017': 'AT Output 2',
            '60018': 'AT Output 3',
            '60019': 'AT Output 4',
            '60020': 'AT Output 5',
            '60021': 'AT Output 6',
            '60022': 'AT Output 7',
            '60023': 'AT Output 8'
        }

        self.LineStates = {
            '1': '60008',
            '2': '60009',
            '3': '60010',
            '4': '60011'
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'32Stat ([0-2]{3})\*([0-4 *]{16})(\d{1,3}\.\d{1}C)\*(\d+)\*(\d+)\*([0-2 *]{4})([0-2])\*([01][0-2]{5}\S+)\r\n'), self.__MatchFaultStatus, None)
            self.AddMatchString(re.compile(b'(53|54|60|61|67|68)Stat ([0-4]|[0-9]{1,4}\*[0-9]{1,4})\r\n', re.I), self.__MatchSystemFault, None)
            self.AddMatchString(re.compile(b'(55|57|62|64)Stat ([0-2*]{3,8})\r\n', re.I), self.__MatchChannelFault, None)
            self.AddMatchString(re.compile(b'GrpmD([0-9]{1,2})\*([0-9 -]{1,5})\r\n'), self.__MatchGroup, None)
            self.AddMatchString(re.compile(b'DsG(40000|40001|40002|40003)\*([0-9 -]{1,5})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'DsG(40100|40101|40102|40103)\*([0-9 -]{1,5})\r\n'), self.__MatchPremixerGain, None)
            self.AddMatchString(re.compile(b'DsG(50100|50101|50102|50103|50104|50105|50106|50107)\*([0-9 -]{1,5})\r\n'), self.__MatchATInputPremixerGain, None)
            self.AddMatchString(re.compile(b'DsG(600\d{2})\*([0-9 -]{1,5})\r\n'), self.__MatchOutputAttenuation, None)
            self.AddMatchString(re.compile(b'PoecS(0|1)\r\n'), self.__MatchPoEStatus, None)
            self.AddMatchString(re.compile(b'28Stat (\d{1,3}\.\d{1})C\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'E([0-9]{2})\r\n'), self.__MatchErrors, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)
            self.AddMatchString(re.compile(b'NtfyM1111111111111\r\n'), self.__MatchNotify, None) # Notify for unsolicited status

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def __MatchNotify(self, match, qualifier):

        self.SendNotify = False

    def UpdateFaultStatus(self, value, qualifier):

        cmdString = '\x1b32Stat\r'
        self.Send(cmdString)
        if self.SendNotify:
            cmdString = '\x1bM1111111111111NTFY\r'
            self.Send(cmdString)

    def SetAmpOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= 4 and self.__CheckValidLevelValue('AmpOutputAttenuation', value):
            level = round(value*10)
            commandString = 'WG{0}*{1:05d}AU\r'.format(channel + 59999, level)
            self.__SetHelper('AmpOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmpOutputAttenuation')

    def UpdateAmpOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= 4:
            commandString = 'WG{0}AU\r'.format(channel + 59999)
            self.__UpdateHelper('AmpOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmpOutputAttenuation')

    def __MatchOutputAttenuation(self, match, tag):
        
        if 'Amp' in self.OutputAttenuationStates[match.group(1).decode()]:
            channel = str(int(match.group(1)) - 59999)
            qualifier = {'Output' : channel}
            value = int(match.group(2))/10
            self.WriteStatus('AmpOutputAttenuation', value, qualifier)
        elif 'Line' in self.OutputAttenuationStates[match.group(1).decode()]:
            channel = str(int(match.group(1)) - 60007)
            qualifier = {'Output' : channel}
            value = int(match.group(2))/10
            self.WriteStatus('LineOutputAttenuation', value, qualifier)
        elif 'AT' in self.OutputAttenuationStates[match.group(1).decode()]:
            channel = str(int(match.group(1)) - 60015)
            qualifier = {'Output' : channel}
            value = int(match.group(2))/10
            self.WriteStatus('ATOutputAttenuation', value, qualifier)

    def SetATOutputAttenuation(self, value, qualifier):
    
        channel = int(qualifier['Output'])
        if 1 <= channel <= 8 and self.__CheckValidLevelValue('ATOutputAttenuation', value):
            level = round(value*10)
            commandString = 'WG{0}*{1:05d}AU\r'.format(channel + 60015, level)
            self.__SetHelper('ATOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATOutputAttenuation')

    def UpdateATOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= 8:
            commandString = 'WG{0}AU\r'.format(channel + 60015)
            self.__UpdateHelper('ATOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATOutputAttenuation')

    def UpdateFanSpeed(self, value, qualifier):

        self.UpdateFaultStatus( None, None)
    
    def UpdateFanStatus(self, value, qualifier):

        self.UpdateFaultStatus( None, None)
    
    def UpdateOverTempFault(self, value, qualifier):

        self.UpdateFaultStatus( None, None)
        
    def UpdateDCProtectionFault(self, value, qualifier):

        self.UpdateFaultStatus( None, None)
        
    def UpdateLossofAC(self, value, qualifier):

        self.UpdateFaultStatus( None, None)
        
    def UpdateMainPowerSupply(self, value, qualifier):

        self.UpdateFaultStatus( None, None)
    
    def UpdateSignalPresence(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 4:
            self.UpdateFaultStatus( None, None)
        else:
            self.Discard('Invalid Command for UpdateSignalPresence')

    def UpdateOverloadProtect(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 4:
            self.UpdateFaultStatus( None, None)
        else:
            self.Discard('Invalid Command for UpdateOverloadProtect')
    
    def UpdateThermalLimiting(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 4:
            self.UpdateFaultStatus( None, None)
        else:
            self.Discard('Invalid Command for UpdateThermalLimiting')

    def UpdateDigitalClip(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 4:
            self.UpdateFaultStatus( None, None)
        else:
            self.Discard('Invalid Command for UpdateDigitalClip')
    
    def __MatchChannelFault(self, match, tag):
    
        faulttable = {
            '0': 'Never Faulted',
            '1': 'Not in Fault State but Has Faulted',
            '2': 'Fault'
        }

        signalpresence = {
            '0': 'No Signal',
            '1': 'Signal'
        }

        type = match.group(1).decode()
        flt = match.group(2).decode()
        fltsplit = flt.split('*')
        if type == '55':
            for index, value in enumerate(fltsplit):
                self.WriteStatus('ThermalLimiting', faulttable[value], {'Output': str(index + 1)})
        elif type == '57':
            for index, value in enumerate(fltsplit):
                self.WriteStatus('OverloadProtect', faulttable[value], {'Output': str(index + 1)})
        elif type == '62':
            for index, value in enumerate(fltsplit):
                self.WriteStatus('SignalPresence', signalpresence[value], {'Output': str(index + 1)})
        elif type == '64':
            for index, value in enumerate(fltsplit):
                self.WriteStatus('DigitalClip', faulttable[value], {'Output': str(index + 1)})

    def __MatchSystemFault(self, match, tag):

        faulttable = {
            '0': 'Never Faulted',
            '1': 'Not in Fault State but Has Faulted',
            '2': 'Fault'
        }

        powertable = {
            '0': 'Never Faulted',
            '1': 'Not in Fault State but Has Faulted',
            '2': 'Fault (SIS Triggered)',
            '3': 'Fault (Timer triggered)',
            '4': 'Fault (Contact closure triggered)',
        }

        type = match.group(1).decode()
        if type == '53':
            self.WriteStatus('OverTempFault', faulttable[match.group(2).decode()], None)
        elif type == '54':
            self.WriteStatus('DCProtectionFault', faulttable[match.group(2).decode()], None)
        elif type == '60':
            self.WriteStatus('LossofAC', faulttable[match.group(2).decode()], None)
        elif type == '61':
            self.WriteStatus('MainPowerSupply', powertable[match.group(2).decode()], None)
        elif type == '67':
            type = type.split('*')
            self.WriteStatus('FanSpeed', int(type[0]), {'L + R': 'Left'})
            self.WriteStatus('FanSpeed', int(type[1]), {'L + R': 'Right'})
        elif type == '68':
            type = type.split('*')
            self.WriteStatus('FanStatus', faulttable[type[0]], {'L + R': 'Left'})
            self.WriteStatus('FanStatus', faulttable[type[1]], {'L + R': 'Right'})


    def __MatchFaultStatus(self, match, tag):
    
        faulttable = {
            '0': 'Never Faulted',
            '1': 'Not in Fault State but Has Faulted',
            '2': 'Fault'
        }

        powertable = {
            '0': 'Never Faulted',
            '1': 'Not in Fault State but Has Faulted',
            '2': 'Fault (SIS Triggered)',
            '3': 'Fault (Timer triggered)',
            '4': 'Fault (Contact closure triggered)',
        }

        signalpresence = {
            '0': 'No Signal',
            '1': 'Signal'
        }

        poe_presence = {
            '1': 'Present',
            '0': 'Not Present'
            }

        value = match.group(1).decode()
        self.WriteStatus('OverTempFault', faulttable[value[0]], None)
        self.WriteStatus('DCProtectionFault', faulttable[value[1]], None)
        self.WriteStatus('LossofAC', faulttable[value[2]], None)

        values = match.group(2).decode()
        values = values.split('*')
        val = values.pop(-2)
        self.WriteStatus('MainPowerSupply', powertable[str(val)], None)

        temperature = match.group(3).decode()
        self.WriteStatus('Temperature', float(temperature.strip('C')), None)

        left_fan_speed = match.group(4).decode()
        right_fan_speed = match.group(5).decode()
        self.WriteStatus('FanSpeed', int(left_fan_speed), {'L + R': 'Left'})
        self.WriteStatus('FanSpeed', int(right_fan_speed), {'L + R': 'Right'})
        fan_status = match.group(6).decode()
        fan_status = fan_status.split('*')
        self.WriteStatus('FanStatus', faulttable[fan_status[0]], {'L + R': 'Left'})
        self.WriteStatus('FanStatus', faulttable[fan_status[1]], {'L + R': 'Right'})

        poe_status = match.group(7).decode()
        self.WriteStatus('PoEStatus', poe_presence[poe_status], None)

        amp_channels = match.group(8).decode()
        amp_channels = amp_channels.split('*')

        for index, items in enumerate(amp_channels):
            self.WriteStatus('SignalPresence', signalpresence[items[0]], {'Output': str(index + 1)})
            self.WriteStatus('OverloadProtect', faulttable[items[1]], {'Output': str(index + 1)})
            self.WriteStatus('ThermalLimiting', faulttable[items[2]], {'Output': str(index + 1)})
            self.WriteStatus('DigitalClip', faulttable[items[3]], {'Output': str(index + 1)})
    
    def SetGroupMicLineInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupMicLineInputGain', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r'.format(group, level)
            self.GroupFunction[group] = 'GroupMicLineInputGain'
            self.__SetHelper('GroupMicLineInputGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupMicLineInputGain')

    def UpdateGroupMicLineInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupMicLineInputGain'
            self.__UpdateHelper('GroupMicLineInputGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupMicLineInputGain')

    def SetGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupMixpointGain', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r'.format(group, level)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__SetHelper('GroupMixpointGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupMixpointGain')

    def UpdateGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__UpdateHelper('GroupMixpointGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupMixpointGain')

    def SetGroupMute(self, value, qualifier):

        GroupMuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }
        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}*{1}grpm\r'.format(group, GroupMuteStateValues[value])
            self.GroupFunction[group] = 'GroupMute'
            self.__SetHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupMute'
            self.__UpdateHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupOutputAttenuation', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r'.format(group, level)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
            self.__SetHelper('GroupOutputAttenuation', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupOutputAttenuation')

    def UpdateGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'Wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
            self.__UpdateHelper('GroupOutputAttenuation', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupOutputAttenuation')

    def SetGroupPostMixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupPostMixerTrim', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r'.format(group, level)
            self.GroupFunction[group] = 'GroupPostMixerTrim'
            self.__SetHelper('GroupPostMixerTrim', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupPostMixerTrim')

    def UpdateGroupPostMixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupPostMixerTrim'
            self.__UpdateHelper('GroupPostMixerTrim', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupPostMixerTrim')

    def SetGroupPreMixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and self.__CheckValidLevelValue('GroupPreMixerGain', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r'.format(group, level)
            self.GroupFunction[group] = 'GroupPreMixerGain'
            self.__SetHelper('GroupPreMixerGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupPreMixerGain')

    def UpdateGroupPreMixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupPreMixerGain'
            self.__UpdateHelper('GroupPreMixerGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupPreMixerGain')

    def __MatchGroup(self, match, tag):

        group = str(int(match.group(1)))
        if group in self.GroupFunction:
            command = self.GroupFunction[group]
            if command == 'GroupMute':
                GroupMuteStateNames = {
                        '1' : 'On',
                        '0' : 'Off'
                }
                qualifier = {'Group' : group}
                value = match.group(2).decode()[-1]
                self.WriteStatus(command, GroupMuteStateNames[value], qualifier)
            elif command in ['GroupPreMixerGain', 'GroupOutputAttenuation',
                             'GroupMixpointGain', 'GroupPostMixerTrim',
                             'GroupMicLineInputGain',
                             ]:
                qualifier = {'Group' : group}
                value = int(match.group(2))/10
                self.WriteStatus(command, value, qualifier)
                
    def SetInputGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4 and self.__CheckValidLevelValue('InputGain', value):
            level = round(value*10)
            commandString = 'WG{0}*{1:05d}AU\r'.format(channel + 39999, level)
            self.__SetHelper('InputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4:
            commandString = 'WG{0}AU\r'.format(channel + 39999)
            self.__UpdateHelper('InputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        channel = str(int(match.group(1)) - 39999)
        qualifier = {'Input' : channel}
        value = int(match.group(2))/10
        self.WriteStatus('InputGain', value, qualifier)

    def SetLineOutputAttenuation(self, value, qualifier):
    
        channel = int(qualifier['Output'])
        if 1 <= channel <= 4 and self.__CheckValidLevelValue('LineOutputAttenuation', value):
            level = round(value*10)
            commandString = 'WG{0}*{1:05d}AU\r'.format(self.LineStates[qualifier['Output']], level)
            self.__SetHelper('LineOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineOutputAttenuation')

    def UpdateLineOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= 4:
            commandString = 'WG{0}AU\r'.format(self.LineStates[qualifier['Output']])
            self.__UpdateHelper('LineOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLineOutputAttenuation')

    def UpdatePoEStatus(self, value, qualifier):

        PoEStatusCmdString = 'wSPOEC\r'
        self.__UpdateHelper('PoEStatus', PoEStatusCmdString, value, qualifier)

    def __MatchPoEStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Present',
            '0': 'Not Present'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PoEStatus', value, None)

    def SetPremixerGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4 and self.__CheckValidLevelValue('PremixerGain', value):
            level=round(value*10)
            commandString = '\x1bG{0}*{1:05d}AU\r'.format(channel + 40099, level)
            self.__SetHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPremixerGain')

    def UpdatePremixerGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 4:
            commandString = '\x1bG{0}AU\r'.format(channel + 40099)
            self.__UpdateHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerGain')

    def __MatchPremixerGain(self, match, tag):

        channel = str(int(match.group(1)) - 40099)
        qualifier = {'Input' : channel}
        value = int(match.group(2))/10
        self.WriteStatus('PremixerGain', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 0 < int(value) <= 32:
            commandString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    
    def UpdateTemperature(self, value, qualifier):

        cmdString = 'w28STAT\r'
        self.__UpdateHelper('Temperature', cmdString, None, None)

    def __MatchTemperature(self, match, tag):

        value = float(match.group(1).decode())
        self.WriteStatus('Temperature', value, None)

    def SetATInputPremixerGain(self, value, qualifier):

        channel = qualifier['Input']
        if 1 <= int(channel) <= 8 and self.__CheckValidLevelValue('ATInputPremixerGain', value):
            level=round(value*10)
            ChannelValue = int(channel) + 50099
            commandString = 'wG{0}*{1:05d}AU\r'.format(ChannelValue, level)
            self.__SetHelper('ATInputPremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATInputPremixerGain')

    def UpdateATInputPremixerGain(self, value, qualifier):

        channel = qualifier['Input']
        if 1 <= int(channel) <= 8:
            ChannelValue = int(channel) + 50099
            commandString = 'wG{0}AU\r'.format(ChannelValue)
            self.__UpdateHelper('ATInputPremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATInputPremixerGain')

    def __MatchATInputPremixerGain(self, match, tag):

        channel = int(match.group(1)) - 50099
        qualifier = {'Input' : str(channel)}
        value = int(match.group(2))/10
        self.WriteStatus('ATInputPremixerGain', value, qualifier)

    def __CheckValidLevelValue(self, command, value):

        return self.LevelTypes[command]['Min'] <= value <= self.LevelTypes[command]['Max']
    
    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n') 
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchErrors(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01' : 'Invalid Input Number',
            '06' : 'Invalid Channel Change',
            '10' : 'Invalid Command',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter',
            '14' : 'Not valid for this configuration',
            '17' : 'Invalid command for signal type',
            '18' : 'System/command timed out',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '27' : 'Invalid event number',
            '28' : 'Filename not found',
            '30' : 'Hardware Failure',
            '31' : 'Attempt to break Port pass-thur when not set',
            }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: '+ match.group(0).decode()]) 

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.SendNotify = True
        self.EchoDisabled = True
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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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