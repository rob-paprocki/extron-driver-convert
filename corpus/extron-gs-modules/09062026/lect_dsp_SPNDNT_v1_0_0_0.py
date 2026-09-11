from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CrosspointGain': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'CrosspointMode': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'CrosspointMute': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'DeviceMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FanStatus': {'Status': {}},
            'FinalMixLevel': {'Parameters': ['Mix Bus'], 'Status': {}},
            'HeadphoneMonitorSource': {'Status': {}},
            'InputActivity': {'Parameters': ['Input'], 'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputGroupLabelCommand': {'Parameters': ['Group'], 'Status': {}},
            'InputGroupLabelStatus': {'Parameters': ['Group'], 'Status': {}},
            'InputGroupMute': {'Parameters': ['Group'], 'Status': {}},
            'InputGroupStatus': {'Parameters': ['Group'], 'Status': {}},
            'InputLabelCommand': {'Parameters': ['Input'], 'Status': {}},
            'InputLabelStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'InputTestSignalGain': {'Parameters': ['Input'], 'Status': {}},
            'MixBusLabelCommand': {'Parameters': ['Mix Bus'], 'Status': {}},
            'MixBusLabelStatus': {'Parameters': ['Mix Bus'], 'Status': {}},
            'OutputChannelLabelCommand': {'Parameters': ['Output'], 'Status': {}},
            'OutputChannelLabelStatus': {'Parameters': ['Output'], 'Status': {}},
            'OutputGain': {'Parameters': ['Output'], 'Status': {}},
            'OutputGroupLabelCommand': {'Parameters': ['Group'], 'Status': {}},
            'OutputGroupLabelStatus': {'Parameters': ['Group'], 'Status': {}},
            'OutputGroupMute': {'Parameters': ['Group'], 'Status': {}},
            'OutputGroupStatus': {'Parameters': ['Group'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
        }


    def SetCrosspointGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 36 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CrosspointGainCmdString = 'xpgn({0},{1})={2}\r'.format(qualifier['Input'], qualifier['Mix Bus'], value)
            self.__SetHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCrosspointGain')

    def UpdateCrosspointGain(self, value, qualifier):

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 36:
            CrosspointGainCmdString = 'xpgn({0},{1})?\r'.format(qualifier['Input'], qualifier['Mix Bus'])
            res = self.__UpdateHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-1])
                    self.WriteStatus('CrosspointGain', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateCrosspointGain')
        else:
            print('Invalid Command for UpdateCrosspointGain')

    def SetCrosspointMode(self, value, qualifier):

        ValueStateValues = {
            'Direct': '0',
            'Override': '1',
            'Background': '2',
            'Auto': '3',
            'Phantom': '5'
        }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 36:
            CrosspointModeCmdString = 'xpmode({0},{1})={2}\r'.format(qualifier['Input'], qualifier['Mix Bus'], ValueStateValues[value])
            self.__SetHelper('CrosspointMode', CrosspointModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCrosspointMode')

    def UpdateCrosspointMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Direct',
            '1': 'Override',
            '2': 'Background',
            '3': 'Auto',
            '5': 'Phantom'
        }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 36:
            CrosspointModeCmdString = 'xpmode({0},{1})?\r'.format(qualifier['Input'], qualifier['Mix Bus'])
            res = self.__UpdateHelper('CrosspointMode', CrosspointModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3:-1]]
                    self.WriteStatus('CrosspointMode', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateCrosspointMode')
        else:
            print('Invalid Command for UpdateCrosspointMode')

    def SetCrosspointMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 36:
            CrosspointMuteCmdString = 'xpmt({0},{1})={2}\r'.format(qualifier['Input'], qualifier['Mix Bus'], ValueStateValues[value])
            self.__SetHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCrosspointMute')

    def UpdateCrosspointMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 36:
            CrosspointMuteCmdString = 'xpmt({0},{1})?\r'.format(qualifier['Input'], qualifier['Mix Bus'])
            res = self.__UpdateHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3:-1]]
                    self.WriteStatus('CrosspointMute', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateCrosspointMute')
        else:
            print('Invalid Command for UpdateCrosspointMute')

    def UpdateDeviceMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Master',
            '0': 'Slave'
        }

        DeviceModeCmdString = 'mode?\r'
        res = self.__UpdateHelper('DeviceMode', DeviceModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('DeviceMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDeviceMode')

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Over Temperature - Fault Condition',
            '2': 'Fan Failure',
            '3': 'Back-up battery is low'
        }

        DeviceStatusCmdString = 'hwstat?\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDeviceStatus')

    def UpdateFanStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Fan Failure',
            '8': 'Fan Stop'
        }

        FanStatusCmdString = 'fanstat?\r'
        res = self.__UpdateHelper('FanStatus', FanStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('FanStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFanStatus')

    def UpdateFinalMixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Mix Bus']) <= 48:
            FinalMixLevelCmdString = 'mixlv({0})?\r'.format(qualifier['Mix Bus'])
            res = self.__UpdateHelper('FinalMixLevel', FinalMixLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-1])
                    self.WriteStatus('FinalMixLevel', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateFinalMixLevel')
        else:
            print('Invalid Command for UpdateFinalMixLevel')

    def SetHeadphoneMonitorSource(self, value, qualifier):

        if 1 <= int(value) <= 48:
            HeadphoneMonitorSourceCmdString = 'monsrc={0}\r'.format(value)
            self.__SetHelper('HeadphoneMonitorSource', HeadphoneMonitorSourceCmdString, value, qualifier)
        else:
            print('Invalid Command for SetHeadphoneMonitorSource')

    def UpdateHeadphoneMonitorSource(self, value, qualifier):

        ValueStateValues = {
            '1': '1', '21': '21', '41': '41',
            '2': '2', '22': '22', '42': '42',
            '3': '3', '23': '23', '43': '43',
            '4': '4', '24': '24', '44': '44',
            '5': '5', '25': '25', '45': '45',
            '6': '6', '26': '26', '46': '46',
            '7': '7', '27': '27', '47': '47',
            '8': '8', '28': '28', '48': '48',
            '9': '9', '29': '29',
            '10': '10', '30': '30',
            '11': '11', '31': '31',
            '12': '12', '32': '32',
            '13': '13', '33': '33',
            '14': '14', '34': '34',
            '15': '15', '35': '35',
            '16': '16', '36': '36',
            '17': '17', '37': '37',
            '18': '18', '38': '38',
            '19': '19', '39': '39',
            '20': '20', '40': '40',
        }

        HeadphoneMonitorSourceCmdString = 'monsrc?\r'
        res = self.__UpdateHelper('HeadphoneMonitorSource', HeadphoneMonitorSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('HeadphoneMonitorSource', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateHeadphoneMonitorSource')

    def UpdateInputActivity(self, value, qualifier):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Inactive'
        }

        if 1 <= int(qualifier['Input']) <= 32:
            InputActivityCmdString = 'inact({0})?\r'.format(qualifier['Input'])
            res = self.__UpdateHelper('InputActivity', InputActivityCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3:-1]]
                    self.WriteStatus('InputActivity', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputActivity')
        else:
            print('Invalid Command for UpdateInputActivity')

    def SetInputGain(self, value, qualifier):

        InputStates = {
            'Group 1': '101',
            'Group 2': '102',
            'Group 3': '103',
            'Group 4': '104',
            'Group 5': '105'
        }

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        input_ = qualifier['Input']
        if input_[0] == 'G' and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputGainCmdString = 'ingn({0})={1}\r'.format(InputStates[input_], str(value))
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        elif 1 <= int(input_) <= 32 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputGainCmdString = 'ingn({0})={1}\r'.format(input_, str(value))
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        InputStates = {
            'Group 1': '101',
            'Group 2': '102',
            'Group 3': '103',
            'Group 4': '104',
            'Group 5': '105'
        }

        input_ = qualifier['Input']
        if input_[0] == 'G':
            InputGainCmdString = 'ingn({0})?\r'.format(InputStates[input_])
        elif 1 <= int(input_) <= 32:
            InputGainCmdString = 'ingn({0})?\r'.format(input_)
        else:
            print('Invalid Command for UpdateInputGain')

        res = self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-1])
                self.WriteStatus('InputGain', value, qualifier)

            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateInputGain')

    def SetInputGroupLabelCommand(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        cmdstring = value
        if value:
            InputGroupLabelCommandCmdString = 'ingrplb({0})=\"{1}\"\r'.format(GroupStates[qualifier['Group']], cmdstring)
            self.__SetHelper('InputGroupLabelCommand', InputGroupLabelCommandCmdString, value, qualifier)

    def UpdateInputGroupLabelStatus(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        if 1 <= int(qualifier['Group']) <= 5:
            InputGroupLabelStatusCmdString = 'ingrplb({0})?\r'.format(GroupStates[qualifier['Group']])
            res = self.__UpdateHelper('InputGroupLabelStatus', InputGroupLabelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res[3:-1].replace('"', '')
                    self.WriteStatus('InputGroupLabelStatus', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputGroupLabelStatus')
        else:
            print('Invalid Command for UpdateInputGroupLabelStatus')

    def SetInputGroupMute(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        InputGroupMuteCmdString = 'inmt({0})={1}\r'.format(GroupStates[qualifier['Group']], ValueStateValues[value])
        self.__SetHelper('InputGroupMute', InputGroupMuteCmdString, value, qualifier)

    def UpdateInputGroupStatus(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        InputGroupStatusCmdString = 'ingrp({0})?\r'.format(GroupStates[qualifier['Group']])
        res = self.__UpdateHelper('InputGroupStatus', InputGroupStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[4:-2]
                self.WriteStatus('InputGroupStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInputGroupStatus')

    def SetInputLabelCommand(self, value, qualifier):

        cmdstring = value
        if vale:
            InputLabelCommandCmdString = 'inlb({0})=\"{1}\"\r'.format(qualifier['Input'], cmdstring)
            self.__SetHelper('InputLabelCommand', InputLabelCommandCmdString, value, qualifier)

    def UpdateInputLabelStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 32:
            InputLabelStatusCmdString = 'inlb({0})?\r'.format(qualifier['Input'])
            res = self.__UpdateHelper('InputLabelStatus', InputLabelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res[3:-1].replace('"', '')
                    self.WriteStatus('InputLabelStatus', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputLabelStatus')
        else:
            print('Invalid Command for UpdateInputLabelStatus')

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        input_ = qualifier['Input']
        AllInputMuteCmdString = 'inmt(*)={{{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}}\r'
        if input_ == 'All':
            InputMuteCmdString = AllInputMuteCmdString.format(ValueStateValues[value])
        else:
            if 1 <= int(input_) <= 36:
                InputMuteCmdString = 'inmt({0})={1}\r'.format(input_, ValueStateValues[value])
            else:
                print('Invalid Command for SetInputMute')
                return
        self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)

    def UpdateInputMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        input_ = qualifier['Input']
        if input_ == 'All':
            InputMuteCmdString = 'inmt(*)?\r'
            res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
            if res:
                try:
                    mute_result = res[4:-2].split(',')

                    if all(x == mute_result[0] for x in mute_result):
                        self.WriteStatus('InputMute', ValueStateValues[mute_result[0]], qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputMute')
        else:
            if 1 <= int(input_) <= 36:
                InputMuteCmdString = 'inmt({0})?\r'.format(input_)
                res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
                if res:
                    try:
                        value = ValueStateValues[res[3:-1]]
                        self.WriteStatus('InputMute', value, qualifier)
                    except (KeyError, IndexError):
                        print('Invalid/unexpected response for UpdateInputMute')
            else:
                print('Invalid Command for UpdateInputMute')

    def SetInputTestSignalGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        input_ = qualifier['Input']
        if 33 <= int(input_) <= 36 and ValueConstraints['Min'] <= value <= \
                ValueConstraints['Max']:
            InputTestSignalGainCmdString = 'ingn({0})={1}\r'.format(input_, str(value))
            self.__SetHelper('InputTestSignalGain', InputTestSignalGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputTestSignalGain')

    def UpdateInputTestSignalGain(self, value, qualifier):

        input_ = qualifier['Input']
        if 33 <= int(input_) <= 36:
            InputTestSignalGainCmdString = 'ingn({0})?\r'.format(input_)
            res = self.__UpdateHelper('InputTestSignalGain', InputTestSignalGainCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-1])
                self.WriteStatus('InputTestSignalGain', value, qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateInputTestSignalGain')

    def SetMixBusLabelCommand(self, value, qualifier):

        cmdstring = value
        if value:
            MixBusLabelCommandCmdString = 'mixlb({0})={1}\r'.format(qualifier['Mix Bus'], cmdstring)
            self.__SetHelper('MixBusLabelCommand', MixBusLabelCommandCmdString, value, qualifier)

    def UpdateMixBusLabelStatus(self, value, qualifier):

        if 1 <= int(qualifier['Mix Bus']) <= 48:
            MixBusLabelStatusCmdString = 'mixlb({0})?\r'.format(qualifier['Mix Bus'])
            res = self.__UpdateHelper('MixBusLabelStatus', MixBusLabelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res[3:-1].replace('"', '')
                    self.WriteStatus('MixBusLabelStatus', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateMixBusLabelStatus')
        else:
            print('Invalid Command for UpdateMixBusLabelStatus')

    def SetOutputChannelLabelCommand(self, value, qualifier):

        cmdstring = value
        OutputChannelLabelCommandCmdString = 'outlb({0})={1}\r'.format(qualifier['Output'], cmdstring)
        self.__SetHelper('OutputChannelLabelCommand', OutputChannelLabelCommandCmdString, value, qualifier)

    def UpdateOutputChannelLabelStatus(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 32:
            OutputChannelLabelStatusCmdString = 'outlb({0})?\r'.format(qualifier['Output'])
            res = self.__UpdateHelper('OutputChannelLabelStatus', OutputChannelLabelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res[3:-1].replace('"', '')
                    self.WriteStatus('OutputChannelLabelStatus', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputChannelLabelStatus')
        else:
            print('Invalid Command for UpdateOutputChannelLabelStatus')

    def SetOutputGain(self, value, qualifier):

        OutputStates = {
            'Group 1': '101',
            'Group 2': '102',
            'Group 3': '103',
            'Group 4': '104',
            'Group 5': '105'
        }

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        output = qualifier['Output']
        if output[0] == 'G' and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputGainCmdString = 'outgn({0})={1}\r'.format(OutputStates[output], value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        elif ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(output) <= 32:
            OutputGainCmdString = 'outgn({0})={1}\r'.format(output, value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        OutputStates = {
            'Group 1': '101',
            'Group 2': '102',
            'Group 3': '103',
            'Group 4': '104',
            'Group 5': '105'
        }

        output = qualifier['Output']
        if output[0] == 'G':
            OutputGainCmdString = 'outgn({0})?\r'.format(OutputStates[output])
        elif 1 <= int(output) <= 32:
            OutputGainCmdString = 'outgn({0})?\r'.format(output)
        else:
            print('Invalid Command for UpdateOutputGain')

        res = self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-1])
                self.WriteStatus('OutputGain', value, qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateOutputGain')

    def SetOutputGroupLabelCommand(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }
        cmdstring = value
        OutputGroupLabelCommandCmdString = 'outgrplb({0})=\"{1}\"\r'.format(GroupStates[qualifier['Group']], cmdstring)
        self.__SetHelper('OutputGroupLabelCommand', OutputGroupLabelCommandCmdString, value, qualifier)

    def UpdateOutputGroupLabelStatus(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        if 1 <= int(qualifier['Group']) <= 5:
            OutputGroupLabelStatusCmdString = 'outgrplb({0})?\r'.format(GroupStates[qualifier['Group']])
            res = self.__UpdateHelper('OutputGroupLabelStatus', OutputGroupLabelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res[3:-1].replace('"', '')
                    self.WriteStatus('OutputGroupLabelStatus', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputGroupLabelStatus')
        else:
            print('Invalid Command for UpdateOutputGroupLabelStatus')

    def SetOutputGroupMute(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        OutputGroupMuteCmdString = 'outmt({0})={1}\r'.format(GroupStates[qualifier['Group']], ValueStateValues[value])
        self.__SetHelper('OutputGroupMute', OutputGroupMuteCmdString, value, qualifier)

    def UpdateOutputGroupStatus(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }
        OutputGroupStatusCmdString = 'outgrp({0})?\r'.format(GroupStates[qualifier['Group']])
        res = self.__UpdateHelper('OutputGroupStatus', OutputGroupStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[4:-2]
                self.WriteStatus('OutputGroupStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOutputGroupStatus')

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AllOutputMuteCmdString = 'inmt(*)={{{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0},{0}}}\r'
        if qualifier['Output'] == 'All':
            OutputMuteCmdString = AllOutputMuteCmdString.format(ValueStateValues[value])
        elif 1 <= int(qualifier['Output']) <= 32:
            OutputMuteCmdString = 'outmt({0})={1}\r'.format(qualifier['Output'], ValueStateValues[value])
        else:
            print('Invalid Command for SetOutputMute')

        self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateOutputMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if qualifier['Output'] == 'All':
            OutputMuteCmdString = 'outmt(*)?\r'
            res = self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
            if res:
                try:
                    mute_result = res[4:-2].split(',')

                    if all(x == mute_result[0] for x in mute_result):
                        self.WriteStatus('OutputMute', ValueStateValues[mute_result[0]], qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputMute')
        elif 1 <= int(qualifier['Output']) <= 32:
            OutputMuteCmdString = 'outmt({0})?\r'.format(qualifier['Output'])
            res = self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3:-1]]
                    self.WriteStatus('OutputMute', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateOutputMute')
        else:
            print('Invalid Command for UpdateOutputMute')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 24:
            PresetRecallCmdString = 'recall({0})\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 24:
            PresetSaveCmdString = 'store({0})\r'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetSave')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response.find('ERROR') >= 0:
                print('{0}{1}'.format(sourceCmdName, ': Error Command Reply'))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

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
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription:
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
        Command = self.Commands[command]
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

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