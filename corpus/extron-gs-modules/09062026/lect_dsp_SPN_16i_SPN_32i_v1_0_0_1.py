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
        self.Models = {
            'SPN 16i': self.lect_25_2569_16,
            'SPN 32i': self.lect_25_2569_32,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioInputLevel': {'Parameters': ['Input'], 'Status': {}},
            'AudioInputRawLevel': {'Parameters': ['Input'], 'Status': {}},
            'CrosspointGain': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'CrosspointMute': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FanStatus': {'Status': {}},
            'GroupCrosspointGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupCrosspointMute': {'Parameters': ['Group'], 'Status': {}},
            'GroupInputGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupInputMute': {'Parameters': ['Group'], 'Status': {}},
            'GroupRearPanelCrosspointGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupRearPanelInputGain': {'Parameters': ['Group'], 'Status': {}},
            'InputActivityStatus': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'InputClippingStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputCompressorGain': {'Parameters': ['Input'], 'Status': {}},
            'InputCompressorMakeupGain': {'Parameters': ['Input'], 'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'InputMuteAll': {'Status': {}},
            'InputPhantomPower': {'Parameters': ['Input'], 'Status': {}},
            'MixBusFinalMixLevel': {'Parameters': ['Mix Bus'], 'Status': {}},
            'Preset': {'Parameters': ['Mode'], 'Status': {}},
            'RearPanelCrosspointGain': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'RearPanelInputGain': {'Parameters': ['Input'], 'Status': {}},
        }

    def UpdateAudioInputLevel(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        if 1 <= inputVal <= self.Size + 4:
            AudioInputLevelCmdString = 'inlv({0})?\r'.format(inputVal)
            res = self.__UpdateHelper('AudioInputLevel', AudioInputLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    if -70 <= value <= 20:
                        self.WriteStatus('AudioInputLevel', value, qualifier)
                    else:
                        self.Error(['AudioInputLevel: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['AudioInputLevel: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioInputLevel')

    def UpdateAudioInputRawLevel(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        if 1 <= inputVal <= self.Size + 4:
            AudioInputRawLevelCmdString = 'inlvraw({0})?\r'.format(inputVal)
            res = self.__UpdateHelper('AudioInputRawLevel', AudioInputRawLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    if -70 <= value <= 20:
                        self.WriteStatus('AudioInputRawLevel', value, qualifier)
                    else:
                        self.Error(['AudioInputRawLevel: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['AudioInputRawLevel: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioInputRawLevel')

    def SetCrosspointGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        inputVal = int(qualifier['Input'])
        mixBus = int(qualifier['Mix Bus'])

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= inputVal <= self.Size + 4 and 1 <= mixBus <= 48:
            CrosspointGainCmdString = 'xpgn({0},{1})={2}\r'.format(inputVal, mixBus, value)
            self.__SetHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointGain')

    def UpdateCrosspointGain(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        mixBus = int(qualifier['Mix Bus'])

        if 1 <= inputVal <= self.Size + 4 and 1 <= mixBus <= 48:
            CrosspointGainCmdString = 'xpgn({0},{1})?\r'.format(inputVal, mixBus)
            res = self.__UpdateHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    if -70 <= value <= 20:
                        self.WriteStatus('CrosspointGain', value, qualifier)
                    else:
                        self.Error(['CrosspointGain: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['CrosspointGain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrosspointGain')

    def SetCrosspointMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        inputVal = int(qualifier['Input'])
        mixBus = int(qualifier['Mix Bus'])

        if 1 <= inputVal <= self.Size + 4 and 1 <= mixBus <= 48:
            CrosspointMuteCmdString = 'xpmt({0},{1})={2}\r'.format(inputVal, mixBus, ValueStateValues[value])
            self.__SetHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointMute')

    def UpdateCrosspointMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        inputVal = int(qualifier['Input'])
        mixBus = int(qualifier['Mix Bus'])

        if 1 <= inputVal <= self.Size + 4 and 1 <= mixBus <= 48:
            CrosspointMuteCmdString = 'xpmt({0},{1})?\r'.format(inputVal, mixBus)
            res = self.__UpdateHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3]]
                    self.WriteStatus('CrosspointMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['CrosspointMute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrosspointMute')

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Over Temperature - Fault Condition',
            '2': 'Fan Failure',
            '3': 'Back-up Battery is Low'
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
            '0': 'Normal',
            '1': 'Fan Failure',
            '8': 'Fan Stop'
        }

        FanStatusCmdString = 'fanstat?\r'
        res = self.__UpdateHelper('FanStatus', FanStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('FanStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['FanStatus: Invalid/unexpected response'])

    def SetGroupCrosspointGain(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        group = GroupStates[qualifier['Group']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupCrosspointGainCmdString = 'xpgn({0})={1}\r'.format(group, value)
            self.__SetHelper('GroupCrosspointGain', GroupCrosspointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupCrosspointGain')

    def UpdateGroupCrosspointGain(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        group = GroupStates[qualifier['Group']]
        GroupCrosspointGainCmdString = 'xpgn({0})?\r'.format(group)
        res = self.__UpdateHelper('GroupCrosspointGain', GroupCrosspointGainCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-2])
                if -70 <= value <= 20:
                    self.WriteStatus('GroupCrosspointGain', value, qualifier)
                else:
                    self.Error(['GroupCrosspointGain: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['GroupCrosspointGain: Invalid/unexpected response'])

    def SetGroupCrosspointMute(self, value, qualifier):

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

        group = GroupStates[qualifier['Group']]
        GroupCrosspointMuteCmdString = 'xpmt({0})={1}\r'.format(group, ValueStateValues[value])
        self.__SetHelper('GroupCrosspointMute', GroupCrosspointMuteCmdString, value, qualifier)

    def UpdateGroupCrosspointMute(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        group = GroupStates[qualifier['Group']]
        GroupCrosspointMuteCmdString = 'xpmt({0})?\r'.format(group)
        res = self.__UpdateHelper('GroupCrosspointMute', GroupCrosspointMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('GroupCrosspointMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['GroupCrosspointMute: Invalid/unexpected response'])

    def SetGroupInputGain(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        ValueConstraints = {
            'Min': -10,
            'Max': 60
        }

        group = GroupStates[qualifier['Group']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupInputGainCmdString = 'ingn({0})={1}\r'.format(group, value)
            self.__SetHelper('GroupInputGain', GroupInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupInputGain')

    def UpdateGroupInputGain(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        group = GroupStates[qualifier['Group']]
        GroupInputGainCmdString = 'ingn({0})?\r'.format(group)
        res = self.__UpdateHelper('GroupInputGain', GroupInputGainCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-2])
                if -10 <= value <= 60:
                    self.WriteStatus('GroupInputGain', value, qualifier)
                else:
                    self.Error(['GroupInputGain: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['GroupInputGain: Invalid/unexpected response'])

    def SetGroupInputMute(self, value, qualifier):

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

        group = GroupStates[qualifier['Group']]
        GroupInputMuteCmdString = 'inmt({0})={1}\r'.format(group, ValueStateValues[value])
        self.__SetHelper('GroupInputMute', GroupInputMuteCmdString, value, qualifier)

    def UpdateGroupInputMute(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        group = GroupStates[qualifier['Group']]
        GroupInputMuteCmdString = 'inmt({0})?\r'.format(group)
        res = self.__UpdateHelper('GroupInputMute', GroupInputMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('GroupInputMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['GroupInputMute: Invalid/unexpected response'])

    def SetGroupRearPanelCrosspointGain(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        ValueConstraints = {
            'Min': -61,
            'Max': 0
        }

        group = GroupStates[qualifier['Group']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupRearPanelCrosspointGainCmdString = 'rpxpgn({0})={1}\r'.format(group, value)
            self.__SetHelper('GroupRearPanelCrosspointGain', GroupRearPanelCrosspointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupRearPanelCrosspointGain')

    def UpdateGroupRearPanelCrosspointGain(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        group = GroupStates[qualifier['Group']]
        GroupRearPanelCrosspointGainCmdString = 'rpxpgn({0})?\r'.format(group)
        res = self.__UpdateHelper('GroupRearPanelCrosspointGain', GroupRearPanelCrosspointGainCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-2])
                if -61 <= value <= 0:
                    self.WriteStatus('GroupRearPanelCrosspointGain', value, qualifier)
                else:
                    self.Error(['GroupRearPanelCrosspointGain: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['GroupRearPanelCrosspointGain: Invalid/unexpected response'])

    def SetGroupRearPanelInputGain(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        ValueConstraints = {
            'Min': -61,
            'Max': 0
        }

        group = GroupStates[qualifier['Group']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupRearPanelInputGainCmdString = 'rpingn({0})={1}\r'.format(group, value)
            self.__SetHelper('GroupRearPanelInputGain', GroupRearPanelInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupRearPanelInputGain')

    def UpdateGroupRearPanelInputGain(self, value, qualifier):

        GroupStates = {
            '1': '101',
            '2': '102',
            '3': '103',
            '4': '104',
            '5': '105'
        }

        group = GroupStates[qualifier['Group']]
        GroupRearPanelInputGainCmdString = 'rpingn({0})?\r'.format(group)
        res = self.__UpdateHelper('GroupRearPanelInputGain', GroupRearPanelInputGainCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-2])
                if -61 <= value <= 0:
                    self.WriteStatus('GroupRearPanelInputGain', value, qualifier)
                else:
                    self.Error(['GroupRearPanelInputGain: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['GroupRearPanelInputGain: Invalid/unexpected response'])

    def UpdateInputActivityStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Inactive'
        }

        inputVal = int(qualifier['Input'])
        mixBus = qualifier['Mix Bus']
        if 1 <= inputVal <= self.Size:
            if mixBus == 'Any':
                InputActivityStatusCmdString = 'inact({0})?\r'.format(inputVal)
            elif 1 <= int(mixBus) <= 48:
                InputActivityStatusCmdString = 'inact({0},{1})?\r'.format(inputVal, mixBus)

            if InputActivityStatusCmdString:
                res = self.__UpdateHelper('InputActivityStatus', InputActivityStatusCmdString, value, qualifier)
                if res:
                    try:
                        value = ValueStateValues[res[3]]
                        self.WriteStatus('InputActivityStatus', value, qualifier)
                    except (KeyError, IndexError):
                        self.Error(['InputActivityStatus: Invalid/unexpected response'])
            else:
                self.Discard('Invalid Command for UpdateInputActivityStatus')
        else:
            self.Discard('Invalid Command for UpdateInputActivityStatus')

    def UpdateInputClippingStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'Clipping',
            '0': 'Not Clipping'
        }

        inputVal = int(qualifier['Input'])
        if 1 <= inputVal <= self.Size:
            InputClippingStatusCmdString = 'incl({0})?\r'.format(inputVal)
            res = self.__UpdateHelper('InputClippingStatus', InputClippingStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3]]
                    self.WriteStatus('InputClippingStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['InputClippingStatus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputClippingStatus')

    def UpdateInputCompressorGain(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        if 1 <= inputVal <= self.Size:
            InputCompressorGainCmdString = 'incpgn({0})?\r'.format(inputVal)
            res = self.__UpdateHelper('InputCompressorGain', InputCompressorGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    if value <= 0:
                        self.WriteStatus('InputCompressorGain', value, qualifier)
                    else:
                        self.Error(['InputCompressorGain: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['InputCompressorGain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputCompressorGain')

    def SetInputCompressorMakeupGain(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 30
        }

        inputVal = int(qualifier['Input'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= inputVal <= self.Size:
            InputCompressorMakeupGainCmdString = 'incpmug({0})={1}\r'.format(inputVal, value)
            self.__SetHelper('InputCompressorMakeupGain', InputCompressorMakeupGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputCompressorMakeupGain')

    def UpdateInputCompressorMakeupGain(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        if 1 <= inputVal <= self.Size:
            InputCompressorMakeupGainCmdString = 'incpmug({0})?\r'.format(inputVal)
            res = self.__UpdateHelper('InputCompressorMakeupGain', InputCompressorMakeupGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    if 0 <= value <= 30:
                        self.WriteStatus('InputCompressorMakeupGain', value, qualifier)
                    else:
                        self.Error(['InputCompressorMakeupGain: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['InputCompressorMakeupGain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputCompressorMakeupGain')

    def SetInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -10,
            'Max': 60
        }

        inputVal = int(qualifier['Input'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= inputVal <= self.Size:
            InputGainCmdString = 'ingn({0})={1}\r'.format(inputVal, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        if 1 <= inputVal <= self.Size:
            InputGainCmdString = 'ingn({0})?\r'.format(inputVal)
            res = self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    if -10 <= value <= 60:
                        self.WriteStatus('InputGain', value, qualifier)
                    else:
                        self.Error(['InputGain: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['InputGain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        inputVal = int(qualifier['Input'])
        if 1 <= inputVal <= self.Size:
            InputMuteCmdString = 'inmt({0})={1}\r'.format(inputVal, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):
        self.UpdateInputMuteAll(value, qualifier)

    def SetInputMuteAll(self, value, qualifier):

        InputMuteAllCmdString = 'inmt(*)={0}\r'.format(self.InputMuteStates[value])
        self.__SetHelper('InputMuteAll', InputMuteAllCmdString, value, qualifier)

    def UpdateInputMuteAll(self, value, qualifier):

        states = {
            '1': 'On',
            '0': 'Off'
        }

        InputMuteAllCmdString = 'inmt(*)?\r'
        res = self.__UpdateHelper('InputMuteAll', InputMuteAllCmdString, value, qualifier)
        if res:
            try:
                muteall = True
                count = 0
                values = res[4:-3].split(',')
                lastinputmute = values[0]
                for i in values:
                    if i != lastinputmute:
                        muteall = False
                    lastinputmute = i
                    count += 1
                    self.WriteStatus('InputMute', states[i], {'Input': str(count)})
                if muteall:
                    self.WriteStatus('InputMuteAll', states[lastinputmute], qualifier)
                else:
                    self.WriteStatus('InputMuteAll', 'Off', qualifier)
            except (KeyError, IndexError):
                self.Error(['InputMuteAll: Invalid/unexpected response'])

    def SetInputPhantomPower(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        inputVal = int(qualifier['Input'])
        if 1 <= inputVal <= self.Size:
            InputPhantomPowerCmdString = 'inph({0})={1}\r'.format(inputVal, ValueStateValues[value])
            self.__SetHelper('InputPhantomPower', InputPhantomPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPhantomPower')

    def UpdateInputPhantomPower(self, value, qualifier):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        inputVal = int(qualifier['Input'])
        if 1 <= inputVal <= self.Size:
            InputPhantomPowerCmdString = 'inph({0})?\r'.format(inputVal)
            res = self.__UpdateHelper('InputPhantomPower', InputPhantomPowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3]]
                    self.WriteStatus('InputPhantomPower', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['InputPhantomPower: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputPhantomPower')

    def UpdateMixBusFinalMixLevel(self, value, qualifier):

        mixbus = int(qualifier['Mix Bus'])
        if 1 <= mixbus <= 48:
            MixBusFinalMixLevelCmdString = 'mixlv({0})?\r'.format(mixbus)
            res = self.__UpdateHelper('MixBusFinalMixLevel', MixBusFinalMixLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    if -70 <= value <= 20:
                        self.WriteStatus('MixBusFinalMixLevel', value, qualifier)
                    else:
                        self.Error(['MixBusFinalMixLevel: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['MixBusFinalMixLevel: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMixBusFinalMixLevel')

    def SetPreset(self, value, qualifier):

        ModeStates = {
            'Recall': 'recall',
            'Save': 'store'
        }

        mode = ModeStates[qualifier['Mode']]
        if 1 <= int(value) <= 24:
            PresetCmdString = '{0}({1})\r'.format(mode, value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetRearPanelCrosspointGain(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        mixBus = int(qualifier['Mix Bus'])

        if self.RPCGMin <= value <= self.RPCGMax and 1 <= inputVal <= self.Size + 4 and 1 <= mixBus <= 48:
            RearPanelCrosspointGainCmdString = 'rpxpgn({0},{1})={2}\r'.format(inputVal, mixBus, value)
            self.__SetHelper('RearPanelCrosspointGain', RearPanelCrosspointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRearPanelCrosspointGain')

    def UpdateRearPanelCrosspointGain(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        mixBus = int(qualifier['Mix Bus'])

        if 1 <= inputVal <= self.Size + 4 and 1 <= mixBus <= 48:
            RearPanelCrosspointGainCmdString = 'rpxpgn({0},{1})?\r'.format(inputVal, mixBus)
            res = self.__UpdateHelper('RearPanelCrosspointGain', RearPanelCrosspointGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    if self.RPCGMin <= value <= self.RPCGMax:
                        self.WriteStatus('RearPanelCrosspointGain', value, qualifier)
                    else:
                        self.Error(['RearPanelCrosspointGain: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['RearPanelCrosspointGain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRearPanelCrosspointGain')

    def SetRearPanelInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -61,
            'Max': 0
        }

        inputVal = int(qualifier['Input'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= inputVal <= self.Size:
            RearPanelInputGainCmdString = 'rpingn({0})={1}\r'.format(inputVal, value)
            self.__SetHelper('RearPanelInputGain', RearPanelInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRearPanelInputGain')

    def UpdateRearPanelInputGain(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        if 1 <= inputVal <= self.Size:
            RearPanelInputGainCmdString = 'rpingn({0})?\r'.format(inputVal)
            res = self.__UpdateHelper('RearPanelInputGain', RearPanelInputGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    if -61 <= value <= 0:
                        self.WriteStatus('RearPanelInputGain', value, qualifier)
                    else:
                        self.Error(['RearPanelInputGain: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['RearPanelInputGain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRearPanelInputGain')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def lect_25_2569_16(self):
        self.Size = 16
        self.RPCGMin = -61
        self.RPCGMax = 0
        self.InputMuteStates = {
            'On': '{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}',
            'Off': '{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}'
        }

    def lect_25_2569_32(self):
        self.Size = 32
        self.RPCGMin = -70
        self.RPCGMax = 20
        self.InputMuteStates = {
            'On': '{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}',
            'Off': '{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}'
        }

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
