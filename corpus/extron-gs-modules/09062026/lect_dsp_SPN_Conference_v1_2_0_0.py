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
        self.NumberofPhoneDirectoryEntries = 5

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AEC': {'Status': {}},
            'AECReferenceSource': {'Status': {}},
            'AECSendSignalSource': {'Status': {}},
            'CodecChime': {'Parameters': ['Interface'], 'Status': {}},
            'CodecChimeLevel': {'Parameters': ['Interface'], 'Status': {}},
            'CodecConnectionStatus': {'Parameters': ['Interface'], 'Status': {}},
            'CodecPrivacy': {'Parameters': ['Interface'], 'Status': {}},
            'CodecPrivacyMode': {'Parameters': ['Interface'], 'Status': {}},
            'CrosspointGain': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'CrosspointMode': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'CrosspointMute': {'Parameters': ['Input', 'Mix Bus'], 'Status': {}},
            'DeviceMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FanStatus': {'Status': {}},
            'FinalMixLevel': {'Parameters': ['Mix Bus'], 'Status': {}},
            'HeadphoneMonitorSource': {'Status': {}},
            'InputActivity': {'Parameters': ['Input'], 'Status': {}},
            'InputCompressorMakeupGain': {'Parameters': ['Input'], 'Status': {}},
            'InputCompressorRatio': {'Parameters': ['Input'], 'Status': {}},
            'InputCompressorThresholdLevel': {'Parameters': ['Input'], 'Status': {}},
            'InputCompressorTimeConstant': {'Parameters': ['Input'], 'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'InputTestSignalGain': {'Parameters': ['Input'], 'Status': {}},
            'LEC': {'Status': {}},
            'MixBusLabelCommand': {'Parameters': ['Mix Bus'], 'Status': {}},
            'MixBusLabelStatus': {'Parameters': ['Mix Bus'], 'Status': {}},
            'NRFDepth': {'Parameters': ['Input'], 'Status': {}},
            'NRFEnable': {'Parameters': ['Input'], 'Status': {}},
            'OutputCompressorMakeupGain': {'Parameters': ['Output'], 'Status': {}},
            'OutputCompressorRatio': {'Parameters': ['Output'], 'Status': {}},
            'OutputCompressorThresholdLevel': {'Parameters': ['Output'], 'Status': {}},
            'OutputCompressorTimeConstant': {'Parameters': ['Output'], 'Status': {}},
            'OutputGain': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'PhoneDirectoryAddress': {'Status': {}},
            'PhoneDirectoryNavigation': {'Status': {}},
            'PhoneDirectoryResults': {'Parameters': ['Entry'], 'Status': {}},
            'PhoneDirectoryResultSet': {'Parameters': ['Entry'], 'Status': {}},
            'PhoneDirectoryStore': {'Status': {}},
            'PhoneDirectoryUpdate': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'TelephoneAutoAnswer': {'Status': {}},
            'TelephoneAutoDisconnect': {'Status': {}},
            'TelephoneConnectionChimeLevel': {'Status': {}},
            'TelephoneLineConnectionStatus': {'Status': {}},
            'TelephoneDialCommand': {'Status': {}},
            'TelephoneDialingSpeed': {'Status': {}},
            'TelephoneDTMF': {'Status': {}},
            'TelephoneDTMFLevel': {'Status': {}},
            'TelephoneHookFlash': {'Status': {}},
            'TelephoneIncomingCallStatus': {'Status': {}},
            'TelephonePrivacy': {'Status': {}},
            'TelephonePrivacyMode': {'Status': {}},
            'TelephoneRedial': {'Status': {}},
        }

    @property
    def NumberofPhoneDirectoryEntries(self):
        return self._NumberofPhoneDirectoryEntries

    @NumberofPhoneDirectoryEntries.setter
    def NumberofPhoneDirectoryEntries(self, value):
        if 1 <= int(value) <= 15:
            self._NumberofPhoneDirectoryEntries = int(value)
            self.phone_directory = Directory(self._NumberofPhoneDirectoryEntries, 'PhoneDirectoryResults', filler='')
            self.phone_directory.write_status_function = self.WriteStatus
        else:
            self.Error(['Number of Phone Directory Entries should be a value between 1 to 15.'])

    def SetAEC(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        AECCmdString = 'aecen={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AEC', AECCmdString, value, qualifier)

    def UpdateAEC(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AECCmdString = 'aecen?\r'
        res = self.__UpdateHelper('AEC', AECCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('AEC', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAECReferenceSource(self, value, qualifier):

        if 1 <= int(value) <= 48:
            AECReferenceSourceCmdString = 'aecref={0}\r'.format(value)
            self.__SetHelper('AECReferenceSource', AECReferenceSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAECReferenceSource')

    def UpdateAECReferenceSource(self, value, qualifier):

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

        AECReferenceSourceCmdString = 'aecref?\r'
        res = self.__UpdateHelper('AECReferenceSource', AECReferenceSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('AECReferenceSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAECSendSignalSource(self, value, qualifier):
        if 1 <= int(value) <= 48:
            AECSendSignalSourceCmdString = 'aecsig={0}\r'.format(value)
            self.__SetHelper('AECSendSignalSource', AECSendSignalSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAECSendSignalSource')

    def UpdateAECSendSignalSource(self, value, qualifier):

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

        AECSendSignalSourceCmdString = 'aecsig?\r'
        res = self.__UpdateHelper('AECSendSignalSource', AECSendSignalSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('AECSendSignalSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetCodecChime(self, value, qualifier):

        InterfaceStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        CodecChimeCmdString = 'codconnchm({0})={1}\r'.format(InterfaceStates[qualifier['Interface']], ValueStateValues[value])
        self.__SetHelper('CodecChime', CodecChimeCmdString, value, qualifier)

    def UpdateCodecChime(self, value, qualifier):

        UpdateInterfaceStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        CodecChimeCmdString = 'codconnchm({0})?\r'.format(UpdateInterfaceStates[qualifier['Interface']])
        res = self.__UpdateHelper('CodecChime', CodecChimeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('CodecChime', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetCodecChimeLevel(self, value, qualifier):

        InterfaceStates = {
            '1': '1',
            '2': '2'
        }

        ValueConstraints = {
            'Min': -12,
            'Max': 12
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CodecChimeLevelCmdString = 'codcchmlv({0})={1}\r'.format(InterfaceStates[qualifier['Interface']], value)
            self.__SetHelper('CodecChimeLevel', CodecChimeLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCodecChimeLevel')

    def UpdateCodecChimeLevel(self, value, qualifier):

        UpdateInterfaceStates = {
            '1': '1',
            '2': '2'
        }

        CodecChimeLevelCmdString = 'codcchmlv({0})?\r'.format(UpdateInterfaceStates[qualifier['Interface']])
        res = self.__UpdateHelper('CodecChimeLevel', CodecChimeLevelCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-2])
                self.WriteStatus('CodecChimeLevel', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetCodecConnectionStatus(self, value, qualifier):

        InterfaceStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'Connected': '1',
            'Disconnected': '0'
        }

        CodecConnectionStatusCmdString = 'codconn({0})={1}\r'.format(InterfaceStates[qualifier['Interface']], ValueStateValues[value])
        self.__SetHelper('CodecConnectionStatus', CodecConnectionStatusCmdString, value, qualifier)

    def UpdateCodecConnectionStatus(self, value, qualifier):

        InterfaceStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            '1': 'Connected',
            '0': 'Disconnected'
        }

        CodecConnectionStatusCmdString = 'codconn({0})?\r'.format(InterfaceStates[qualifier['Interface']])
        res = self.__UpdateHelper('CodecConnectionStatus', CodecConnectionStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('CodecConnectionStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetCodecPrivacy(self, value, qualifier):

        InterfaceStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        CodecPrivacyCmdString = 'codpriv({0})={1}\r'.format(InterfaceStates[qualifier['Interface']], ValueStateValues[value])
        self.__SetHelper('CodecPrivacy', CodecPrivacyCmdString, value, qualifier)

    def UpdateCodecPrivacy(self, value, qualifier):

        InterfaceStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        CodecPrivacyCmdString = 'codpriv({0})?\r'.format(InterfaceStates[qualifier['Interface']])
        res = self.__UpdateHelper('CodecPrivacy', CodecPrivacyCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('CodecPrivacy', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetCodecPrivacyMode(self, value, qualifier):

        InterfaceStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'Only Mute Transmit Audio': '1',
            'Only Mute Receive Audio': '2',
            'Mute Both Transmit and Receive Audio': '3'
        }

        CodecPrivacyModeCmdString = 'codprivmod({0})={1}\r'.format(InterfaceStates[qualifier['Interface']], ValueStateValues[value])
        self.__SetHelper('CodecPrivacyMode', CodecPrivacyModeCmdString, value, qualifier)

    def UpdateCodecPrivacyMode(self, value, qualifier):

        InterfaceStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            '1': 'Only Mute Transmit Audio',
            '2': 'Only Mute Receive Audio',
            '3': 'Mute Both Transmit and Receive Audio'
        }

        CodecPrivacyModeCmdString = 'codprivmod({0})?\r'.format(InterfaceStates[qualifier['Interface']])
        res = self.__UpdateHelper('CodecPrivacyMode', CodecPrivacyModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('CodecPrivacyMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetCrosspointGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 8 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CrosspointGainCmdString = 'xpgn({0},{1})={2}\r'.format(qualifier['Input'], qualifier['Mix Bus'], value)
            self.__SetHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointGain')

    def UpdateCrosspointGain(self, value, qualifier):

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 8:
            CrosspointGainCmdString = 'xpgn({0},{1})?\r'.format(qualifier['Input'], qualifier['Mix Bus'])
            res = self.__UpdateHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('CrosspointGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrosspointGain')

    def SetCrosspointMode(self, value, qualifier):

        ValueStateValues = {
            'Direct': '0',
            'Override': '1',
            'Background': '2',
            'Auto': '3',
            'Phantom': '5'
        }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 8:
            CrosspointModeCmdString = 'xpmode({0},{1})={2}\r'.format(qualifier['Input'], qualifier['Mix Bus'], ValueStateValues[value])
            self.__SetHelper('CrosspointMode', CrosspointModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointMode')

    def UpdateCrosspointMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Direct',
            '1': 'Override',
            '2': 'Background',
            '3': 'Auto',
            '5': 'Phantom'
        }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 8:
            CrosspointModeCmdString = 'xpmode({0},{1})?\r'.format(qualifier['Input'], qualifier['Mix Bus'])
            res = self.__UpdateHelper('CrosspointMode', CrosspointModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3:-2]]
                    self.WriteStatus('CrosspointMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrosspointMode')

    def SetCrosspointMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 8:
            CrosspointMuteCmdString = 'xpmt({0},{1})={2}\r'.format(qualifier['Input'], qualifier['Mix Bus'], ValueStateValues[value])
            self.__SetHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointMute')

    def UpdateCrosspointMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if 1 <= int(qualifier['Mix Bus']) <= 48 and 1 <= int(qualifier['Input']) <= 8:
            CrosspointMuteCmdString = 'xpmt({0},{1})?\r'.format(qualifier['Input'], qualifier['Mix Bus'])
            res = self.__UpdateHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3:-2]]
                    self.WriteStatus('CrosspointMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrosspointMute')

    def UpdateDeviceMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Master',
            '0': 'Slave'
        }

        DeviceModeCmdString = 'mode?\r'
        res = self.__UpdateHelper('DeviceMode', DeviceModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('DeviceMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Over Temperature - Fault Condition',
            '2': 'Fan Failure',
            '3': 'Back-up battery is low',
            '4': 'Power Amp Fault'
        }

        DeviceStatusCmdString = 'hwstat?\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

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
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('FanStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def UpdateFinalMixLevel(self, value, qualifier):

        if 1 <= int(qualifier['Mix Bus']) <= 48:
            FinalMixLevelCmdString = 'mixlv({0})?\r'.format(qualifier['Mix Bus'])
            res = self.__UpdateHelper('FinalMixLevel', FinalMixLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('FinalMixLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
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
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('HeadphoneMonitorSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def UpdateInputActivity(self, value, qualifier):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Inactive'
        }

        if 1 <= int(qualifier['Input']) <= 4:
            InputActivityCmdString = 'inact({0})?\r'.format(qualifier['Input'])
            res = self.__UpdateHelper('InputActivity', InputActivityCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3:-2]]
                    self.WriteStatus('InputActivity', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputActivity')

    def SetInputCompressorMakeupGain(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 30
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Input']) <= 4:
            InputCompressorMakeupGainCmdString = 'incpmug({0})={1}'.format(qualifier['Input'], value)
            self.__SetHelper('InputCompressorMakeupGain', InputCompressorMakeupGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputCompressorMakeupGain')

    def UpdateInputCompressorMakeupGain(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            InputCompressorMakeupGainCmdString = 'incpmug({0})?\r'.format(qualifier['Input'])
            res = self.__UpdateHelper('InputCompressorMakeupGain', InputCompressorMakeupGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('InputCompressorMakeupGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputCompressorMakeupGain')

    def SetInputCompressorRatio(self, value, qualifier):

        ValueConstraints = {
            'Min': 0.0,
            'Max': 50.0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Input']) <= 4:
            InputCompressorRatioCmdString = 'incprat({0})={1}\r'.format(qualifier['Input'], value)
            self.__SetHelper('InputCompressorRatio', InputCompressorRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputCompressorRatio')

    def UpdateInputCompressorRatio(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            InputCompressorRatioCmdString = 'incprat({0})?\r'.format(qualifier['Input'])
            res = self.__UpdateHelper('InputCompressorRatio', InputCompressorRatioCmdString, value, qualifier)
            if res:
                try:
                    value = float(res[3:-2])
                    self.WriteStatus('InputCompressorRatio', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputCompressorRatio')

    def SetInputCompressorThresholdLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Input']) <= 4:
            InputCompressorThresholdLevelCmdString = 'incpthr({0})={1}\r'.format(qualifier['Input'], value)
            self.__SetHelper('InputCompressorThresholdLevel', InputCompressorThresholdLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputCompressorThresholdLevel')

    def UpdateInputCompressorThresholdLevel(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            InputCompressorThresholdLevelCmdString = 'incpthr({0})?\r'.format(qualifier['Input'])
            res = self.__UpdateHelper('InputCompressorThresholdLevel', InputCompressorThresholdLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('InputCompressorThresholdLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputCompressorThresholdLevel')

    def SetInputCompressorTimeConstant(self, value, qualifier):

        ValueConstraints = {
            'Min': 5,
            'Max': 10000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Input']) <= 4:
            InputCompressorTimeConstantCmdString = 'incptc({0})={1}\r'.format(qualifier['Input'], value)
            self.__SetHelper('InputCompressorTimeConstant', InputCompressorTimeConstantCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputCompressorTimeConstant')

    def UpdateInputCompressorTimeConstant(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 4:
            InputCompressorTimeConstantCmdString = 'incptc({0})?\r'.format(qualifier['Input'])
            res = self.__UpdateHelper('InputCompressorTimeConstant', InputCompressorTimeConstantCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('InputCompressorTimeConstant', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputCompressorTimeConstant')

    def SetInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -20,
            'Max': 20
        }

        inputVal = qualifier['Input']

        if 1 <= int(inputVal) <= 4 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputGainCmdString = 'ingn({0})={1}\r'.format(inputVal, str(value))
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        inputVal = qualifier['Input']

        if 1 <= int(inputVal) <= 4:
            InputGainCmdString = 'ingn({0})?\r'.format(inputVal)
            res = self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('InputGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        inputVal = qualifier['Input']

        if inputVal == 'All':
            InputMuteCmdString = 'inmt(*)={{{0},{0},{0},{0},{0},{0},{0},{0}}}\r'.format(ValueStateValues[value])
        else:
            if 1 <= int(inputVal) <= 8:
                InputMuteCmdString = 'inmt({0})={1}\r'.format(inputVal, ValueStateValues[value])
            else:
                self.Discard('Invalid Command for SetInputMute')
                return

        self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)

    def UpdateInputMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        inputVal = qualifier['Input']

        if inputVal == 'All':
            InputMuteCmdString = 'inmt(*)?\r'
            res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
            if res:
                try:
                    mute_result = res[4:-2].split(',')
                    if all(x == mute_result[0] for x in mute_result):
                        self.WriteStatus('InputMute', ValueStateValues[mute_result[0]], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            if 1 <= int(inputVal) <= 8:
                InputMuteCmdString = 'inmt({0})?\r'.format(inputVal)
                res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
                if res:
                    try:
                        value = ValueStateValues[res[3:-2]]
                        self.WriteStatus('InputMute', value, qualifier)
                    except (KeyError, IndexError):
                        self.Error(['Invalid/unexpected response'])
            else:
                self.Discard('Invalid Command for UpdateInputMute')

    def SetInputTestSignalGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        inputVal = qualifier['Input']

        if 5 <= int(inputVal) <= 8 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputTestSignalGainCmdString = 'ingn({0})={1}\r'.format(inputVal, str(value))
            self.__SetHelper('InputTestSignalGain', InputTestSignalGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputTestSignalGain')

    def UpdateInputTestSignalGain(self, value, qualifier):

        inputVal = qualifier['Input']

        if 5 <= int(inputVal) <= 8:
            InputTestSignalGainCmdString = 'ingn({0})?\r'.format(inputVal)
            res = self.__UpdateHelper('InputTestSignalGain', InputTestSignalGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('InputTestSignalGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputTestSignalGain')

    def SetLEC(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        LECCmdString = 'lecen={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LEC', LECCmdString, value, qualifier)

    def UpdateLEC(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        LECCmdString = 'lecen?\r'
        res = self.__UpdateHelper('LEC', LECCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('LEC', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

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
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMixBusLabelStatus')

    def SetNRFDepth(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueConstraints = {
            'Min': 6,
            'Max': 36
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            NRFDepthCmdString = 'nrfdep({0})={1}\r'.format(InputStates[qualifier['Input']], value)
            self.__SetHelper('NRFDepth', NRFDepthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNRFDepth')

    def UpdateNRFDepth(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        NRFDepthCmdString = 'nrfdep({0})?\r'.format(InputStates[qualifier['Input']])
        res = self.__UpdateHelper('NRFDepth', NRFDepthCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-2])
                self.WriteStatus('NRFDepth', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetNRFEnable(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        NRFEnableCmdString = 'nrfen({0})={1}\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('NRFEnable', NRFEnableCmdString, value, qualifier)

    def UpdateNRFEnable(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        NRFEnableCmdString = 'nrfen({0})?\r'.format(InputStates[qualifier['Input']])
        res = self.__UpdateHelper('NRFEnable', NRFEnableCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('NRFEnable', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetOutputCompressorMakeupGain(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 30
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Output']) <= 5:
            OutputCompressorMakeupGainCmdString = 'outcpmug({0})={1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('OutputCompressorMakeupGain', OutputCompressorMakeupGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputCompressorMakeupGain')

    def UpdateOutputCompressorMakeupGain(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 5:
            OutputCompressorMakeupGainCmdString = 'outcpmug({0})?\r'.format(qualifier['Output'])
            res = self.__UpdateHelper('OutputCompressorMakeupGain', OutputCompressorMakeupGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('OutputCompressorMakeupGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputCompressorMakeupGain')

    def SetOutputCompressorRatio(self, value, qualifier):

        ValueConstraints = {
            'Min': 0.0,
            'Max': 50.0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Output']) <= 5:
            OutputCompressorRatioCmdString = 'outcprat({0})={1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('OutputCompressorRatio', OutputCompressorRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputCompressorRatio')

    def UpdateOutputCompressorRatio(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 5:
            OutputCompressorRatioCmdString = 'outcprat({0})?\r'.format(qualifier['Output'])
            res = self.__UpdateHelper('OutputCompressorRatio', OutputCompressorRatioCmdString, value, qualifier)
            if res:
                try:
                    value = float(res[3:-2])
                    self.WriteStatus('OutputCompressorRatio', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputCompressorRatio')

    def SetOutputCompressorThresholdLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Output']) <= 5:
            OutputCompressorThresholdLevelCmdString = 'outcpthr({0})={1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('OutputCompressorThresholdLevel', OutputCompressorThresholdLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputCompressorThresholdLevel')

    def UpdateOutputCompressorThresholdLevel(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 5:
            OutputCompressorThresholdLevelCmdString = 'outcpthr({0})?\r'.format(qualifier['Output'])
            res = self.__UpdateHelper('OutputCompressorThresholdLevel', OutputCompressorThresholdLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('OutputCompressorThresholdLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputCompressorThresholdLevel')

    def SetOutputCompressorTimeConstant(self, value, qualifier):

        ValueConstraints = {
            'Min': 5,
            'Max': 10000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Output']) <= 5:
            OutputCompressorTimeConstantCmdString = 'outcptc({0})={1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('OutputCompressorTimeConstant', OutputCompressorTimeConstantCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputCompressorTimeConstant')

    def UpdateOutputCompressorTimeConstant(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 5:
            OutputCompressorTimeConstantCmdString = 'outcptc({0})?\r'.format(qualifier['Output'])
            res = self.__UpdateHelper('OutputCompressorTimeConstant', OutputCompressorTimeConstantCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('OutputCompressorTimeConstant', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputCompressorTimeConstant')

    def SetOutputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Output']) <= 5:
            OutputGainCmdString = 'outgn({0})={1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 5:
            OutputGainCmdString = 'outgn({0})?\r'.format(qualifier['Output'])
            res = self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[3:-2])
                    self.WriteStatus('OutputGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if qualifier['Output'] == 'All':
            OutputMuteCmdString = 'outmt(*)={{{0},{0},{0},{0},{0}}}\r'.format(ValueStateValues[value])
        elif 1 <= int(qualifier['Output']) <= 5:
            OutputMuteCmdString = 'outmt({0})={1}\r'.format(qualifier['Output'], ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetOutputMute')

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
                    self.Error(['Invalid/unexpected response'])
        elif 1 <= int(qualifier['Output']) <= 5:
            OutputMuteCmdString = 'outmt({0})?\r'.format(qualifier['Output'])
            res = self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[3:-2]]
                    self.WriteStatus('OutputMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def SetPhoneDirectoryNavigation(self, value, qualifier):

        if value == 'Up':
            self.phone_directory.scroll_up(1)
        elif value == 'Down':
            self.phone_directory.scroll_down(1)
        elif value == 'Page Up':
            self.phone_directory.scroll_up(self._NumberofPhoneDirectoryEntries)
        elif value == 'Page Down':
            self.phone_directory.scroll_down(self._NumberofPhoneDirectoryEntries)
        else:
            self.Discard('Invalid Command for SetPhoneDirectoryNavigation')

    def SetPhoneDirectoryResultSet(self, value, qualifier):

        value = qualifier['Entry']
        if 1 <= value <= self.NumberOfEntries:
            phone_entry = self.ReadStatus('PhoneDirectoryResults', {'Entry': value})
            if ':' in phone_entry:
                phoneNum = phone_entry.split(' : ')
                self.SetTelephoneDialCommand(phoneNum[1])
            else:
                self.Discard('Invalid Command for SetPhoneDirectoryResultSet')
        else:
            self.Discard('Invalid Command for SetPhoneDirectoryResultSet')

    def SetPhoneDirectoryStore(self, value, qualifier):

        address = qualifier['Address']
        phoneTitle = qualifier['Telephone Number Title']
        phoneNum = qualifier['Telephone Number']

        if address and phoneTitle and phoneNum and 1 <= address <= 32 and len(phoneTitle) <= 30 and len(phoneNum) <= 30:
            StoreTelephoneNumberString = 'telnbr({})=\"{}\"\r'.format(address, phoneNum)
            StoreTelephoneNumberTitleString = 'telnbrti({})=\"{}\"\r'.format(address, phoneTitle)
            self.__SetHelper('PhoneDirectoryStore', StoreTelephoneNumberString, value, qualifier)
            self.__SetHelper('PhoneDirectoryStore', StoreTelephoneNumberTitleString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhoneDirectoryStore')

    def SetPhoneDirectoryUpdate(self, value, qualifier):

        new_directory_data = []
        for address in range(32):
            TelephoneNumberUpdateString = 'telnbr({})?\r'.format(address + 1)
            TelephoneNumberTitleUpdateString = 'telnbrti({})?\r'.format(address + 1)
            phoneNum = self.__UpdateHelper('PhoneDirectoryUpdate', TelephoneNumberUpdateString, value, qualifier)
            phoneTitle = self.__UpdateHelper('PhoneDirectoryUpdate', TelephoneNumberTitleUpdateString, value, qualifier)
            if phoneNum and phoneTitle:
                try:
                    new_directory_data.append('{} : {}'.format(phoneTitle[4:-3], phoneNum[4:-3]))
                except IndexError:
                    self.Error(['Cannot find Phone Entry in response'])

        new_directory_data.append('*** End of List ***')
        self.phone_directory.reset(new_directory_data)

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

    def SetTelephoneAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        TelephoneAutoAnswerCmdString = 'telautoans={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('TelephoneAutoAnswer', TelephoneAutoAnswerCmdString, value, qualifier)

    def UpdateTelephoneAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        TelephoneAutoAnswerCmdString = 'telautoans?\r'
        res = self.__UpdateHelper('TelephoneAutoAnswer', TelephoneAutoAnswerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('TelephoneAutoAnswer', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetTelephoneAutoDisconnect(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        TelephoneAutoDisconnectCmdString = 'telautodis={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('TelephoneAutoDisconnect', TelephoneAutoDisconnectCmdString, value, qualifier)

    def UpdateTelephoneAutoDisconnect(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        TelephoneAutoDisconnectCmdString = 'telautodis?\r'
        res = self.__UpdateHelper('TelephoneAutoDisconnect', TelephoneAutoDisconnectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('TelephoneAutoDisconnect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetTelephoneConnectionChimeLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -12,
            'Max': 12
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TelephoneConnectionChimeLevelCmdString = 'telcchmlv={0}\r'.format(value)
            self.__SetHelper('TelephoneConnectionChimeLevel', TelephoneConnectionChimeLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTelephoneConnectionChimeLevel')

    def UpdateTelephoneConnectionChimeLevel(self, value, qualifier):

        TelephoneConnectionChimeLevelCmdString = 'telcchmlv?\r'
        res = self.__UpdateHelper('TelephoneConnectionChimeLevel', TelephoneConnectionChimeLevelCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-2])
                self.WriteStatus('TelephoneConnectionChimeLevel', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetTelephoneLineConnectionStatus(self, value, qualifier):

        ValueStateValues = {
            'On-Hook': '0',
            'Off-Hook': '1'
        }

        TelephoneLineConnectionStatusCmdString = 'telconn={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('TelephoneLineConnectionStatus', TelephoneLineConnectionStatusCmdString, value, qualifier)

    def UpdateTelephoneLineConnectionStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'On-Hook',
            '1': 'Off-Hook'
        }

        TelephoneLineConnectionStatusCmdString = 'telconn?\r'
        res = self.__UpdateHelper('TelephoneLineConnectionStatus', TelephoneLineConnectionStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('TelephoneLineConnectionStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetTelephoneDialCommand(self, value, qualifier):

        cmdstring = value
        TelephoneDialCommandCmdString = 'teldial=\"{0}\"\r'.format(cmdstring)
        self.__SetHelper('TelephoneDialCommand', TelephoneDialCommandCmdString, value, qualifier)

    def SetTelephoneDialingSpeed(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        TelephoneDialingSpeedCmdString = 'teldialspd={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('TelephoneDialingSpeed', TelephoneDialingSpeedCmdString, value, qualifier)

    def UpdateTelephoneDialingSpeed(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        TelephoneDialingSpeedCmdString = 'teldialspd?\r'
        res = self.__UpdateHelper('TelephoneDialingSpeed', TelephoneDialingSpeedCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('TelephoneDialingSpeed', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetTelephoneDTMF(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '*': '*',
            '#': '#',
            'A': 'A',
            'B': 'B',
            'C': 'C',
            'D': 'D'
        }

        TelephoneDTMFCmdString = 'teldtmf=\"{0}\"\r'.format(ValueStateValues[value])
        self.__SetHelper('TelephoneDTMF', TelephoneDTMFCmdString, value, qualifier)

    def SetTelephoneDTMFLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -6,
            'Max': 6
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TelephoneDTMFLevelCmdString = 'teldtmflv={0}\r'.format(value)
            self.__SetHelper('TelephoneDTMFLevel', TelephoneDTMFLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTelephoneDTMFLevel')

    def UpdateTelephoneDTMFLevel(self, value, qualifier):

        TelephoneDTMFLevelCmdString = 'teldtmflv?\r'
        res = self.__UpdateHelper('TelephoneDTMFLevel', TelephoneDTMFLevelCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-2])
                self.WriteStatus('TelephoneDTMFLevel', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetTelephoneHookFlash(self, value, qualifier):

        TelephoneHookFlashCmdString = 'telflash\r'
        self.__SetHelper('TelephoneHookFlash', TelephoneHookFlashCmdString, value, qualifier)

    def UpdateTelephoneIncomingCallStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'True',
            '0': 'False'
        }

        TelephoneIncomingCallStatusCmdString = 'telringing?\r'
        res = self.__UpdateHelper('TelephoneIncomingCallStatus', TelephoneIncomingCallStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('TelephoneIncomingCallStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetTelephonePrivacy(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        TelephonePrivacyCmdString = 'telpriv={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('TelephonePrivacy', TelephonePrivacyCmdString, value, qualifier)

    def UpdateTelephonePrivacy(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        TelephonePrivacyCmdString = 'telpriv?\r'
        res = self.__UpdateHelper('TelephonePrivacy', TelephonePrivacyCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('TelephonePrivacy', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetTelephonePrivacyMode(self, value, qualifier):

        ValueStateValues = {
            'Only Mute Transmit Audio': '1',
            'Only Mute Receive Audio': '2',
            'Mute Both Transmit and Receive Audio': '3'
        }

        TelephonePrivacyModeCmdString = 'telprivmod={0}\r'.format(ValueStateValues[value])
        self.__SetHelper('TelephonePrivacyMode', TelephonePrivacyModeCmdString, value, qualifier)

    def UpdateTelephonePrivacyMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Only Mute Transmit Audio',
            '2': 'Only Mute Receive Audio',
            '3': 'Mute Both Transmit and Receive Audio'
        }

        TelephonePrivacyModeCmdString = 'telprivmod?\r'
        res = self.__UpdateHelper('TelephonePrivacyMode', TelephonePrivacyModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-2]]
                self.WriteStatus('TelephonePrivacyMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetTelephoneRedial(self, value, qualifier):

        TelephoneRedialCmdString = 'telredial\r'
        self.__SetHelper('TelephoneRedial', TelephoneRedialCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response.find('ERROR') >= 0:
                self.Error(['{0}{1}'.format(sourceCmdName, ': Error Command Reply')])
                response = ''
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

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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


def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_module()
        return res

    return wrapper


class Directory:
    def __init__(self, display_count, write_function_name, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Entry'
        self._qualifier_type = 'Number'
        self._write_function_name = write_function_name

        self.entry_list = []

        self._start_index = 0
        self.auto_update = True
        self.filler = filler
        self.entry_function = lambda entry: entry

    @property
    def display_count(self):
        return self._display_count

    @property
    def qualifier_type(self):
        return self._qualifier_type

    @qualifier_type.setter
    def qualifier_type(self, value):
        if value in ('Enum', 'Number'):
            self._qualifier_type = value

    def write_to_module(self):

        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Number':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            self.write_status_function(self._write_function_name, self.entry_function(entry[0]), {self.qualifier_name: position_value})

    def write_status_function(self, value, qualifier, context):
        pass

    @UseAutoUpdate
    def add_entry(self, entry):
        if isinstance(entry, list):
            self.entry_list.extend(entry)
        else:
            self.entry_list.append(entry)

    @UseAutoUpdate
    def reset(self, newEntries=None):
        if isinstance(newEntries, list):
            self.entry_list.clear()
            self.entry_list.extend(newEntries)
        else:
            self.entry_list.clear()
        self._start_index = 0

    @UseAutoUpdate
    def remove_entry(self, display_position):

        if self.__display_position_check(display_position):
            try:
                return self.entry_list.pop(self._start_index + display_position - 1)
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_entry(self, display_position):

        if self.__display_position_check(display_position):
            try:
                return self.entry_list[self._start_index + display_position - 1]
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_displayed_entries(self):

        index = self._start_index
        while index <= self._start_index + self._display_count - 1:
            if index >= len(self.entry_list):
                yield self.filler, index + 1
            else:
                yield self.entry_list[index], index + 1
            index += 1

    def __display_position_check(self, position):

        return 0 < position <= self._display_count

    @UseAutoUpdate
    def scroll_up(self, step=1):
        if self._start_index - step >= 0:
            self._start_index -= step
        else:
            self._start_index = 0

    @UseAutoUpdate
    def scroll_down(self, step=1):
        if self._start_index + step < len(self.entry_list):
            self._start_index += step
        else:
            self._start_index = len(self.entry_list) - 1  # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1
