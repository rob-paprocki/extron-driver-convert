from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
                'SPN 812':  self.lect_812, 
                'SPN 1612': self.lect_1612, 
                'SPN 1624': self.lect_1624, 
                'SPN 2412': self.lect_2412,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CrosspointGain': {'Parameters':['Input','Mix Bus'], 'Status': {}},
            'CrosspointMode': {'Parameters':['Input','Mix Bus'], 'Status': {}},
            'CrosspointMute': {'Parameters':['Input','Mix Bus'], 'Status': {}},
            'DeviceMode': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'FanStatus': { 'Status': {}},
            'FinalMixLevel': {'Parameters':['Mix Bus'], 'Status': {}},
            'HeadphoneMonitorSource': { 'Status': {}},
            'InputActivity': {'Parameters':['Input'], 'Status': {}},
            'InputCompressorMakeupGain': {'Parameters':['Input'], 'Status': {}},
            'InputCompressorRatio': {'Parameters':['Input'], 'Status': {}},
            'InputCompressorThresholdLevel': {'Parameters':['Input'], 'Status': {}},
            'InputCompressorTimeConstant': {'Parameters':['Input'], 'Status': {}},
            'InputGain': {'Parameters':['Input'], 'Status': {}},
            'InputGroupMute': {'Parameters':['Group'], 'Status': {}},
            'InputGroupLabelCommand': {'Parameters':['Group'], 'Status': {}},
            'InputGroupLabelStatus': {'Parameters':['Group'], 'Status': {}},
            'InputGroupStatus': {'Parameters':['Group'], 'Status': {}},
            'InputLabelCommand': {'Parameters':['Input'], 'Status': {}},
            'InputLabelStatus': {'Parameters':['Input'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'InputTestSignalGain': {'Parameters':['Input'], 'Status': {}},
            'MixBusLabelCommand': {'Parameters':['Mix Bus'], 'Status': {}},
            'MixBusLabelStatus': {'Parameters':['Mix Bus'], 'Status': {}},
            'OutputChannelLabelCommand': {'Parameters':['Output'], 'Status': {}},
            'OutputChannelLabelStatus': {'Parameters':['Output'], 'Status': {}},
            'OutputCompressorMakeupGain': {'Parameters':['Output'], 'Status': {}},
            'OutputCompressorRatio': {'Parameters':['Output'], 'Status': {}},
            'OutputCompressorThresholdLevel': {'Parameters':['Output'], 'Status': {}},
            'OutputCompressorTimeConstant': {'Parameters':['Output'], 'Status': {}},
            'OutputGain': {'Parameters':['Output'], 'Status': {}},
            'OutputGroupLabelCommand': {'Parameters':['Group'], 'Status': {}},
            'OutputGroupLabelStatus': {'Parameters':['Group'], 'Status': {}},
            'OutputGroupStatus': {'Parameters':['Group'], 'Status': {}},
            'OutputGroupMute': {'Parameters':['Group'], 'Status': {}},
            'OutputMute': {'Parameters':['Output'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'RearPanelAudioInputGain': {'Parameters':['Address'], 'Status': {}},
            'RearPanelAudioOutputGain': {'Parameters':['Address'], 'Status': {}},
        }

    def SetCrosspointGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -70,
            'Max' : 20
            }

        if 1<= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= self.InputSize and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CrosspointGainCmdString = 'xpgn({0},{1})={2}\r'.format(qualifier['Input'],qualifier['Mix Bus'],value)
            self.__SetHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointGain')

    def UpdateCrosspointGain(self, value, qualifier):

        if 1<= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= self.InputSize:
            CrosspointGainCmdString = 'xpgn({0},{1})?\r'.format(qualifier['Input'],qualifier['Mix Bus'])
            res = self.__UpdateHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('CrosspointGain', value, qualifier)                    
                except (KeyError, IndexError, ValueError):
                    self.Error(['CrosspointGain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrosspointGain')

    def SetCrosspointMode(self, value, qualifier):

        ValueStateValues = {
            'Direct'     : '0', 
            'Override'   : '1', 
            'Background' : '2', 
            'Auto'       : '3', 
            'Phantom'    : '5'
            }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= self.InputSize:
            CrosspointModeCmdString = 'xpmode({0},{1})={2}\r'.format(qualifier['Input'], qualifier['Mix Bus'], ValueStateValues[value])
            self.__SetHelper('CrosspointMode', CrosspointModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointMode')

    def UpdateCrosspointMode(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Direct', 
            '1' : 'Override', 
            '2' : 'Background', 
            '3' : 'Auto', 
            '5' : 'Phantom'
            }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= self.InputSize:
            CrosspointModeCmdString = 'xpmode({0},{1})?\r'.format(qualifier['Input'], qualifier['Mix Bus'])
            res = self.__UpdateHelper('CrosspointMode', CrosspointModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3:-2]]
                    self.WriteStatus('CrosspointMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['CrosspointMode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrosspointMode')

    def SetCrosspointMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
            }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= self.InputSize:
            CrosspointMuteCmdString = 'xpmt({0},{1})={2}\r'.format(qualifier['Input'], qualifier['Mix Bus'], ValueStateValues[value])
            self.__SetHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointMute')

    def UpdateCrosspointMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
            }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= self.InputSize:
            CrosspointMuteCmdString = 'xpmt({0},{1})?\r'.format(qualifier['Input'], qualifier['Mix Bus'])
            res = self.__UpdateHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3:-2]]
                    self.WriteStatus('CrosspointMute', value, qualifier)                    
                except (KeyError, IndexError):
                    self.Error(['CrosspointMute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrosspointMute')

    def UpdateDeviceMode(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Master', 
            '0' : 'Slave'
            }

        DeviceModeCmdString = 'mode?\r'
        res = self.__UpdateHelper('DeviceMode', DeviceModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('DeviceMode', value, qualifier)                
            except (KeyError, IndexError):
                self.Error(['DeviceMode: UpdateInvalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Normal', 
            '1' : 'Over Temperature - Fault Condition', 
            '2' : 'Fan Failure', 
            '3' : 'Back-up battery is low'
            }

        DeviceStatusCmdString = 'hwstat?\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['DeviceStatus: Invalid/unexpected response'])

    def UpdateFanStatus(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Normal', 
            '1' : 'Fan Failure', 
            '8' : 'Fan Stop'
            }

        FanStatusCmdString = 'fanstat?\r'
        res = self.__UpdateHelper('FanStatus', FanStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('FanStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['FanStatus: Invalid/unexpected response'])

    def UpdateFinalMixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Mix Bus']) <= 48:
            FinalMixLevelCmdString = 'mixlv(*)?\r'
            res = self.__UpdateHelper('FinalMixLevel', FinalMixLevelCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (KeyError, IndexError, ValueError):
                    self.Error(['FinalMixLevel: Invalid/unexpected response'])
                else:
                    for i in range(1, 49):
                        self.WriteStatus('FinalMixLevel', int(value[i-1]), {'Mix Bus' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateFinalMixLevel')

    def SetHeadphoneMonitorSource(self, value, qualifier):

        if 1 <= int(value) <= 48:
            HeadphoneMonitorSourceCmdString = 'monsrc={0}\r'.format(value)
            self.__SetHelper('HeadphoneMonitorSource', HeadphoneMonitorSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHeadphoneMonitorSource')

    def UpdateHeadphoneMonitorSource(self, value, qualifier):

        ValueStateValues = {
            '1'  : '1',           '21' : '21',            '41' : '41',
            '2'  : '2',           '22' : '22',            '42' : '42',
            '3'  : '3',           '23' : '23',            '43' : '43',
            '4'  : '4',           '24' : '24',            '44' : '44',
            '5'  : '5',           '25' : '25',            '45' : '45',
            '6'  : '6',           '26' : '26',            '46' : '46',
            '7'  : '7',           '27' : '27',            '47' : '47',
            '8'  : '8',           '28' : '28',            '48' : '48',
            '9'  : '9',           '29' : '29', 
            '10' : '10',          '30' : '30', 
            '11' : '11',          '31' : '31', 
            '12' : '12',          '32' : '32', 
            '13' : '13',          '33' : '33', 
            '14' : '14',          '34' : '34', 
            '15' : '15',          '35' : '35', 
            '16' : '16',          '36' : '36', 
            '17' : '17',          '37' : '37', 
            '18' : '18',          '38' : '38', 
            '19' : '19',          '39' : '39',
            '20' : '20',          '40' : '40',
            }

        HeadphoneMonitorSourceCmdString = 'monsrc?\r'
        res = self.__UpdateHelper('HeadphoneMonitorSource', HeadphoneMonitorSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('HeadphoneMonitorSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['HeadPhoneMonitorSource: Invalid/unexpected response'])

    def UpdateInputActivity(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Active', 
            '0' : 'Inactive'
            }

        if 1 <= int(qualifier['Input']) <= self.RealInputSize:

            InputActivityCmdString = 'inact(*)?\r'
            res = self.__UpdateHelper('InputActivity', InputActivityCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (KeyError, IndexError):
                    self.Error(['InputActivity: Invalid/unexpected response'])
                else:
                    for i in range(1, self.RealInputSize+1):
                        InValue = ValueStateValues[value[i-1]]
                        self.WriteStatus('InputActivity', InValue, {'Input' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateInputActivity')

    def SetInputCompressorMakeupGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 30
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Input']) <= self.RealInputSize:
            InputCompressorMakeupGainCmdString = 'incpmug({0})={1}'.format(qualifier['Input'], value)
            self.__SetHelper('InputCompressorMakeupGain', InputCompressorMakeupGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputCompressorMakeupGain')

    def UpdateInputCompressorMakeupGain(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.RealInputSize:

            InputCompressorMakeupGainCmdString = 'incpmug(*)?\r'
            res = self.__UpdateHelper('InputCompressorMakeupGain', InputCompressorMakeupGainCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (KeyError, IndexError, ValueError):
                    self.Error(['InputCompressorMakeupGain: Invalid/unexpected response'])
                else:
                    for i in range(1, self.RealInputSize+1):
                        self.WriteStatus('InputCompressorMakeupGain', int(value[i-1]), {'Input' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateInputCompressorMakeupGain')

    def SetInputCompressorRatio(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0.0,
            'Max' : 50.0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Input']) <= self.RealInputSize:
            InputCompressorRatioCmdString = 'incprat({0})={1}\r'.format(qualifier['Input'], value)
            self.__SetHelper('InputCompressorRatio', InputCompressorRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputCompressorRatio')

    def UpdateInputCompressorRatio(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.RealInputSize:
            InputCompressorRatioCmdString = 'incprat(*)?\r'
            res = self.__UpdateHelper('InputCompressorRatio', InputCompressorRatioCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (KeyError, IndexError, ValueError):
                    self.Error(['InputCompressorRatio: Invalid/unexpected response'])
                else:
                    for i in range(1, self.RealInputSize+1):
                        self.WriteStatus('InputCompressorRatio', float(value[i-1]), {'Input' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateInputCompressorRatio')

    def SetInputCompressorThresholdLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 20
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Input']) <= self.RealInputSize:
            InputCompressorThresholdLevelCmdString = 'incpthr({0})={1}\r'.format(qualifier['Input'], value)
            self.__SetHelper('InputCompressorThresholdLevel', InputCompressorThresholdLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputCompressorThresholdLevel')

    def UpdateInputCompressorThresholdLevel(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.RealInputSize:
            InputCompressorThresholdLevelCmdString = 'incpthr(*)?\r'
            res = self.__UpdateHelper('InputCompressorThresholdLevel', InputCompressorThresholdLevelCmdString, value, qualifier)
            if res:
                value = res[4:-3].split(',')
                try:
                    for i in range(1, self.RealInputSize+1):
                        self.WriteStatus('InputCompressorThresholdLevel', int(value[i-1]), {'Input' : str(i)})
                except (KeyError, IndexError, ValueError):
                    self.Error(['InputCompressorThresholdLevel: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputCompressorThresholdLevel')

    def SetInputCompressorTimeConstant(self, value, qualifier):

        ValueConstraints = {
            'Min' : 5,
            'Max' : 10000
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Input']) <= self.RealInputSize:
            InputCompressorTimeConstantCmdString = 'incptc({0})={1}\r'.format(qualifier['Input'], value)
            self.__SetHelper('InputCompressorTimeConstant', InputCompressorTimeConstantCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputCompressorTimeConstant')

    def UpdateInputCompressorTimeConstant(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.RealInputSize:
            InputCompressorTimeConstantCmdString = 'incptc(*)?\r'
            res = self.__UpdateHelper('InputCompressorTimeConstant', InputCompressorTimeConstantCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (KeyError, IndexError, ValueError):
                    self.Error(['InputCompressorTimeConstant: Invalid/unexpected response'])
                else:
                    for i in range(1, self.RealInputSize+1):
                        self.WriteStatus('InputCompressorTimeConstant', int(value[i-1]), {'Input' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateInputCompressorTimeConstant')

    def SetInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -10,
            'Max' : 60
            }

        InputVal = qualifier['Input']
        if 1 <= int(InputVal) <= self.RealInputSize and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputGainCmdString = 'ingn({0})={1}\r'.format(InputVal, str(value))
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        InputVal = qualifier['Input']
        if 1 <= int(InputVal) <= self.RealInputSize:
            InputGainCmdString = 'ingn(*)?\r'
            res = self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (KeyError, IndexError, ValueError):
                    self.Error(['InputGain: Invalid/unexpected response'])
                else:
                    for i in range(1, self.RealInputSize+1):
                        self.WriteStatus('InputGain', int(value[i-1]), {'Input' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def SetInputGroupLabelCommand(self, value, qualifier):

        GroupStates = {
            '1' : '101', 
            '2' : '102', 
            '3' : '103', 
            '4' : '104', 
            '5' : '105'
            }

        cmdstring = value
        InputGroupLabelCommandCmdString = 'ingrplb({0})=\"{1}\"\r'.format(GroupStates[qualifier['Group']], cmdstring)
        self.__SetHelper('InputGroupLabelCommand', InputGroupLabelCommandCmdString, value, qualifier)

    def UpdateInputGroupLabelStatus(self, value, qualifier):

        GroupStates = {
            '1' : '101', 
            '2' : '102', 
            '3' : '103', 
            '4' : '104', 
            '5' : '105'
            }

        if 1 <= int(qualifier['Group']) <= 5:
            InputGroupLabelStatusCmdString = 'ingrplb({0})?\r'.format(GroupStates[qualifier['Group']])
            res = self.__UpdateHelper('InputGroupLabelStatus', InputGroupLabelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res[3:-2].replace('"','')
                    self.WriteStatus('InputGroupLabelStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['InputGroupLabelStatus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputGroupLabelStatus')

    def UpdateInputGroupStatus(self, value, qualifier):

        GroupStates = {
            '1' : '101', 
            '2' : '102', 
            '3' : '103', 
            '4' : '104', 
            '5' : '105'
            }

        InputGroupStatusCmdString = 'ingrp({0})?\r'.format(GroupStates[qualifier['Group']])
        res = self.__UpdateHelper('InputGroupStatus', InputGroupStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[4:-3]
                self.WriteStatus('InputGroupStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['InputGroupStatus: Invalid/unexpected response'])

    def SetInputGroupMute(self, value, qualifier):

        GroupStates = {
            '1' : '101', 
            '2' : '102', 
            '3' : '103', 
            '4' : '104', 
            '5' : '105'
            }

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
            }

        InputGroupMuteCmdString = 'inmt({0})={1}\r'.format(GroupStates[qualifier['Group']], ValueStateValues[value])
        self.__SetHelper('InputGroupMute', InputGroupMuteCmdString, value, qualifier)

    def SetInputLabelCommand(self, value, qualifier):

        cmdstring = value
        InputLabelCommandCmdString = 'inlb({0})=\"{1}\"\r'.format(qualifier['Input'], cmdstring)
        self.__SetHelper('InputLabelCommand', InputLabelCommandCmdString, value, qualifier)

    def UpdateInputLabelStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.RealInputSize:
            InputLabelStatusCmdString = 'inlb({0})?\r'.format(qualifier['Input'])
            res = self.__UpdateHelper('InputLabelStatus', InputLabelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res[3:-2].replace('"','')
                    self.WriteStatus('InputLabelStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['InputLabelStatus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputLabelStatus')

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0',
            }

        InputVal = qualifier['Input']
        InputMuteCmdString = None
        if InputVal == 'All':
            InputMuteCmdString = self.AllInputMuteCmdString.format(ValueStateValues[value])
        else:
            if 1 <= int(InputVal) <= self.InputSize:
                InputMuteCmdString = 'inmt({0})={1}\r'.format(InputVal, ValueStateValues[value])
            else:
                self.Discard('Invalid Command for SetInputMute')

        self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)

    def UpdateInputMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
            }

        InputMuteCmdString = 'inmt(*)?\r'
        res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        if res:
            try:
                value = res[4:-3].split(',')
            except (KeyError, IndexError):
                self.Error(['InputMute All: Invalid/unexpected response'])
            else:
                for i in range(1, self.InputSize+1):
                    self.WriteStatus('InputMute', ValueStateValues[value[i-1]], {'Input' : str(i)})

    def SetInputTestSignalGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -70,
            'Max' : 20
            }

        InputVal = qualifier['Input']
        if self.TestSignalStart <= int(InputVal) <= self.InputSize and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputTestSignalGainCmdString = 'ingn({0})={1}\r'.format(InputVal, str(value))
            self.__SetHelper('InputTestSignalGain', InputTestSignalGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputTestSignalGain')

    def UpdateInputTestSignalGain(self, value, qualifier):

        InputVal = qualifier['Input']
        if self.TestSignalStart <= int(InputVal) <= self.InputSize:
            InputTestSignalGainCmdString = 'ingn({0})?\r'.format(InputVal)
            res = self.__UpdateHelper('InputTestSignalGain', InputTestSignalGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('InputTestSignalGain', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['InputTestSignalGain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputTestSignalGain')

    def SetMixBusLabelCommand(self, value, qualifier):

        cmdstring = value
        MixBusLabelCommandCmdString = 'mixlb({0})={1}\r'.format(qualifier['Mix Bus'], cmdstring)
        self.__SetHelper('MixBusLabelCommand', MixBusLabelCommandCmdString, value, qualifier)

    def UpdateMixBusLabelStatus(self, value, qualifier):

        if 1 <= int(qualifier['Mix Bus']) <= 48:
            MixBusLabelStatusCmdString = 'mixlb({0})?\r'.format(qualifier['Mix Bus'])
            res = self.__UpdateHelper('MixBusLabelStatus', MixBusLabelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res[3:-2].replace('"', '')
                    self.WriteStatus('MixBusLabelStatus', value, qualifier)                
                except (KeyError, IndexError):
                    self.Error(['MixBusLabelStatus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMixBusLabelStatus')

    def SetOutputChannelLabelCommand(self, value, qualifier):

        cmdstring = value
        OutputChannelLabelCommandCmdString = 'outlb({0})={1}\r'.format(qualifier['Output'], cmdstring)
        self.__SetHelper('OutputChannelLabelCommand', OutputChannelLabelCommandCmdString, value, qualifier)

    def UpdateOutputChannelLabelStatus(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
             OutputChannelLabelStatusCmdString = 'outlb({0})?\r'.format(qualifier['Output'])
             res = self.__UpdateHelper('OutputChannelLabelStatus', OutputChannelLabelStatusCmdString, value, qualifier)
             if res:
                 try:
                     value = res[3:-2].replace('"', '')
                     self.WriteStatus('OutputChannelLabelStatus', value, qualifier)
                 except (KeyError, IndexError):
                     self.Error(['OutputChannelLabelStatus: Invalid/unexpected response'])
        else:
             self.Discard('Invalid Command for UpdateOutputChannelLabelStatus')

    def SetOutputCompressorMakeupGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 30
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputCompressorMakeupGainCmdString = 'outcpmug({0})={1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('OutputCompressorMakeupGain', OutputCompressorMakeupGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputCompressorMakeupGain')

    def UpdateOutputCompressorMakeupGain(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputCompressorMakeupGainCmdString = 'outcpmug(*)?\r'
            res = self.__UpdateHelper('OutputCompressorMakeupGain', OutputCompressorMakeupGainCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (KeyError, IndexError, ValueError):
                    self.Error(['OutputCompressorMakeupGain: Invalid/unexpected response'])
                else:
                    for i in range(1, self.OutputSize+1):
                        self.WriteStatus('OutputCompressorMakeupGain', int(value[i-1]), {'Output' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateOutputCompressorMakeupGain')

    def SetOutputCompressorRatio(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0.0,
            'Max' : 50.0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputCompressorRatioCmdString = 'outcprat({0})={1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('OutputCompressorRatio', OutputCompressorRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputCompressorRatio')

    def UpdateOutputCompressorRatio(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputCompressorRatioCmdString = 'outcprat(*)?\r'
            res = self.__UpdateHelper('OutputCompressorRatio', OutputCompressorRatioCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (KeyError, IndexError, ValueError):
                    self.Error(['OutputCompressorRatio: Invalid/unexpected response'])
                else:
                    for i in range(1, self.OutputSize+1):
                        self.WriteStatus('OutputCompressorRatio', float(value[i-1]), {'Output' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateOutputCompressorRatio')

    def SetOutputCompressorThresholdLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 20
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputCompressorThresholdLevelCmdString = 'outcpthr({0})={1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('OutputCompressorThresholdLevel', OutputCompressorThresholdLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputCompressorThresholdLevel')

    def UpdateOutputCompressorThresholdLevel(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputCompressorThresholdLevelCmdString = 'outcpthr(*)?\r'
            res = self.__UpdateHelper('OutputCompressorThresholdLevel', OutputCompressorThresholdLevelCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (KeyError, IndexError, ValueError):
                    self.Error(['OutputCompressorThresholdLevel: Invalid/unexpected response'])
                else:
                    for i in range(1, self.OutputSize+1):
                        self.WriteStatus('OutputCompressorThresholdLevel', int(value[i-1]), {'Output' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateOutputCompressorThresholdLevel')

    def SetOutputCompressorTimeConstant(self, value, qualifier):

        ValueConstraints = {
            'Min' : 5,
            'Max' : 10000
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputCompressorTimeConstantCmdString = 'outcptc({0})={1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('OutputCompressorTimeConstant', OutputCompressorTimeConstantCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputCompressorTimeConstant')

    def UpdateOutputCompressorTimeConstant(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputCompressorTimeConstantCmdString = 'outcptc(*)?\r'
            res = self.__UpdateHelper('OutputCompressorTimeConstant', OutputCompressorTimeConstantCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (KeyError, IndexError, ValueError):
                    self.Error(['OutputCompressorTimeConstant: Invalid/unexpected response'])
                else:
                    for i in range(1, self.OutputSize+1):
                        self.WriteStatus('OutputCompressorTimeConstant', int(value[i-1]), {'Output' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateOutputCompressorTimeConstant')

    def SetOutputGain(self, value, qualifier):

        OutputStates = {
            'Group 1' : '101', 
            'Group 2' : '102', 
            'Group 3' : '103', 
            'Group 4' : '104', 
            'Group 5' : '105'
            }

        ValueConstraints = {
            'Min' : -70,
            'Max' : 20
            }

        output = qualifier['Output']
        if output[0] == 'G' and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputGainCmdString = 'outgn({0})={1}\r'.format(OutputStates[output], value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        elif ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(output) <= self.OutputSize:
            OutputGainCmdString = 'outgn({0})={1}\r'.format(output, value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)     
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        output = qualifier['Output']
        if 'Group' not in output and 1 <= int(output) <= self.OutputSize:
            OutputGainCmdString = 'outgn(*)?\r'
            res = self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
            if res:
                try:
                    gain_result = res[4:-3].split(',')
                except (KeyError, IndexError, ValueError):
                    self.Error(['OutputGain: Invalid/unexpected response'])
                else:
                    for i in range(1, self.OutputSize+1):
                        self.WriteStatus('OutputGain', int(gain_result[i-1]), {'Output' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def SetOutputGroupLabelCommand(self, value, qualifier):

        GroupStates = {
            '1' : '101', 
            '2' : '102', 
            '3' : '103', 
            '4' : '104', 
            '5' : '105'
            }

        cmdstring = value
        OutputGroupLabelCommandCmdString = 'outgrplb({0})=\"{1}\"\r'.format(GroupStates[qualifier['Group']], cmdstring)
        self.__SetHelper('OutputGroupLabelCommand', OutputGroupLabelCommandCmdString, value, qualifier)

    def UpdateOutputGroupLabelStatus(self, value, qualifier):

        GroupStates = {
            '1' : '101', 
            '2' : '102', 
            '3' : '103', 
            '4' : '104', 
            '5' : '105'
            }

        if 1 <= int(qualifier['Group']) <= 5:
            OutputGroupLabelStatusCmdString = 'outgrplb({0})?\r'.format(GroupStates[qualifier['Group']])
            res = self.__UpdateHelper('OutputGroupLabelStatus', OutputGroupLabelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res[3:-2].replace('"','')
                    self.WriteStatus('OutputGroupLabelStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['OutputGroupLabelStatus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputGroupLabelStatus')        

    def UpdateOutputGroupStatus(self, value, qualifier):

        GroupStates = {
            '1' : '101', 
            '2' : '102', 
            '3' : '103', 
            '4' : '104', 
            '5' : '105'
            }

        OutputGroupStatusCmdString = 'outgrp({0})?\r'.format(GroupStates[qualifier['Group']])
        res = self.__UpdateHelper('OutputGroupStatus', OutputGroupStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[4:-3]
                self.WriteStatus('OutputGroupStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['OutputGroupStatus: Invalid/unexpected response'])

    def SetOutputGroupMute(self, value, qualifier):

        GroupStates = {
            '1' : '101', 
            '2' : '102', 
            '3' : '103', 
            '4' : '104', 
            '5' : '105'
            }

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
            }

        OutputGroupMuteCmdString = 'outmt({0})={1}\r'.format(GroupStates[qualifier['Group']], ValueStateValues[value])
        self.__SetHelper('OutputGroupMute', OutputGroupMuteCmdString, value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
            }

        OutputMuteCmdString = None
        if qualifier['Output'] == 'All':
            OutputMuteCmdString = self.AllOutputMuteCmdString.format(ValueStateValues[value])
        elif 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputMuteCmdString = 'outmt({0})={1}\r'.format(qualifier['Output'], ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetOutputMute')

        self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateOutputMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
            }

        OutputMuteCmdString = 'outmt(*)?\r'
        res = self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        if res:
            try:
                value = res[4:-3].split(',')
            except (KeyError, IndexError):
                self.Error(['OutputMute All: Invalid/unexpected response'])
            else:
                for i in range(1, self.OutputSize+1):
                    self.WriteStatus('OutputMute', ValueStateValues[value[i-1]], {'Output' : str(i)})

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 24:
            PresetRecallCmdString = 'recall({0})\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 24:
            PresetSaveCmdString = 'store({0})\r'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRearPanelAudioInputGain(self, value, qualifier):

        AddressConstraints = {
            'Min' : 1, 
            'Max' : 20
            }

        ValueConstraints = {
            'Min' : -61,
            'Max' : 0
            }

        Address = qualifier['Address']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
            AddressConstraints['Min'] <= int(Address) <= AddressConstraints['Max']):
            RearPanelAudioInputGainCmdString = 'rpingn({})={}\r'.format(Address,value)
            self.__SetHelper('RearPanelAudioInputGain', RearPanelAudioInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRearPanelAudioInputGain')

    def UpdateRearPanelAudioInputGain(self, value, qualifier):

        AddressConstraints = {
            'Min' : 1, 
            'Max' : 20
            }

        Address = qualifier['Address']
        if AddressConstraints['Min'] <= int(Address) <= AddressConstraints['Max']:
            RearPanelAudioInputGainCmdString = 'rpingn(*)?\r'
            res = self.__UpdateHelper('RearPanelAudioInputGain', RearPanelAudioInputGainCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (ValueError, IndexError):
                    self.Error(['RearPanelAudioInputGain: Invalid/unexpected response'])
                else:
                    for i in range(1, 21):
                        self.WriteStatus('RearPanelAudioInputGain', int(value[i-1]), {'Address' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateRearPanelAudioInputGain')

    def SetRearPanelAudioOutputGain(self, value, qualifier):

        AddressConstraints = {
            'Min' : 1, 
            'Max' : self.OutputSize
            }

        ValueConstraints = {
            'Min' : -61,
            'Max' : 0
            }

        Address = qualifier['Address']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
            AddressConstraints['Min'] <= int(Address) <= AddressConstraints['Max']):
            RearPanelAudioOutputGainCmdString = 'rpoutgn({})={}\r'.format(Address,value)
            self.__SetHelper('RearPanelAudioOutputGain', RearPanelAudioOutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRearPanelAudioOutputGain')

    def UpdateRearPanelAudioOutputGain(self, value, qualifier):

        AddressConstraints = {
            'Min' : 1, 
            'Max' : self.OutputSize
            }

        Address = qualifier['Address']
        if AddressConstraints['Min'] <= int(Address) <= AddressConstraints['Max']:
            RearPanelAudioOutputGainCmdString = 'rpoutgn(*)?\r'
            res = self.__UpdateHelper('RearPanelAudioOutputGain', RearPanelAudioOutputGainCmdString, value, qualifier)
            if res:
                try:
                    value = res[4:-3].split(',')
                except (ValueError, IndexError):
                    self.Error(['RearPanelAudioOutputGain: Invalid/unexpected response'])
                else:
                    for i in range(1, self.OutputSize+1):
                        self.WriteStatus('RearPanelAudioOutputGain', int(value[i-1]), {'Address' : str(i)})
        else:
            self.Discard('Invalid Command for UpdateRearPanelAudioOutputGain')
            
    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            response = response.decode()
            if response.find('ERROR') >= 0:
                self.Error(['{0}{1}'.format(sourceCmdName, ': Error Command Reply' )])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True


        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n')
            if not res:
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n')
            return self.__CheckResponseForErrors(command, res)
            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def lect_812(self):

        self.AllInputMuteCmdString = 'inmt(*)={{{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}}\r'
        self.TestSignalStart = 9
        self.InputSize = 12
        self.RealInputSize = 8
        self.OutputSize = 12


    def lect_1612(self):

        self.AllInputMuteCmdString = 'inmt(*)={{{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}}\r'
        self.AllOutputMuteCmdString = 'outmt(*)={{{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}}\r'
        self.TestSignalStart = 17
        self.InputSize = 20
        self.RealInputSize = 16
        self.OutputSize = 12

    def lect_1624(self):

        self.AllInputMuteCmdString = 'inmt(*)={{{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}}\r'
        self.AllOutputMuteCmdString = 'outmt(*)={{{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}}\r'
        self.TestSignalStart = 17
        self.InputSize = 20
        self.RealInputSize = 16
        self.OutputSize = 24
        
    def lect_2412(self):

        self.AllInputMuteCmdString = 'inmt(*)={{{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}}\r'
        self.AllOutputMuteCmdString = 'outmt(*)={{{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}}\r'
        self.TestSignalStart = 25
        self.InputSize = 28
        self.RealInputSize = 24
        self.OutputSize = 12

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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