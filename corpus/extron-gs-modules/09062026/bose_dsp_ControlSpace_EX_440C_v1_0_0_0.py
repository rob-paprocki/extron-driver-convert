from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from collections import defaultdict

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
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AECCNEnable': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AECEnable': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AECInternalMute': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AECNLPControl': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AECNRLevel': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AECReference': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGainSharingAttack': {'Parameters':['Name'], 'Status': {}},
            'AMMGainSharingBypass': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGainSharingDecay': {'Parameters':['Name'], 'Status': {}},
            'AMMGainSharingGain': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGainSharingHold': {'Parameters':['Name'], 'Status': {}},
            'AMMGainSharingMute': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGainSharingPriority': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGainSharingRMSAverage': {'Parameters':['Name','Type'], 'Status': {}},
            'AMMGainSharingSlope': {'Parameters':['Name'], 'Status': {}},
            'AMMGatedAttack': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedDecay': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedDuckingDepth': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedGain': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedGateDepth': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedHighPass': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedHold': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedLowPass': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedMute': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedPriority': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedRMSAvg': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMMGatedThreshold': {'Parameters':['Name','Index 1'], 'Status': {}},
            'AMPLinkLevel': {'Parameters':['Channel'], 'Status': {}},
            'AMPLinkMute': {'Parameters':['Channel'], 'Status': {}},
            'AMPLinkPolarity': {'Parameters':['Channel'], 'Status': {}},
            'ArrayEQAdvanced': {'Parameters':['Name'], 'Status': {}},
            'ArrayEQCenterFrequency': {'Parameters':['Name'], 'Status': {}},
            'ArrayEQTilt': {'Parameters':['Name'], 'Status': {}},
            'ArrayEQVerticalAngle': {'Parameters':['Name'], 'Status': {}},
            'CompressorLimiterInputDetect': {'Parameters':['Name'], 'Status': {}},
            'CompressorLimiterRatio': {'Parameters':['Name'], 'Status': {}},
            'CompressorLimiterRelease': {'Parameters':['Name'], 'Status': {}},
            'CrossoverFilter': {'Parameters':['Name','Index 1','Type'], 'Status': {}},
            'CrossoverFrequency': {'Parameters':['Name','Index 1','Type'], 'Status': {}},
            'CrossoverMute': {'Parameters':['Name','Index 1','Type'], 'Status': {}},
            'CrossoverPolarity': {'Parameters':['Name','Index 1','Type'], 'Status': {}},
            'CRRAdvancedLevel': {'Parameters':['Name','Input','Output'], 'Status': {}},
            'CRRAdvancedState': {'Parameters':['Name','Input','Output'], 'Status': {}},
            'DelayBypass': {'Parameters':['Name','Output'], 'Status': {}},
            'DelayTime': {'Parameters':['Name','Output'], 'Status': {}},
            'DuckerDecay': {'Parameters':['Name'], 'Status': {}},
            'DuckerHold': {'Parameters':['Name'], 'Status': {}},
            'DuckerRange': {'Parameters':['Name'], 'Status': {}},
            'Gain': {'Parameters':['Name'], 'Status': {}},
            'GainMute': {'Parameters':['Name'], 'Status': {}},
            'GateDecay': {'Parameters':['Name'], 'Status': {}},
            'GateDetector': {'Parameters':['Name'], 'Status': {}},
            'GateHold': {'Parameters':['Name'], 'Status': {}},
            'GateRange': {'Parameters':['Name'], 'Status': {}},
            'GPOMode': {'Parameters':['Name','Pin'], 'Status': {}},
            'GraphicEQLevel': {'Parameters':['Name','Frequency'], 'Status': {}},
            'GroupLevel': {'Parameters':['Group'], 'Status': {}},
            'GroupMute': {'Parameters':['Group'], 'Status': {}},
            'MatrixMixerLevel': {'Parameters':['Name','Input','Output','Matrix Size'], 'Status': {}},
            'MatrixMixerState': {'Parameters':['Name','Input','Output','Matrix Size'], 'Status': {}},
            'ParameterRecall': { 'Status': {}},
            'ParametricEQFrequency': {'Parameters':['Name','Band'], 'Status': {}},
            'ParametricEQGain': {'Parameters':['Name','Band'], 'Status': {}},
            'ParametricEQQ': {'Parameters':['Name','Band'], 'Status': {}},
            'ParametricEQSlope': {'Parameters':['Name','Band'], 'Status': {}},
            'ParametricEQType': {'Parameters':['Name','Band'], 'Status': {}},
            'PeakRMSInputDetect': {'Parameters':['Name'], 'Status': {}},
            'PeakRMSRMS': {'Parameters':['Name','Function'], 'Status': {}},
            'PSTNAction': {'Parameters':['Name', 'Dial String'], 'Status': {}},
            'PSTNCallActive': {'Parameters':['Name'], 'Status': {}},
            'PSTNCallerID': {'Parameters':['Name','Type'], 'Status': {}},
            'PSTNCallStatus': {'Parameters':['Name'], 'Status': {}},
            'PSTNDialKey': {'Parameters':['Name'], 'Status': {}},
            'PSTNHook': {'Parameters':['Name'], 'Status': {}},
            'PSTNLevel': {'Parameters':['Module','Name'], 'Status': {}},
            'PSTNMute': {'Parameters':['Module','Name'], 'Status': {}},
            'RouterInputSelect': {'Parameters':['Name','Output'], 'Status': {}},
            'SignalGeneratorGain': {'Parameters':['Name','Wave'], 'Status': {}},
            'SignalGeneratorMute': {'Parameters':['Name','Wave'], 'Status': {}},
            'SourceSelect': {'Parameters':['Name'], 'Status': {}},
            'SpeakerParametricAlignDelay': {'Parameters':['Name'], 'Status': {}},
            'SpeakerParametricBypass': {'Parameters':['Name','Type'], 'Status': {}},
            'SpeakerParametricEQBandBypass': {'Parameters':['Name','Index 1'], 'Status': {}},
            'SpeakerParametricEQBandFilter': {'Parameters':['Name','Index 1'], 'Status': {}},
            'SpeakerParametricEQBandFrequency': {'Parameters':['Name','Index 1'], 'Status': {}},
            'SpeakerParametricEQBandGain': {'Parameters':['Name','Index 1'], 'Status': {}},
            'SpeakerParametricEQBandQ': {'Parameters':['Name','Index 1'], 'Status': {}},
            'SpeakerParametricFilter': {'Parameters':['Name','Type'], 'Status': {}},
            'SpeakerParametricFrequency': {'Parameters':['Name','Type'], 'Status': {}},
            'SpeakerParametricGain': {'Parameters':['Name'], 'Status': {}},
            'StandardMixerLevel': {'Parameters':['Name','Index 1','Index 2'], 'Status': {}},
            'StandardMixerMute': {'Parameters':['Name','Index 1','Index 2'], 'Status': {}},
            'StandardMixerRouting': {'Parameters':['Name','Input','Output'], 'Status': {}},
            'ToneControlGain': {'Parameters':['Name','Type'], 'Status': {}},
            'USBLevel': {'Parameters':['Name','Channel'], 'Status': {}},
            'USBMute': {'Parameters':['Name','Channel'], 'Status': {}},
            'VoIPAction': {'Parameters':['Name', 'Dial String'], 'Status': {}},
            'VoIPCallActive': {'Parameters':['Name'], 'Status': {}},
            'VoIPCallerID': {'Parameters':['Name','Type'], 'Status': {}},
            'VoIPCallStatus': {'Parameters':['Name'], 'Status': {}},
            'VoIPDialKey': {'Parameters':['Name'], 'Status': {}},
            'VoIPLevel': {'Parameters':['Name'], 'Status': {}},
            'VoIPMute': {'Parameters':['Name'], 'Status': {}},
            }


        self.lastPTSNCallerIDUpdate = defaultdict(float)
        self.lastVoIPCallerIDUpdate = defaultdict(float)

        self.set_regex = re.compile(b'\x06|\x15(?:01|02|03|99)')
        self.get_regex = re.compile(b'.+\r|\x15(?:01|02|03|99)')
        self.pattern = re.compile('GA.+=(.*);?\r')


    def parse(self, response):
        if response:
            data = self.pattern.search(response)
            if data:
                return data.group(1).strip().strip(';')
            return response    
        
    def SetAECCNEnable(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 1 <= int(index1) <= 8 and value in ValueStateValues:
            AECCNEnableCmdString = 'SA"{}">{}>8={}\r'.format(name, index1, ValueStateValues[value])
            self.__SetHelper('AECCNEnable', AECCNEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAECCNEnable')

    def UpdateAECCNEnable(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 1 <= int(index1) <= 8:
            AECCNEnableCmdString = 'GA"{}">{}>8\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AECCNEnable', AECCNEnableCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AECCNEnable', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AEC CN Enable: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAECCNEnable')

    def SetAECEnable(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 1 <= int(index1) <= 8 and value in ValueStateValues:
            AECEnableCmdString = 'SA"{}">{}>6={}\r'.format(name, index1, ValueStateValues[value])
            self.__SetHelper('AECEnable', AECEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAECEnable')

    def UpdateAECEnable(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 1 <= int(index1) <= 8:
            AECEnableCmdString = 'GA"{}">{}>6\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AECEnable', AECEnableCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AECEnable', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AEC Enable: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAECEnable')

    def SetAECInternalMute(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 1 <= int(index1) <= 8 and value in ValueStateValues:
            AECInternalMuteCmdString = 'SA"{}">{}>5={}\r'.format(name, index1, ValueStateValues[value])
            self.__SetHelper('AECInternalMute', AECInternalMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAECInternalMute')

    def UpdateAECInternalMute(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 1 <= int(index1) <= 8:
            AECInternalMuteCmdString = 'GA"{}">{}>5\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AECInternalMute', AECInternalMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AECInternalMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AEC Internal Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAECInternalMute')

    def SetAECNLPControl(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'Light':    '1',
            'Medium':   '2',
            'Strong':   '3'
        }

        if name and 1 <= int(index1) <= 8 and value in ValueStateValues:
            AECNLPControlCmdString = 'SA"{}">{}>7={}\r'.format(name, index1, ValueStateValues[value])
            self.__SetHelper('AECNLPControl', AECNLPControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAECNLPControl')

    def UpdateAECNLPControl(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            '1': 'Light',
            '2': 'Medium',
            '3': 'Strong'
        }

        if name and 1 <= int(index1) <= 8:
            AECNLPControlCmdString = 'GA"{}">{}>7\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AECNLPControl', AECNLPControlCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AECNLPControl', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AEC NLP Control: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAECNLPControl')

    def SetAECNRLevel(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 8 and 0 <= value <= 24:
            AECNRLevelCmdString = 'SA"{}">{}>9={}\r'.format(name, index1, value)
            self.__SetHelper('AECNRLevel', AECNRLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAECNRLevel')

    def UpdateAECNRLevel(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 8:
            AECNRLevelCmdString = 'GA"{}">{}>9\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AECNRLevel', AECNRLevelCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('AECNRLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AEC NR Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAECNRLevel')

    def UpdateAECReference(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        if name and 1 <= int(index1) <= 8:
            AECReferenceCmdString = 'GA"{}">{}>10\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AECReference', AECReferenceCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AECReference', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AEC Reference: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAECReference')

    def SetAMMGainSharingAttack(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if name and 0.5 <= value <= 100.0:
            AMMGainSharingAttackCmdString = 'SA"{}">0>4={:.1f}\r'.format(name, value)
            self.__SetHelper('AMMGainSharingAttack', AMMGainSharingAttackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGainSharingAttack')

    def UpdateAMMGainSharingAttack(self, value, qualifier):

        name = qualifier['Name']

        if name:
            AMMGainSharingAttackCmdString = 'GA"{}">0>4\r'.format(name)
            res = self.parse(self.__UpdateHelper('AMMGainSharingAttack', AMMGainSharingAttackCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('AMMGainSharingAttack', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gain Sharing Attack: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGainSharingAttack')

    def SetAMMGainSharingBypass(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 1 <= int(index1) <= 32 and value in ValueStateValues:
            AMMGainSharingBypassCmdString = 'SA"{}">{}>4={}\r'.format(name, index1, ValueStateValues[value])
            self.__SetHelper('AMMGainSharingBypass', AMMGainSharingBypassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGainSharingBypass')

    def UpdateAMMGainSharingBypass(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 1 <= int(index1) <= 32:
            AMMGainSharingBypassCmdString = 'GA"{}">{}>4\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGainSharingBypass', AMMGainSharingBypassCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AMMGainSharingBypass', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AMM Gain Sharing Bypass: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGainSharingBypass')

    def SetAMMGainSharingDecay(self, value, qualifier):

        name = qualifier['Name']

        if name and 5 <= value <= 50000:
            AMMGainSharingDecayCmdString = 'SA"{}">0>6={}\r'.format(name, value)
            self.__SetHelper('AMMGainSharingDecay', AMMGainSharingDecayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGainSharingDecay')

    def UpdateAMMGainSharingDecay(self, value, qualifier):

        name = qualifier['Name']

        if name:
            AMMGainSharingDecayCmdString = 'GA"{}">0>6\r'.format(name)
            res = self.parse(self.__UpdateHelper('AMMGainSharingDecay', AMMGainSharingDecayCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('AMMGainSharingDecay', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gain Sharing Decay: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGainSharingDecay')

    def SetAMMGainSharingGain(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        value = float('{:.1f}'.format(value))

        if name and 0 <= int(index1) <= 32 and -60.5 <= value <= 12.0:
            AMMGainSharingGainCmdString = 'SA"{}">{}>1={:.1f}\r'.format(name, index1, value)
            self.__SetHelper('AMMGainSharingGain', AMMGainSharingGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGainSharingGain')

    def UpdateAMMGainSharingGain(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 0 <= int(index1) <= 32:
            AMMGainSharingGainCmdString = 'GA"{}">{}>1\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGainSharingGain', AMMGainSharingGainCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('AMMGainSharingGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gain Sharing Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGainSharingGain')

    def SetAMMGainSharingHold(self, value, qualifier):

        name = qualifier['Name']

        if name and 0 <= value <= 1000:
            AMMGainSharingHoldCmdString = 'SA"{}">0>5={}\r'.format(name, value)
            self.__SetHelper('AMMGainSharingHold', AMMGainSharingHoldCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGainSharingHold')

    def UpdateAMMGainSharingHold(self, value, qualifier):

        name = qualifier['Name']

        if name:
            AMMGainSharingHoldCmdString = 'GA"{}">0>5\r'.format(name)
            res = self.parse(self.__UpdateHelper('AMMGainSharingHold', AMMGainSharingHoldCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('AMMGainSharingHold', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gain Sharing Hold: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGainSharingHold')

    def SetAMMGainSharingMute(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 0 <= int(index1) <= 32 and value in ValueStateValues:
            AMMGainSharingMuteCmdString = 'SA"{}">{}>2={}\r'.format(name, index1, ValueStateValues[value])
            self.__SetHelper('AMMGainSharingMute', AMMGainSharingMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGainSharingMute')

    def UpdateAMMGainSharingMute(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 0 <= int(index1) <= 32:
            AMMGainSharingMuteCmdString = 'GA"{}">{}>2\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGainSharingMute', AMMGainSharingMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AMMGainSharingMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AMM Gain Sharing Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGainSharingMute')

    def SetAMMGainSharingPriority(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        if name and 1 <= int(index1) <= 32 and value in ValueStateValues:
            AMMGainSharingPriorityCmdString = 'SA"{}">{}>3={}\r'.format(name, index1, ValueStateValues[value])
            self.__SetHelper('AMMGainSharingPriority', AMMGainSharingPriorityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGainSharingPriority')

    def UpdateAMMGainSharingPriority(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        if name and 1 <= int(index1) <= 32:
            AMMGainSharingPriorityCmdString = 'GA"{}">{}>3\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGainSharingPriority', AMMGainSharingPriorityCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AMMGainSharingPriority', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AMM Gain Sharing Priority: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGainSharingPriority')

    def SetAMMGainSharingRMSAverage(self, value, qualifier):

        name = qualifier['Name']
        _type = qualifier['Type']

        TypeStates = {
            'Input':    '7',
            'Output':   '8'
        }

        if name and _type in TypeStates and 1 <= value <= 500:
            AMMGainSharingRMSAverageCmdString = 'SA"{}">0>{}={}\r'.format(name, TypeStates[_type], value)
            self.__SetHelper('AMMGainSharingRMSAverage', AMMGainSharingRMSAverageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGainSharingRMSAverage')

    def UpdateAMMGainSharingRMSAverage(self, value, qualifier):

        name = qualifier['Name']
        _type = qualifier['Type']

        TypeStates = {
            'Input':    '7',
            'Output':   '8'
        }

        if name and _type in TypeStates:
            AMMGainSharingRMSAverageCmdString = 'GA"{}">0>{}\r'.format(name, TypeStates[_type])
            res = self.parse(self.__UpdateHelper('AMMGainSharingRMSAverage', AMMGainSharingRMSAverageCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('AMMGainSharingRMSAverage', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gain Sharing RMS Average: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGainSharingRMSAverage')


    def SetAMMGainSharingSlope(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.2f}'.format(value))

        if name and 0.01 <= value <= 2.00:
            AMMGainSharingSlopeCmdString = 'SA"{}">0>3={:.2f}\r'.format(name, value)
            self.__SetHelper('AMMGainSharingSlope', AMMGainSharingSlopeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGainSharingSlope')

    def UpdateAMMGainSharingSlope(self, value, qualifier):

        name = qualifier['Name']

        if name:
            AMMGainSharingSlopeCmdString = 'GA"{}">0>3\r'.format(name)
            res = self.parse(self.__UpdateHelper('AMMGainSharingSlope', AMMGainSharingSlopeCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.2f}'.format(float(res)))
                    self.WriteStatus('AMMGainSharingSlope', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gain Sharing Slope: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGainSharingSlope')

    def SetAMMGatedAttack(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        value = float('{:.1f}'.format(value))

        if name and 1 <= int(index1) <= 32 and 0.5 <= value <= 500.0:
            AMMGatedAttackCmdString = 'SA"{}">{}>14={:.1f}\r'.format(name, index1, value)
            self.__SetHelper('AMMGatedAttack', AMMGatedAttackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedAttack')

    def UpdateAMMGatedAttack(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32:
            AMMGatedAttackCmdString = 'GA"{}">{}>14\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedAttack', AMMGatedAttackCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('AMMGatedAttack', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gated Attack: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedAttack')

    def SetAMMGatedDecay(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32 and 1 <= value <= 50000:
            AMMGatedDecayCmdString = 'SA"{}">{}>16={}\r'.format(name, index1, value)
            self.__SetHelper('AMMGatedDecay', AMMGatedDecayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedDecay')

    def UpdateAMMGatedDecay(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32:
            AMMGatedDecayCmdString = 'GA"{}">{}>16\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedDecay', AMMGatedDecayCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('AMMGatedDecay', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gated Decay: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedDecay')

    def SetAMMGatedDuckingDepth(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        value = float('{:.1f}'.format(value))

        if name and 1 <= int(index1) <= 32 and -60 <= value <= 0:
            AMMGatedDuckingDepthCmdString = 'SA"{}">{}>12={:.1f}\r'.format(name, index1, value)
            self.__SetHelper('AMMGatedDuckingDepth', AMMGatedDuckingDepthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedDuckingDepth')

    def UpdateAMMGatedDuckingDepth(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32:
            AMMGatedDuckingDepthCmdString = 'GA"{}">{}>12\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedDuckingDepth', AMMGatedDuckingDepthCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('AMMGatedDuckingDepth', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gated Ducking Depth: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedDuckingDepth')

    def SetAMMGatedGain(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        value = float('{:.1f}'.format(value))

        if name and 0 <= int(index1) <= 32 and -60.5 <= value <= 12.0:
            if index1 == '0':
                AMMGatedGainCmdString = 'SA"{}">0>1={:.1f}\r'.format(name, value)
            else:
                AMMGatedGainCmdString = 'SA"{}">{}>2={:.1f}\r'.format(name, index1, value)

            self.__SetHelper('AMMGatedGain', AMMGatedGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedGain')

    def UpdateAMMGatedGain(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 0 <= int(index1) <= 32:
            if index1 == '0':
                AMMGatedGainCmdString = 'GA"{}">0>1\r'.format(name)
            else:
                AMMGatedGainCmdString = 'GA"{}">{}>2\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedGain', AMMGatedGainCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('AMMGatedGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gated Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedGain')

    def SetAMMGatedGateDepth(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        value = float('{:.1f}'.format(value))

        if name and 1 <= int(index1) <= 32 and -70 <= value <= 0:
            AMMGatedGateDepthCmdString = 'SA"{}">{}>13={:.1f}\r'.format(name, index1, value)
            self.__SetHelper('AMMGatedGateDepth', AMMGatedGateDepthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedGateDepth')

    def UpdateAMMGatedGateDepth(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32:
            AMMGatedGateDepthCmdString = 'GA"{}">{}>13\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedGateDepth', AMMGatedGateDepthCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('AMMGatedGateDepth', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gated Gate Depth: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedGateDepth')

    def SetAMMGatedHighPass(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32 and 20 <= value <= 20000:
            value = float('{:.1f}'.format(value))
            AMMGatedHighPassCmdString = 'SA"{}">{}>10={:.1f}\r'.format(name, index1, value)
            self.__SetHelper('AMMGatedHighPass', AMMGatedHighPassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedHighPass')

    def UpdateAMMGatedHighPass(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32:
            AMMGatedHighPassCmdString = 'GA"{}">{}>10\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedHighPass', AMMGatedHighPassCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('AMMGatedHighPass', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gated High Pass: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedHighPass')

    def SetAMMGatedHold(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32 and 1 <= value <= 50000:
            AMMGatedHoldCmdString = 'SA"{}">{}>15={}\r'.format(name, index1, value)
            self.__SetHelper('AMMGatedHold', AMMGatedHoldCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedHold')

    def UpdateAMMGatedHold(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32:
            AMMGatedHoldCmdString = 'GA"{}">{}>15\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedHold', AMMGatedHoldCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('AMMGatedHold', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gated Hold: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedHold')

    def SetAMMGatedLowPass(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32 and 20 <= value <= 20000:
            value = float('{:.1f}'.format(value))
            AMMGatedLowPassCmdString = 'SA"{}">{}>9={:.1f}\r'.format(name, index1, value)
            self.__SetHelper('AMMGatedLowPass', AMMGatedLowPassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedLowPass')

    def UpdateAMMGatedLowPass(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32:
            AMMGatedLowPassCmdString = 'GA"{}">{}>9\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedLowPass', AMMGatedLowPassCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('AMMGatedLowPass', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gated Low Pass: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedLowPass')

    def SetAMMGatedMute(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 0 <= int(index1) <= 32 and value in ValueStateValues:
            if index1 == '0':
                AMMGatedMuteCmdString = 'SA"{}">0>2={}\r'.format(name, ValueStateValues[value])
            else:
                AMMGatedMuteCmdString = 'SA"{}">{}>3={}\r'.format(name, index1, ValueStateValues[value])

            self.__SetHelper('AMMGatedMute', AMMGatedMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedMute')

    def UpdateAMMGatedMute(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 0 <= int(index1) <= 32:
            if index1 == '0':
                AMMGatedMuteCmdString = 'GA"{}">0>2\r'.format(name)
            else:
                AMMGatedMuteCmdString = 'GA"{}">{}>3\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedMute', AMMGatedMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AMMGatedMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AMM Gated Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedMute')

    def SetAMMGatedPriority(self, value, qualifier):

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32 and value in ValueStateValues:
            AMMGatedPriorityCmdString = 'SA"{}">{}>1={}\r'.format(name, index1, ValueStateValues[value])
            self.__SetHelper('AMMGatedPriority', AMMGatedPriorityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedPriority')

    def UpdateAMMGatedPriority(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32:
            AMMGatedPriorityCmdString = 'GA"{}">{}>1\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedPriority', AMMGatedPriorityCmdString, value, qualifier))
            if res:
                try:
                    value = str(int(res))
                    self.WriteStatus('AMMGatedPriority', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AMM Gated Priority: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedPriority')

    def SetAMMGatedRMSAvg(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32 and 1 <= value <= 1000:
            AMMGatedRMSAvgCmdString = 'SA"{}">{}>11={}\r'.format(name, index1, value)
            self.__SetHelper('AMMGatedRMSAvg', AMMGatedRMSAvgCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedRMSAvg')

    def UpdateAMMGatedRMSAvg(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32:
            AMMGatedRMSAvgCmdString = 'GA"{}">{}>11\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedRMSAvg', AMMGatedRMSAvgCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('AMMGatedRMSAvg', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gated RMS Avg: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedRMSAvg')

    def SetAMMGatedThreshold(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        value = float('{:.1f}'.format(value))

        if name and 1 <= int(index1) <= 32 and -80.0 <= value <= 0:
            AMMGatedThresholdCmdString = 'SA"{}">{}>5={:.1f}\r'.format(name, index1, value)
            self.__SetHelper('AMMGatedThreshold', AMMGatedThresholdCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMMGatedThreshold')

    def UpdateAMMGatedThreshold(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 32:
            AMMGatedThresholdCmdString = 'GA"{}">{}>5\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('AMMGatedThreshold', AMMGatedThresholdCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('AMMGatedThreshold', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMM Gated Threshold: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMMGatedThreshold')

    def SetAMPLinkLevel(self, value, qualifier):
        
        channel = int(qualifier['Channel'])
        value = float('{:.1f}'.format(value))

        if 1 <= channel <= 4 and -60.5 <= value <= 12:
            AMPLinkLevelCmdString = 'SA"AMPLink-Ch {}">1={:.1f}\r'.format(channel, value)
            self.__SetHelper('AMPLinkLevel', AMPLinkLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMPLinkLevel')

    def UpdateAMPLinkLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= 4:
            AMPLinkLevelCmdString = 'GA"AMPLink-Ch {}">1\r'.format(channel)
            res = self.parse(self.__UpdateHelper('AMPLinkLevel', AMPLinkLevelCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('AMPLinkLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['AMPLink Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMPLinkLevel')

    def SetAMPLinkMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'O', 
            'Off' : 'F'
        }
        channel = int(qualifier['Channel'])

        if 1 <= channel <= 4 and value in ValueStateValues:
            AMPLinkMuteCmdString = 'SA"AMPLink-Ch {}">2={}\r'.format(channel, ValueStateValues[value])
            self.__SetHelper('AMPLinkMute', AMPLinkMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMPLinkMute')

    def UpdateAMPLinkMute(self, value, qualifier):

        ValueStateValues = {
            'O' : 'On', 
            'F' : 'Off'
        }
        channel = int(qualifier['Channel'])
        if 1 <= channel <= 4:
            AMPLinkMuteCmdString = 'GA"AMPLink-Ch {}">2\r'.format(channel)
            res = self.parse(self.__UpdateHelper('AMPLinkMute', AMPLinkMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AMPLinkMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AMPLink Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAMPLinkMute')

    def SetAMPLinkPolarity(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'O', 
            'Off' : 'F'
        }
        channel = int(qualifier['Channel'])

        if 1 <= channel <= 4 and value in ValueStateValues:
            AMPLinkPolarityCmdString = 'SA"AMPLink-Ch {}">3={}\r'.format(channel, ValueStateValues[value])
            self.__SetHelper('AMPLinkPolarity', AMPLinkPolarityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAMPLinkPolarity')

    def UpdateAMPLinkPolarity(self, value, qualifier):

        ValueStateValues = {
            'O' : 'On', 
            'F' : 'Off'
        }
        channel = int(qualifier['Channel'])
        if 1 <= channel <= 4:
            AMPLinkPolarityCmdString = 'GA"AMPLink-Ch {}">3\r'.format(channel)
            res = self.parse(self.__UpdateHelper('AMPLinkPolarity', AMPLinkPolarityCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('AMPLinkPolarity', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AMPLink Polarity: Invalid/unexpected response'])
            else:
                self.Discard('Invalid Command for UpdateAMPLinkPolarity')

    def SetArrayEQAdvanced(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and value in ValueStateValues:
            ArrayEQAdvancedCmdString = 'SA"{}">1>6={}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('ArrayEQAdvanced', ArrayEQAdvancedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetArrayEQAdvanced')

    def UpdateArrayEQAdvanced(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name:
            ArrayEQAdvancedCmdString = 'GA"{}">1>6\r'.format(name)
            res = self.parse(self.__UpdateHelper('ArrayEQAdvanced', ArrayEQAdvancedCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('ArrayEQAdvanced', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Array EQ Advanced: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateArrayEQAdvanced')

    def SetArrayEQCenterFrequency(self, value, qualifier):

        name = qualifier['Name']

        if name and 100 <= value <= 4000:
            ArrayEQCenterFrequencyCmdString = 'SA"{}">1>1={}\r'.format(name, value)
            self.__SetHelper('ArrayEQCenterFrequency', ArrayEQCenterFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetArrayEQCenterFrequency')

    def UpdateArrayEQCenterFrequency(self, value, qualifier):

        name = qualifier['Name']

        if name:
            ArrayEQCenterFrequencyCmdString = 'GA"{}">1>1\r'.format(name)
            res = self.parse(self.__UpdateHelper('ArrayEQCenterFrequency', ArrayEQCenterFrequencyCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('ArrayEQCenterFrequency', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Array EQ Center Frequency: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateArrayEQCenterFrequency')

    def SetArrayEQTilt(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if name and 0.1 <= value <= 10.0:
            ArrayEQTiltCmdString = 'SA"{}">1>2={:.1f}\r'.format(name, value)
            self.__SetHelper('ArrayEQTilt', ArrayEQTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetArrayEQTilt')

    def UpdateArrayEQTilt(self, value, qualifier):

        name = qualifier['Name']

        if name:
            ArrayEQTiltCmdString = 'GA"{}">1>2\r'.format(name)
            res = self.parse(self.__UpdateHelper('ArrayEQTilt', ArrayEQTiltCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('ArrayEQTilt', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Array EQ Tilt: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateArrayEQTilt')

    def SetArrayEQVerticalAngle(self, value, qualifier):

        name = qualifier['Name']

        if name and 20 <= value <= 100:
            ArrayEQVerticalAngleCmdString = 'SA"{}">1>8={}\r'.format(name, value)
            self.__SetHelper('ArrayEQVerticalAngle', ArrayEQVerticalAngleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetArrayEQVerticalAngle')

    def UpdateArrayEQVerticalAngle(self, value, qualifier):

        name = qualifier['Name']

        if name:
            ArrayEQVerticalAngleCmdString = 'GA"{}">1>8\r'.format(name)
            res = self.parse(self.__UpdateHelper('ArrayEQVerticalAngle', ArrayEQVerticalAngleCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('ArrayEQVerticalAngle', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Array EQ Vertical Angle: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateArrayEQVerticalAngle')

    def SetCompressorLimiterInputDetect(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'Left':         'L',
            'Right':        'R',
            'Mix':          'M',
            'Sidechain':    'S'
        }

        if name and value in ValueStateValues:
            CompressorLimiterInputDetectCmdString = 'SA"{}">1={}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('CompressorLimiterInputDetect', CompressorLimiterInputDetectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCompressorLimiterInputDetect')

    def UpdateCompressorLimiterInputDetect(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'L': 'Left',
            'R': 'Right',
            'M': 'Mix',
            'S': 'Sidechain'
        }

        if name:
            CompressorLimiterInputDetectCmdString = 'GA"{}">1\r'.format(name)
            res = self.parse(self.__UpdateHelper('CompressorLimiterInputDetect', CompressorLimiterInputDetectCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('CompressorLimiterInputDetect', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Compressor/Limiter Input Detect: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCompressorLimiterInputDetect')

    def SetCompressorLimiterRatio(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if name and 1.0 <= value <= 20.0:
            CompressorLimiterRatioCmdString = 'SA"{}">3={:.1f}\r'.format(name, value)
            self.__SetHelper('CompressorLimiterRatio', CompressorLimiterRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCompressorLimiterRatio')

    def UpdateCompressorLimiterRatio(self, value, qualifier):

        name = qualifier['Name']

        if name:
            CompressorLimiterRatioCmdString = 'GA"{}">3\r'.format(name)
            res = self.parse(self.__UpdateHelper('CompressorLimiterRatio', CompressorLimiterRatioCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('CompressorLimiterRatio', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Compressor/Limiter Ratio: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCompressorLimiterRatio')

    def SetCompressorLimiterRelease(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if name and 5 <= value <= 1000:
            CompressorLimiterReleaseCmdString = 'SA"{}">5={:.1f}\r'.format(name, value)
            self.__SetHelper('CompressorLimiterRelease', CompressorLimiterReleaseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCompressorLimiterRelease')

    def UpdateCompressorLimiterRelease(self, value, qualifier):

        name = qualifier['Name']

        if name:
            CompressorLimiterReleaseCmdString = 'GA"{}">5\r'.format(name)
            res = self.parse(self.__UpdateHelper('CompressorLimiterRelease', CompressorLimiterReleaseCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('CompressorLimiterRelease', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Compressor/Limiter Release: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCompressorLimiterRelease')

    def SetCrossoverFilter(self, value, qualifier):

        TypeStates = {
            'Low/High': '1',
            'Mid HPF':  '1',
            'Mid LPF':  '3'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        _type = qualifier['Type']

        ValueStateValues = {
            'Butterworth 6dB/oct':      'But6',
            'Butterworth 12dB/oct':     'But12',
            'Butterworth 18dB/oct':     'But18',
            'Butterworth 24dB/oct':     'But24',
            'Butterworth 36dB/oct':     'But36',
            'Butterworth 48dB/oct':     'But48',
            'Bessel 12dB/oct':          'Bes12',
            'Bessel 18dB/oct':          'Bes18',
            'Bessel 24dB/oct':          'Bes24',
            'Bessel 36dB/oct':          'Bes36',
            'Bessel 48dB/oct':          'Bes48',
            'Linkwitz-Reily 12dB/oct':  'Lin12',
            'Linkwitz-Reily 24dB/oct':  'Lin24',
            'Linkwitz-Reily 36dB/oct':  'Lin36',
            'Linkwitz-Reily 48dB/oct':  'Lin48'
        }

        if name and 1 <= int(index1) <= 4 and _type in TypeStates and value in ValueStateValues:
            CrossoverFilterCmdString = 'SA"{}">{}>{}={}\r'.format(name, index1, TypeStates[_type], ValueStateValues[value])
            self.__SetHelper('CrossoverFilter', CrossoverFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrossoverFilter')

    def UpdateCrossoverFilter(self, value, qualifier):

        TypeStates = {
            'Low/High': '1',
            'Mid HPF':  '1',
            'Mid LPF':  '3'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        _type = qualifier['Type']

        ValueStateValues = {
            'But6':     'Butterworth 6dB/oct',
            'But12':    'Butterworth 12dB/oct',
            'But18':    'Butterworth 18dB/oct',
            'But24':    'Butterworth 24dB/oct',
            'But36':    'Butterworth 36dB/oct',
            'But48':    'Butterworth 48dB/oct',
            'Bes12':    'Bessel 12dB/oct',
            'Bes18':    'Bessel 18dB/oct',
            'Bes24':    'Bessel 24dB/oct',
            'Bes36':    'Bessel 36dB/oct',
            'Bes48':    'Bessel 48dB/oct',
            'Lin12':    'Linkwitz-Reily 12dB/oct',
            'Lin24':    'Linkwitz-Reily 24dB/oct',
            'Lin36':    'Linkwitz-Reily 36dB/oct',
            'Lin48':    'Linkwitz-Reily 48dB/oct'
        }

        if name and 1 <= int(index1) <= 4 and _type in TypeStates:
            CrossoverFilterCmdString = 'GA"{}">{}>{}\r'.format(name, index1, TypeStates[_type])
            res = self.parse(self.__UpdateHelper('CrossoverFilter', CrossoverFilterCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('CrossoverFilter', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Crossover Filter: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrossoverFilter')

    def SetCrossoverFrequency(self, value, qualifier):

        TypeStates = {
            'Low/High': '2',
            'Mid HPF':  '2',
            'Mid LPF':  '4'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        _type = qualifier['Type']

        if name and 1 <= int(index1) <= 4 and _type in TypeStates and 20 <= value <= 20000:
            CrossoverFrequencyCmdString = 'SA"{}">{}>{}={}\r'.format(name, index1, TypeStates[_type], value)
            self.__SetHelper('CrossoverFrequency', CrossoverFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrossoverFrequency')

    def UpdateCrossoverFrequency(self, value, qualifier):

        TypeStates = {
            'Low/High': '2',
            'Mid HPF':  '2',
            'Mid LPF':  '4'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        _type = qualifier['Type']

        if name and 1 <= int(index1) <= 4 and _type in TypeStates:
            CrossoverFrequencyCmdString = 'GA"{}">{}>{}\r'.format(name, index1, TypeStates[_type])
            res = self.parse(self.__UpdateHelper('CrossoverFrequency', CrossoverFrequencyCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('CrossoverFrequency', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Crossover Frequency: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrossoverFrequency')

    def SetCrossoverMute(self, value, qualifier):

        TypeStates = {
            'Low/High': '5',
            'Mid':      '7'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        _type = qualifier['Type']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 1 <= int(index1) <= 4 and _type in TypeStates and value in ValueStateValues:
            CrossoverMuteCmdString = 'SA"{}">{}>{}={}\r'.format(name, index1, TypeStates[_type], ValueStateValues[value])
            self.__SetHelper('CrossoverMute', CrossoverMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrossoverMute')

    def UpdateCrossoverMute(self, value, qualifier):

        TypeStates = {
            'Low/High': '5',
            'Mid':      '7'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        _type = qualifier['Type']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 1 <= int(index1) <= 4 and _type in TypeStates:
            CrossoverMuteCmdString = 'GA"{}">{}>{}\r'.format(name, index1, TypeStates[_type])
            res = self.parse(self.__UpdateHelper('CrossoverMute', CrossoverMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('CrossoverMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Crossover Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrossoverMute')

    def SetCrossoverPolarity(self, value, qualifier):

        TypeStates = {
            'Low/High': '4',
            'Mid':      '6'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        _type = qualifier['Type']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 1 <= int(index1) <= 4 and _type in TypeStates and value in ValueStateValues:
            CrossoverPolarityCmdString = 'SA"{}">{}>{}={}\r'.format(name, index1, TypeStates[_type], ValueStateValues[value])
            self.__SetHelper('CrossoverPolarity', CrossoverPolarityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrossoverPolarity')

    def UpdateCrossoverPolarity(self, value, qualifier):

        TypeStates = {
            'Low/High': '4',
            'Mid':      '6'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        _type = qualifier['Type']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 1 <= int(index1) <= 4 and _type in TypeStates:
            CrossoverPolarityCmdString = 'GA"{}">{}>{}\r'.format(name, index1, TypeStates[_type])
            res = self.parse(self.__UpdateHelper('CrossoverPolarity', CrossoverPolarityCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('CrossoverPolarity', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Crossover Polarity: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCrossoverPolarity')

    def SetCRRAdvancedLevel(self, value, qualifier):

        name = qualifier['Name']
        _input = qualifier['Input']
        output = qualifier['Output']
        if name and 1 <= int(_input) <= 51 and 1 <= int(output) <= 67 and -60.5 <= value <= 0.0:
            CRRAdvancedLevelCmdString = 'SA"{}">6>({},{})={:.1f}\r'.format(name, _input, output, value)
            self.__SetHelper('CRRAdvancedLevel', CRRAdvancedLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCRRAdvancedLevel')

    def UpdateCRRAdvancedLevel(self, value, qualifier):

        name = qualifier['Name']
        _input = qualifier['Input']
        output = qualifier['Output']
        if name and 1 <= int(_input) <= 51 and 1 <= int(output) <= 67:
            CRRAdvancedLevelCmdString = 'GA"{}">6>({},{})\r'.format(name, _input, output)
            res = self.parse(self.__UpdateHelper('CRRAdvancedLevel', CRRAdvancedLevelCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('CRRAdvancedLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['CRR Advanced Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCRRAdvancedLevel')

    def SetCRRAdvancedState(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'O', 
            'Off' : 'F'
        }

        name = qualifier['Name']
        _input = qualifier['Input']
        output = qualifier['Output']
        if name and 1 <= int(_input) <= 51 and 1 <= int(output) <= 67 and value in ValueStateValues:
            CRRAdvancedStateCmdString = 'SA"{}">5>({},{})={}\r'.format(name, _input, output, ValueStateValues[value])
            self.__SetHelper('CRRAdvancedState', CRRAdvancedStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCRRAdvancedState')

    def UpdateCRRAdvancedState(self, value, qualifier):

        ValueStateValues = {
            'O' : 'On', 
            'F' : 'Off'
        }

        name = qualifier['Name']
        _input = qualifier['Input']
        output = qualifier['Output']
        if name and 1 <= int(_input) <= 51 and 1 <= int(output) <= 67:
            CRRAdvancedStateCmdString = 'GA"{}">5>({},{})\r'.format(name, _input, output)
            res = self.parse(self.__UpdateHelper('CRRAdvancedState', CRRAdvancedStateCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('CRRAdvancedState', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['CRR Advanced State: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCRRAdvancedState')
            
    def SetDelayBypass(self, value, qualifier):

        name = qualifier['Name']
        output = qualifier['Output']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 1 <= int(output) <= 8 and value in ValueStateValues:
            DelayBypassCmdString = 'SA"{}">{}>2={}\r'.format(name, output, ValueStateValues[value])
            self.__SetHelper('DelayBypass', DelayBypassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDelayBypass')

    def UpdateDelayBypass(self, value, qualifier):

        name = qualifier['Name']
        output = qualifier['Output']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 1 <= int(output) <= 8:
            DelayBypassCmdString = 'GA"{}">{}>2\r'.format(name, output)
            res = self.parse(self.__UpdateHelper('DelayBypass', DelayBypassCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('DelayBypass', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Delay Bypass: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDelayBypass')

    def SetDelayTime(self, value, qualifier):

        name = qualifier['Name']
        output = qualifier['Output']

        if name and 1 <= int(output) <= 8 and 0 <= value <= 48000:
            DelayTimeCmdString = 'SA"{}">{}>1={}\r'.format(name, output, value)
            self.__SetHelper('DelayTime', DelayTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDelayTime')

    def UpdateDelayTime(self, value, qualifier):

        name = qualifier['Name']
        output = qualifier['Output']

        if name and 1 <= int(output) <= 8:
            DelayTimeCmdString = 'GA"{}">{}>1\r'.format(name, output)
            res = self.parse(self.__UpdateHelper('DelayTime', DelayTimeCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('DelayTime', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Delay Time: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDelayTime')

    def SetDuckerDecay(self, value, qualifier):

        name = qualifier['Name']

        if name and 5 <= value <= 50000:
            DuckerDecayCmdString = 'SA"{}">6={}\r'.format(name, value)
            self.__SetHelper('DuckerDecay', DuckerDecayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDuckerDecay')

    def UpdateDuckerDecay(self, value, qualifier):

        name = qualifier['Name']

        if name:
            DuckerDecayCmdString = 'GA"{}">6\r'.format(name)
            res = self.parse(self.__UpdateHelper('DuckerDecay', DuckerDecayCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('DuckerDecay', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Ducker Decay: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDuckerDecay')

    def SetDuckerHold(self, value, qualifier):

        name = qualifier['Name']

        if name and 0 <= value <= 1000:
            DuckerHoldCmdString = 'SA"{}">5={}\r'.format(name, value)
            self.__SetHelper('DuckerHold', DuckerHoldCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDuckerHold')

    def UpdateDuckerHold(self, value, qualifier):

        name = qualifier['Name']

        if name:
            DuckerHoldCmdString = 'GA"{}">5\r'.format(name)
            res = self.parse(self.__UpdateHelper('DuckerHold', DuckerHoldCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('DuckerHold', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Ducker Hold: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDuckerHold')

    def SetDuckerRange(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if name and -60 <= value <= 0:
            DuckerRangeCmdString = 'SA"{}">3={:.1f}\r'.format(name, value)
            self.__SetHelper('DuckerRange', DuckerRangeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDuckerRange')

    def UpdateDuckerRange(self, value, qualifier):

        name = qualifier['Name']

        if name:
            DuckerRangeCmdString = 'GA"{}">3\r'.format(name)
            res = self.parse(self.__UpdateHelper('DuckerRange', DuckerRangeCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('DuckerRange', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Ducker Range: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDuckerRange')

    def SetGain(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if name and -60.5 <= value <= 12.0:
            GainCmdString = 'SA"{}">1={:.1f}\r'.format(name, value)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):

        name = qualifier['Name']

        if name:
            GainCmdString = 'GA"{}">1\r'.format(name)
            res = self.parse(self.__UpdateHelper('Gain', GainCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('Gain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGain')

    def SetGainMute(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and value in ValueStateValues:
            GainMuteCmdString = 'SA"{}">2={}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('GainMute', GainMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGainMute')

    def UpdateGainMute(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name:
            GainMuteCmdString = 'GA"{}">2\r'.format(name)
            res = self.parse(self.__UpdateHelper('GainMute', GainMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('GainMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Gain Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGainMute')

    def SetGateDecay(self, value, qualifier):

        name = qualifier['Name']

        if name and 5 <= value <= 50000:
            GateDecayCmdString = 'SA"{}">6={}\r'.format(name, value)
            self.__SetHelper('GateDecay', GateDecayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGateDecay')

    def UpdateGateDecay(self, value, qualifier):

        name = qualifier['Name']

        if name:
            GateDecayCmdString = 'GA"{}">6\r'.format(name)
            res = self.parse(self.__UpdateHelper('GateDecay', GateDecayCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('GateDecay', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Gate Decay: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGateDecay')

    def SetGateDetector(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'Left':         'L',
            'Right':        'R',
            'Mix':          'M',
            'Sidechain':    'S'
        }

        if name and value in ValueStateValues:
            GateDetectorCmdString = 'SA"{}">1={}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('GateDetector', GateDetectorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGateDetector')

    def UpdateGateDetector(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'L': 'Left',
            'R': 'Right',
            'M': 'Mix',
            'S': 'Sidechain'
        }

        if name:
            GateDetectorCmdString = 'GA"{}">1\r'.format(name)
            res = self.parse(self.__UpdateHelper('GateDetector', GateDetectorCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('GateDetector', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Gate Detector: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGateDetector')

    def SetGateHold(self, value, qualifier):

        name = qualifier['Name']

        if name and 0 <= value <= 1000:
            GateHoldCmdString = 'SA"{}">5={}\r'.format(name, value)
            self.__SetHelper('GateHold', GateHoldCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGateHold')

    def UpdateGateHold(self, value, qualifier):

        name = qualifier['Name']

        if name:
            GateHoldCmdString = 'GA"{}">5\r'.format(name)
            res = self.parse(self.__UpdateHelper('GateHold', GateHoldCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('GateHold', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Gate Hold: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGateHold')

    def SetGateRange(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if name and -70.0 <= value <= 0.0:
            GateRangeCmdString = 'SA"{}">3={:.1f}\r'.format(name, value)
            self.__SetHelper('GateRange', GateRangeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGateRange')

    def UpdateGateRange(self, value, qualifier):

        name = qualifier['Name']

        if name:
            GateRangeCmdString = 'GA"{}">3\r'.format(name)
            res = self.parse(self.__UpdateHelper('GateRange', GateRangeCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('GateRange', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Gate Range: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGateRange')

    def SetGPOMode(self, value, qualifier):

        name = qualifier['Name']
        pin = qualifier['Pin']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 1 <= int(pin) <= 5 and value in ValueStateValues:
            GPOModeCmdString = 'SA"{}">{}={}\r'.format(name, pin, ValueStateValues[value])
            self.__SetHelper('GPOMode', GPOModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGPOMode')

    def UpdateGPOMode(self, value, qualifier):

        name = qualifier['Name']
        pin = qualifier['Pin']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 1 <= int(pin) <= 5:
            GPOModeCmdString = 'GA"{}">{}\r'.format(name, pin)
            res = self.parse(self.__UpdateHelper('GPOMode', GPOModeCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('GPOMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['GPO Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGPOMode')

    def SetGraphicEQLevel(self, value, qualifier):

        FrequencyStates = {
            '20Hz':     '1',
            '25Hz':     '2',
            '31.5Hz':   '3',
            '40Hz':     '4',
            '50Hz':     '5',
            '63Hz':     '6',
            '80Hz':     '7',
            '100Hz':    '8',
            '125Hz':    '9',
            '160Hz':    '10',
            '200Hz':    '11',
            '250Hz':    '12',
            '315Hz':    '13',
            '400Hz':    '14',
            '500Hz':    '15',
            '630Hz':    '16',
            '800Hz':    '17',
            '1kHz':     '18',
            '1.25kHz':  '19',
            '1.6kHz':   '20',
            '2kHz':     '21',
            '2.5kHz':   '22',
            '3.15kHz':  '23',
            '4kHz':     '24',
            '5kHz':     '25',
            '6.3kHz':   '26',
            '8kHz':     '27',
            '10kHz':    '28',
            '12.5kHz':  '29',
            '16kHz':    '30',
            '20kHz':    '31'
        }

        name = qualifier['Name']
        frequency = qualifier['Frequency']
        value = float('{:.1f}'.format(value))

        if name and frequency in FrequencyStates and -15.0 <= value <= 15.0:
            GraphicEQLevelCmdString = 'SA"{}">{}={:.1f}\r'.format(name, FrequencyStates[frequency], value)
            self.__SetHelper('GraphicEQLevel', GraphicEQLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGraphicEQLevel')

    def UpdateGraphicEQLevel(self, value, qualifier):

        FrequencyStates = {
            '20Hz':     '1',
            '25Hz':     '2',
            '31.5Hz':   '3',
            '40Hz':     '4',
            '50Hz':     '5',
            '63Hz':     '6',
            '80Hz':     '7',
            '100Hz':    '8',
            '125Hz':    '9',
            '160Hz':    '10',
            '200Hz':    '11',
            '250Hz':    '12',
            '315Hz':    '13',
            '400Hz':    '14',
            '500Hz':    '15',
            '630Hz':    '16',
            '800Hz':    '17',
            '1kHz':     '18',
            '1.25kHz':  '19',
            '1.6kHz':   '20',
            '2kHz':     '21',
            '2.5kHz':   '22',
            '3.15kHz':  '23',
            '4kHz':     '24',
            '5kHz':     '25',
            '6.3kHz':   '26',
            '8kHz':     '27',
            '10kHz':    '28',
            '12.5kHz':  '29',
            '16kHz':    '30',
            '20kHz':    '31'
        }

        name = qualifier['Name']
        frequency = qualifier['Frequency']

        if name and frequency in FrequencyStates:
            GraphicEQLevelCmdString = 'GA"{}">{}\r'.format(name, FrequencyStates[frequency])
            res = self.parse(self.__UpdateHelper('GraphicEQLevel', GraphicEQLevelCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('GraphicEQLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Graphic EQ Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGraphicEQLevel')

    def SetGroupLevel(self, value, qualifier):

        group = qualifier['Group']

        if 1 <= int(group) <= 64 and -60.0 <= value <= 12.0:
            scaled = int((value + 60) * 2)
            GroupLevelCmdString = 'SG {:x},{:x}\r'.format(int(group), scaled)
            self.__SetHelper('GroupLevel', GroupLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupLevel')

    def UpdateGroupLevel(self, value, qualifier):

        group = qualifier['Group']

        if 1 <= int(group) <= 64:
            GroupLevelCmdString = 'GG {:x}\r'.format(int(group))
            res = self.__UpdateHelper('GroupLevel', GroupLevelCmdString, value, qualifier)
            if res:
                try:
                    res = res.strip(';\r')
                    value = int(res.split(',')[-1], 16)
                    value = float('{:.1f}'.format(value / 2 - 60))
                    self.WriteStatus('GroupLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Group Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGroupLevel')

    def SetGroupMute(self, value, qualifier):

        group = qualifier['Group']

        ValueStateValues = {
            'On':   'M',
            'Off':  'U'
        }

        if 1 <= int(group) <= 64 and value in ValueStateValues:
            GroupMuteCmdString = 'SN {:x},{}\r'.format(int(group), ValueStateValues[value])
            self.__SetHelper('GroupMute', GroupMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = qualifier['Group']

        ValueStateValues = {
            'M': 'On',
            'U': 'Off'
        }

        if 1 <= int(group) <= 64:
            GroupMuteCmdString = 'GN {:x}\r'.format(int(group))
            res = self.__UpdateHelper('GroupMute', GroupMuteCmdString, value, qualifier)
            if res:
                try:
                    res = res.strip(';\r').split(',')[-1]
                    value = ValueStateValues[res]
                    self.WriteStatus('GroupMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Group Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetMatrixMixerLevel(self, value, qualifier):

        name = qualifier['Name']
        _input = qualifier['Input']
        output = qualifier['Output']
        matrix_size = qualifier['Matrix Size']
        value = float('{:.1f}'.format(value))

        if name and 1 <= int(_input) <= 32 and 1 <= int(output) <= 32 and 1 <= int(matrix_size) <= 32 and -60.5 <= value <= 0.0:
            index2 = ((int(_input) - 1) * int(matrix_size)) + int(output)
            MatrixMixerLevelCmdString = 'SA"{}">2>{}={:.1f}\r'.format(name, index2, value)
            self.__SetHelper('MatrixMixerLevel', MatrixMixerLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerLevel')

    def UpdateMatrixMixerLevel(self, value, qualifier):

        name = qualifier['Name']
        _input = qualifier['Input']
        output = qualifier['Output']
        matrix_size = qualifier['Matrix Size']

        if name and 1 <= int(_input) <= 32 and 1 <= int(output) <= 32 and 1 <= int(matrix_size) <= 32:
            index2 = ((int(_input) - 1) * int(matrix_size)) + int(output)
            MatrixMixerLevelCmdString = 'GA"{}">2>{}\r'.format(name, index2)
            res = self.parse(self.__UpdateHelper('MatrixMixerLevel', MatrixMixerLevelCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('MatrixMixerLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Matrix Mixer Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMatrixMixerLevel')

    def SetMatrixMixerState(self, value, qualifier):

        name = qualifier['Name']
        _input = qualifier['Input']
        output = qualifier['Output']
        matrix_size = qualifier['Matrix Size']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 1 <= int(_input) <= 32 and 1 <= int(output) <= 32 and 1 <= int(matrix_size) <= 32 and value in ValueStateValues:
            index2 = ((int(_input) - 1) * int(matrix_size)) + int(output)
            MatrixMixerStateCmdString = 'SA"{}">1>{}={}\r'.format(name, index2, ValueStateValues[value])
            self.__SetHelper('MatrixMixerState', MatrixMixerStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerState')

    def UpdateMatrixMixerState(self, value, qualifier):

        name = qualifier['Name']
        _input = qualifier['Input']
        output = qualifier['Output']
        matrix_size = qualifier['Matrix Size']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 1 <= int(_input) <= 32 and 1 <= int(output) <= 32 and 1 <= int(matrix_size) <= 32:
            index2 = ((int(_input) - 1) * int(matrix_size)) + int(output)
            MatrixMixerStateCmdString = 'GA"{}">1>{}\r'.format(name, index2)
            res = self.parse(self.__UpdateHelper('MatrixMixerState', MatrixMixerStateCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('MatrixMixerState', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Matrix Mixer State: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMatrixMixerState')

    def SetParameterRecall(self, value, qualifier):

        if 1 <= int(value) <= 255:
            ParameterRecallCmdString = 'SS {:x}\r'.format(int(value))
            self.__SetHelper('ParameterRecall', ParameterRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetParameterRecall')

    def UpdateParameterRecall(self, value, qualifier):

        ParameterRecallCmdString = 'GS\r'
        res = self.__UpdateHelper('ParameterRecall', ParameterRecallCmdString, value, qualifier)
        if res:
            try:
                res = res.strip(';\r')
                value = int(res.split()[-1], 16)

                if 0 <= value <= 255:
                    value = str(value)

                    if value == '0':
                        value = 'None'
                    self.WriteStatus('ParameterRecall', value, qualifier)
            except ValueError:
                self.Error(['Parameter Recall: Invalid/unexpected response'])

    def SetParametricEQFrequency(self, value, qualifier):

        name = qualifier['Name']
        band = qualifier['Band']

        if name and 1 <= int(band) <= 16 and 20 <= value <= 20000:
            ParametricEQFrequencyCmdString = 'SA"{}">{}>1={}\r'.format(name, band, value)
            self.__SetHelper('ParametricEQFrequency', ParametricEQFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetParametricEQFrequency')

    def UpdateParametricEQFrequency(self, value, qualifier):

        name = qualifier['Name']
        band = qualifier['Band']

        if name and 1 <= int(band) <= 16:
            ParametricEQFrequencyCmdString = 'GA"{}">{}>1\r'.format(name, band)
            res = self.parse(self.__UpdateHelper('ParametricEQFrequency', ParametricEQFrequencyCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('ParametricEQFrequency', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Parametric EQ Frequency: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateParametricEQFrequency')

    def SetParametricEQGain(self, value, qualifier):

        name = qualifier['Name']
        band = qualifier['Band']
        value = float('{:.1f}'.format(value))

        if name and 1 <= int(band) <= 16 and -20.0 <= value <= 20.0:
            ParametricEQGainCmdString = 'SA"{}">{}>3={:.1f}\r'.format(name, band, value)
            self.__SetHelper('ParametricEQGain', ParametricEQGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetParametricEQGain')

    def UpdateParametricEQGain(self, value, qualifier):

        name = qualifier['Name']
        band = qualifier['Band']

        if name and 1 <= int(band) <= 16:
            ParametricEQGainCmdString = 'GA"{}">{}>3\r'.format(name, band)
            res = self.parse(self.__UpdateHelper('ParametricEQGain', ParametricEQGainCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('ParametricEQGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Parametric EQ Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateParametricEQGain')

    def SetParametricEQQ(self, value, qualifier):

        name = qualifier['Name']
        band = qualifier['Band']
        value = float('{:.3f}'.format(value))

        if name and 1 <= int(band) <= 16 and 0.1 <= value <= 14.42:
            ParametricEQQCmdString = 'SA"{}">{}>2={:.3f}\r'.format(name, band, value)
            self.__SetHelper('ParametricEQQ', ParametricEQQCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetParametricEQQ')

    def UpdateParametricEQQ(self, value, qualifier):

        name = qualifier['Name']
        band = qualifier['Band']

        if name and 1 <= int(band) <= 16:
            ParametricEQQCmdString = 'GA"{}">{}>2\r'.format(name, band)
            res = self.parse(self.__UpdateHelper('ParametricEQQ', ParametricEQQCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.3f}'.format(float(res)))
                    self.WriteStatus('ParametricEQQ', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Parametric EQ Q: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateParametricEQQ')

    def SetParametricEQSlope(self, value, qualifier):

        name = qualifier['Name']
        band = qualifier['Band']

        ValueStateValues = {'-6', '-12'}

        if name and 1 <= int(band) <= 16 and value in ValueStateValues:
            ParametricEQSlopeCmdString = 'SA"{}">{}>4={}\r'.format(name, band, value)
            self.__SetHelper('ParametricEQSlope', ParametricEQSlopeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetParametricEQSlope')

    def UpdateParametricEQSlope(self, value, qualifier):

        name = qualifier['Name']
        band = qualifier['Band']

        ValueStateValues = {
            '-6':   '-6',
            '-12':  '-12'
        }

        if name and 1 <= int(band) <= 16:
            ParametricEQSlopeCmdString = 'GA"{}">{}>4\r'.format(name, band)
            res = self.parse(self.__UpdateHelper('ParametricEQSlope', ParametricEQSlopeCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[str(int(float(res)))]
                    self.WriteStatus('ParametricEQSlope', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Parametric EQ Slope: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateParametricEQSlope')

    def SetParametricEQType(self, value, qualifier):

        name = qualifier['Name']
        band = qualifier['Band']

        ValueStateValues = {
            'PEQ':          'B',
            'High Shelf':   'HS',
            'Low Shelf':    'LS',
            'Low Pass':     'HC',
            'High Pass':    'LC',
            'Notch':        'N'
        }

        if name and 1 <= int(band) <= 16 and value in ValueStateValues:
            ParametricEQTypeCmdString = 'SA"{}">{}>5={}\r'.format(name, band, ValueStateValues[value])
            self.__SetHelper('ParametricEQType', ParametricEQTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetParametricEQType')

    def UpdateParametricEQType(self, value, qualifier):

        name = qualifier['Name']
        band = qualifier['Band']

        ValueStateValues = {
            'B':    'PEQ',
            'HS':   'High Shelf',
            'LS':   'Low Shelf',
            'HC':   'Low Pass',
            'LC':   'High Pass',
            'N':    'Notch'
        }

        if name and 1 <= int(band) <= 16:
            ParametricEQTypeCmdString = 'GA"{}">{}>5\r'.format(name, band)
            res = self.parse(self.__UpdateHelper('ParametricEQType', ParametricEQTypeCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('ParametricEQType', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Parametric EQ Type: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateParametricEQType')

    def SetPeakRMSInputDetect(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'Left':         'L',
            'Right':        'R',
            'Mix':          'M',
            'Sidechain':    'S'
        }

        if name and value in ValueStateValues:
            PeakRMSInputDetectCmdString = 'SA"{}">1={}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('PeakRMSInputDetect', PeakRMSInputDetectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPeakRMSInputDetect')

    def UpdatePeakRMSInputDetect(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'L': 'Left',
            'R': 'Right',
            'M': 'Mix',
            'S': 'Sidechain'
        }

        if name:
            PeakRMSInputDetectCmdString = 'GA"{}">1\r'.format(name)
            res = self.parse(self.__UpdateHelper('PeakRMSInputDetect', PeakRMSInputDetectCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('PeakRMSInputDetect', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Peak/RMS Input Detect: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePeakRMSInputDetect')

    def SetPeakRMSRMS(self, value, qualifier):

        FunctionStates = {
            'Attack':   '8',
            'Release':  '9'
        }

        name = qualifier['Name']
        _function = qualifier['Function']

        if name and _function in FunctionStates and 500 <= value <= 10000:
            PeakRMSRMSCmdString = 'SA"{}">{}={}\r'.format(name, FunctionStates[_function], value)
            self.__SetHelper('PeakRMSRMS', PeakRMSRMSCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPeakRMSRMS')

    def UpdatePeakRMSRMS(self, value, qualifier):

        FunctionStates = {
            'Attack':   '8',
            'Release':  '9'
        }

        name = qualifier['Name']
        _function = qualifier['Function']

        if name and _function in FunctionStates:
            PeakRMSRMSCmdString = 'GA"{}">{}\r'.format(name, FunctionStates[_function])
            res = self.parse(self.__UpdateHelper('PeakRMSRMS', PeakRMSRMSCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('PeakRMSRMS', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Peak/RMS RMS: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePeakRMSRMS')

    def SetPSTNAction(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'Make Call':    '2',
            'End Call':     '3',
            'Answer Call':  '4'
        }

        dial_string = qualifier['Dial String']

        if name and value in ValueStateValues:
            if value == 'Make Call':
                if dial_string:
                    PSTNActionCmdString = 'MA"{}">{}="{}"\r'.format(name, ValueStateValues[value], dial_string)
                else:
                    self.Discard('Invalid Command for SetPSTNAction')
                    return
            else:
                PSTNActionCmdString = 'MA"{}">{}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('PSTNAction', PSTNActionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPSTNAction')
    def UpdatePSTNCallActive(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name:
            PSTNCallActiveCmdString = 'GA"{}">0>8\r'.format(name)
            res = self.parse(self.__UpdateHelper('PSTNCallActive', PSTNCallActiveCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('PSTNCallActive', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PSTN Call Active: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePSTNCallActive')

    def UpdatePSTNCallStatus(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            '"HANGUP"':     'Hangup',
            '"INCOMING"':   'Incoming',
            '"ACTIVE"':     'Active',
            '"ERROR"':      'Error'
        }

        if name:
            PSTNCallStatusCmdString = 'GA"{}">0>1\r'.format(name)
            res = self.parse(self.__UpdateHelper('PSTNCallStatus', PSTNCallStatusCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('PSTNCallStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PSTN Call Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePSTNCallStatus')

    def UpdatePSTNCallerID(self, value, qualifier):

        name = qualifier['Name']

        if name:

            PSTNCallerIDCmdString = 'GA"{}">0>2\r'.format(name)
            res = self.parse(self.__UpdateHelper('PSTNCallerID', PSTNCallerIDCmdString, value, qualifier))
            if res:
                try:
                    res = res.split('&')

                    self.WriteStatus('PSTNCallerID', res[0].split()[0][1:].strip(), {'Name': name, 'Type': 'Date'})
                    self.WriteStatus('PSTNCallerID', res[0].split()[1].strip(), {'Name': name, 'Type': 'Time'})
                    self.WriteStatus('PSTNCallerID', res[1].strip(), {'Name': name, 'Type': 'Number'})
                    self.WriteStatus('PSTNCallerID', res[2][:-1].strip(), {'Name': name, 'Type': 'Name'})
                except (ValueError, IndexError):
                    self.Error(['PSTN Caller ID: Invalid/unexpected response'])
        else:
            self.Discard('Device Is Busy for UpdatePSTNCallerID')

    def SetPSTNDialKey(self, value, qualifier):

        name = qualifier['Name']

        if name and value in '0123456789*#!':
            PSTNDialKeyCmdString = 'MA"{}">1="{}"\r'.format(name, value)
            self.__SetHelper('PSTNDialKey', PSTNDialKeyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPSTNDialKey')

    def SetPSTNHook(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and value in ValueStateValues:
            PSTNHookCmdString = 'SA"{}">0>9={}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('PSTNHook', PSTNHookCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPSTNHook')

    def UpdatePSTNHook(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name:
            PSTNHookCmdString = 'GA"{}">0>9\r'.format(name)
            res = self.parse(self.__UpdateHelper('PSTNHook', PSTNHookCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('PSTNHook', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PSTN Hook: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePSTNHook')

    def SetPSTNLevel(self, value, qualifier):

        ModuleStates = {
            'Input':    '1>1',
            'Output':   '1'
        }

        module = qualifier['Module']
        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if module in ModuleStates and name and -60.5 <= value <= 12.0:
            PSTNLevelCmdString = 'SA"{}">{}={:.1f}\r'.format(name, ModuleStates[module], value)
            self.__SetHelper('PSTNLevel', PSTNLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPSTNLevel')

    def UpdatePSTNLevel(self, value, qualifier):

        ModuleStates = {
            'Input':    '1>1',
            'Output':   '1'
        }

        module = qualifier['Module']
        name = qualifier['Name']

        if module in ModuleStates and name:
            PSTNLevelCmdString = 'GA"{}">{}\r'.format(name, ModuleStates[module])
            res = self.parse(self.__UpdateHelper('PSTNLevel', PSTNLevelCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('PSTNLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['PSTN Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePSTNLevel')

    def SetPSTNMute(self, value, qualifier):

        ModuleStates = {
            'Input':    '1>2',
            'Output':   '2'
        }

        module = qualifier['Module']
        name = qualifier['Name']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if module in ModuleStates and name and value in ValueStateValues:
            PSTNMuteCmdString = 'SA"{}">{}={}\r'.format(name, ModuleStates[module], ValueStateValues[value])
            self.__SetHelper('PSTNMute', PSTNMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPSTNMute')

    def UpdatePSTNMute(self, value, qualifier):

        ModuleStates = {
            'Input':    '1>2',
            'Output':   '2'
        }

        module = qualifier['Module']
        name = qualifier['Name']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if module in ModuleStates and name:
            PSTNMuteCmdString = 'GA"{}">{}\r'.format(name, ModuleStates[module])
            res = self.parse(self.__UpdateHelper('PSTNMute', PSTNMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('PSTNMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PSTN Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePSTNMute')

    def SetRouterInputSelect(self, value, qualifier):

        name = qualifier['Name']
        output = qualifier['Output']

        if name and 1 <= int(output) <= 32 and 0 <= int(value) <= 32:
            RouterInputSelectCmdString = 'SA"{}">{}={}\r'.format(name, output, value)
            self.__SetHelper('RouterInputSelect', RouterInputSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRouterInputSelect')

    def UpdateRouterInputSelect(self, value, qualifier):

        name = qualifier['Name']
        output = qualifier['Output']

        if name and 1 <= int(output) <= 32:
            RouterInputSelectCmdString = 'GA"{}">{}\r'.format(name, output)
            res = self.parse(self.__UpdateHelper('RouterInputSelect', RouterInputSelectCmdString, value, qualifier))
            if res:
                try:
                    value = str(res)
                    self.WriteStatus('RouterInputSelect', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Router Input Select: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRouterInputSelect')

    def SetSignalGeneratorGain(self, value, qualifier):

        WaveStates = {
            'Sine':     '1>2',
            'White':    '2>1',
            'Pink':     '3>1',
            'Sweep':    '4>1'
        }

        name = qualifier['Name']
        wave = qualifier['Wave']
        value = float('{:.1f}'.format(value))

        if name and wave in WaveStates and -60.5 <= value <= 12.0:
            SignalGeneratorGainCmdString = 'SA"{}">{}={:.1f}\r'.format(name, WaveStates[wave], value)
            self.__SetHelper('SignalGeneratorGain', SignalGeneratorGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalGeneratorGain')

    def UpdateSignalGeneratorGain(self, value, qualifier):

        WaveStates = {
            'Sine':     '1>2',
            'White':    '2>1',
            'Pink':     '3>1',
            'Sweep':    '4>1'
        }

        name = qualifier['Name']
        wave = qualifier['Wave']

        if name and wave in WaveStates:
            SignalGeneratorGainCmdString = 'GA"{}">{}\r'.format(name, WaveStates[wave])
            res = self.parse(self.__UpdateHelper('SignalGeneratorGain', SignalGeneratorGainCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('SignalGeneratorGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Signal Generator Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSignalGeneratorGain')

    def SetSignalGeneratorMute(self, value, qualifier):

        WaveStates = {
            'Sine':     '1>3',
            'White':    '2>2',
            'Pink':     '3>2'
        }

        name = qualifier['Name']
        wave = qualifier['Wave']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and wave in WaveStates and value in ValueStateValues:
            SignalGeneratorMuteCmdString = 'SA"{}">{}={}\r'.format(name, WaveStates[wave], ValueStateValues[value])
            self.__SetHelper('SignalGeneratorMute', SignalGeneratorMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalGeneratorMute')

    def UpdateSignalGeneratorMute(self, value, qualifier):

        WaveStates = {
            'Sine':     '1>3',
            'White':    '2>2',
            'Pink':     '3>2'
        }

        name = qualifier['Name']
        wave = qualifier['Wave']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and wave in WaveStates:
            SignalGeneratorMuteCmdString = 'GA"{}">{}\r'.format(name, WaveStates[wave])
            res = self.parse(self.__UpdateHelper('SignalGeneratorMute', SignalGeneratorMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('SignalGeneratorMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Signal Generator Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSignalGeneratorMute')

    def SetSourceSelect(self, value, qualifier):

        name = qualifier['Name']

        if name and 1 <= int(value) <= 32:
            SourceSelectCmdString = 'SA"{}">1={}\r'.format(name, value)
            self.__SetHelper('SourceSelect', SourceSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSourceSelect')

    def UpdateSourceSelect(self, value, qualifier):

        name = qualifier['Name']

        if name:
            SourceSelectCmdString = 'GA"{}">1\r'.format(name)
            res = self.parse(self.__UpdateHelper('SourceSelect', SourceSelectCmdString, value, qualifier))
            if res:
                try:
                    value = str(res)
                    self.WriteStatus('SourceSelect', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Source Select: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSourceSelect')

    def SetSpeakerParametricAlignDelay(self, value, qualifier):

        name = qualifier['Name']

        if name and 0 <= value <= 480:
            SpeakerParametricAlignDelayCmdString = 'SA"{}">0>4={}\r'.format(name, value)
            self.__SetHelper('SpeakerParametricAlignDelay', SpeakerParametricAlignDelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerParametricAlignDelay')

    def UpdateSpeakerParametricAlignDelay(self, value, qualifier):

        name = qualifier['Name']

        if name:
            SpeakerParametricAlignDelayCmdString = 'GA"{}">0>4\r'.format(name)
            res = self.parse(self.__UpdateHelper('SpeakerParametricAlignDelay', SpeakerParametricAlignDelayCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('SpeakerParametricAlignDelay', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Speaker Parametric Align Delay: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerParametricAlignDelay')

    def SetSpeakerParametricBypass(self, value, qualifier):

        TypeStates = {
            'High': '10',
            'Low':  '9'
        }

        name = qualifier['Name']
        _type = qualifier['Type']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and _type in TypeStates and value in ValueStateValues:
            SpeakerParametricBypassCmdString = 'SA"{}">0>{}={}\r'.format(name, TypeStates[_type], ValueStateValues[value])
            self.__SetHelper('SpeakerParametricBypass', SpeakerParametricBypassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerParametricBypass')

    def UpdateSpeakerParametricBypass(self, value, qualifier):

        TypeStates = {
            'High': '10',
            'Low':  '9'
        }

        name = qualifier['Name']
        _type = qualifier['Type']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and _type in TypeStates:
            SpeakerParametricBypassCmdString = 'GA"{}">0>{}\r'.format(name, TypeStates[_type])
            res = self.parse(self.__UpdateHelper('SpeakerParametricBypass', SpeakerParametricBypassCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('SpeakerParametricBypass', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Speaker Parametric Bypass: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerParametricBypass')

    def SetSpeakerParametricEQBandBypass(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and 1 <= int(index1) <= 9 and value in ValueStateValues:
            SpeakerParametricEQBandBypassCmdString = 'SA"{}">{}>6={}\r'.format(name, index1, ValueStateValues[value])
            self.__SetHelper('SpeakerParametricEQBandBypass', SpeakerParametricEQBandBypassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerParametricEQBandBypass')

    def UpdateSpeakerParametricEQBandBypass(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and 1 <= int(index1) <= 9:
            SpeakerParametricEQBandBypassCmdString = 'GA"{}">{}>6\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('SpeakerParametricEQBandBypass', SpeakerParametricEQBandBypassCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('SpeakerParametricEQBandBypass', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Speaker Parametric EQ Band Bypass: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerParametricEQBandBypass')

    def SetSpeakerParametricEQBandFilter(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'PEQ':          'B',
            'High Shelf':   'HS',
            'Low Shelf':    'LS',
            'Notch':        'N'
        }

        if name and 1 <= int(index1) <= 9 and value in ValueStateValues:
            SpeakerParametricEQBandFilterCmdString = 'SA"{}">{}>5={}\r'.format(name, index1, ValueStateValues[value])
            self.__SetHelper('SpeakerParametricEQBandFilter', SpeakerParametricEQBandFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerParametricEQBandFilter')

    def UpdateSpeakerParametricEQBandFilter(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        ValueStateValues = {
            'B':    'PEQ',
            'HS':   'High Shelf',
            'LS':   'Low Shelf',
            'N':    'Notch'
        }

        if name and 1 <= int(index1) <= 9:
            SpeakerParametricEQBandFilterCmdString = 'GA"{}">{}>5\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('SpeakerParametricEQBandFilter', SpeakerParametricEQBandFilterCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('SpeakerParametricEQBandFilter', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Speaker Parametric EQ Band Filter: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerParametricEQBandFilter')

    def SetSpeakerParametricEQBandFrequency(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 9 and 20 <= value <= 20000:
            SpeakerParametricEQBandFrequencyCmdString = 'SA"{}">{}>1={}\r'.format(name, index1, value)
            self.__SetHelper('SpeakerParametricEQBandFrequency', SpeakerParametricEQBandFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerParametricEQBandFrequency')

    def UpdateSpeakerParametricEQBandFrequency(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 9:
            SpeakerParametricEQBandFrequencyCmdString = 'GA"{}">{}>1\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('SpeakerParametricEQBandFrequency', SpeakerParametricEQBandFrequencyCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('SpeakerParametricEQBandFrequency', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Speaker Parametric EQ Band Frequency: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerParametricEQBandFrequency')

    def SetSpeakerParametricEQBandGain(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        value = float('{:.1f}'.format(value))

        if name and 1 <= int(index1) <= 9 and -20.0 <= value <= 20.0:
            SpeakerParametricEQBandGainCmdString = 'SA"{}">{}>3={:.1f}\r'.format(name, index1, value)
            self.__SetHelper('SpeakerParametricEQBandGain', SpeakerParametricEQBandGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerParametricEQBandGain')

    def UpdateSpeakerParametricEQBandGain(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 9:
            SpeakerParametricEQBandGainCmdString = 'GA"{}">{}>3\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('SpeakerParametricEQBandGain', SpeakerParametricEQBandGainCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('SpeakerParametricEQBandGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Speaker Parametric EQ Band Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerParametricEQBandGain')

    def SetSpeakerParametricEQBandQ(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        value = float('{:.3f}'.format(value))

        if name and 1 <= int(index1) <= 9 and 0.1 <= value <= 10.0:
            SpeakerParametricEQBandQCmdString = 'SA"{}">{}>2={:.3f}\r'.format(name, index1, value)
            self.__SetHelper('SpeakerParametricEQBandQ', SpeakerParametricEQBandQCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerParametricEQBandQ')

    def UpdateSpeakerParametricEQBandQ(self, value, qualifier):

        name = qualifier['Name']
        index1 = qualifier['Index 1']

        if name and 1 <= int(index1) <= 9:
            SpeakerParametricEQBandQCmdString = 'GA"{}">{}>2\r'.format(name, index1)
            res = self.parse(self.__UpdateHelper('SpeakerParametricEQBandQ', SpeakerParametricEQBandQCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.3f}'.format(float(res)))
                    self.WriteStatus('SpeakerParametricEQBandQ', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Speaker Parametric EQ Band Q: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerParametricEQBandQ')

    def SetSpeakerParametricFilter(self, value, qualifier):

        TypeStates = {
            'High': '5',
            'Low':  '7'
        }

        name = qualifier['Name']
        _type = qualifier['Type']

        ValueStateValues = {
            'Butterworth 6dB/oct':      'But6',
            'Butterworth 12dB/oct':     'But12',
            'Butterworth 18dB/oct':     'But18',
            'Butterworth 24dB/oct':     'But24',
            'Butterworth 36dB/oct':     'But36',
            'Butterworth 48dB/oct':     'But48',
            'Bessel 12dB/oct':          'Bes12',
            'Bessel 18dB/oct':          'Bes18',
            'Bessel 24dB/oct':          'Bes24',
            'Bessel 36dB/oct':          'Bes36',
            'Bessel 48dB/oct':          'Bes48',
            'Linkwitz-Reily 12dB/oct':  'Lin12',
            'Linkwitz-Reily 24dB/oct':  'Lin24',
            'Linkwitz-Reily 36dB/oct':  'Lin36',
            'Linkwitz-Reily 48dB/oct':  'Lin48'
        }

        if name and _type in TypeStates and value in ValueStateValues:
            SpeakerParametricFilterCmdString = 'SA"{}">0>{}={}\r'.format(name, TypeStates[_type], ValueStateValues[value])
            self.__SetHelper('SpeakerParametricFilter', SpeakerParametricFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerParametricFilter')

    def UpdateSpeakerParametricFilter(self, value, qualifier):

        TypeStates = {
            'High': '5',
            'Low':  '7'
        }

        name = qualifier['Name']
        _type = qualifier['Type']

        ValueStateValues = {
            'But6':     'Butterworth 6dB/oct',
            'But12':    'Butterworth 12dB/oct',
            'But18':    'Butterworth 18dB/oct',
            'But24':    'Butterworth 24dB/oct',
            'But36':    'Butterworth 36dB/oct',
            'But48':    'Butterworth 48dB/oct',
            'Bes12':    'Bessel 12dB/oct',
            'Bes18':    'Bessel 18dB/oct',
            'Bes24':    'Bessel 24dB/oct',
            'Bes36':    'Bessel 36dB/oct',
            'Bes48':    'Bessel 48dB/oct',
            'Lin12':    'Linkwitz-Reily 12dB/oct',
            'Lin24':    'Linkwitz-Reily 24dB/oct',
            'Lin36':    'Linkwitz-Reily 36dB/oct',
            'Lin48':    'Linkwitz-Reily 48dB/oct'
        }

        if name and _type in TypeStates:
            SpeakerParametricFilterCmdString = 'GA"{}">0>{}\r'.format(name, TypeStates[_type])
            res = self.parse(self.__UpdateHelper('SpeakerParametricFilter', SpeakerParametricFilterCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('SpeakerParametricFilter', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Speaker Parametric Filter: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerParametricFilter')

    def SetSpeakerParametricFrequency(self, value, qualifier):

        TypeStates = {
            'High': '6',
            'Low':  '8'
        }

        name = qualifier['Name']
        _type = qualifier['Type']

        if name and _type in TypeStates and 20 <= value <= 20000:
            SpeakerParametricFrequencyCmdString = 'SA"{}">0>{}={}\r'.format(name, TypeStates[_type], value)
            self.__SetHelper('SpeakerParametricFrequency', SpeakerParametricFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerParametricFrequency')

    def UpdateSpeakerParametricFrequency(self, value, qualifier):

        TypeStates = {
            'High': '6',
            'Low':  '8'
        }

        name = qualifier['Name']
        _type = qualifier['Type']

        if name and _type in TypeStates:
            SpeakerParametricFrequencyCmdString = 'GA"{}">0>{}\r'.format(name, TypeStates[_type])
            res = self.parse(self.__UpdateHelper('SpeakerParametricFrequency', SpeakerParametricFrequencyCmdString, value, qualifier))
            if res:
                try:
                    value = int(float(res))
                    self.WriteStatus('SpeakerParametricFrequency', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Speaker Parametric Frequency: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerParametricFrequency')

    def SetSpeakerParametricGain(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if name and -15.0 <= value <= 15.0:
            SpeakerParametricGainCmdString = 'SA"{}">0>3={:.1f}\r'.format(name, value)
            self.__SetHelper('SpeakerParametricGain', SpeakerParametricGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerParametricGain')

    def UpdateSpeakerParametricGain(self, value, qualifier):

        name = qualifier['Name']

        if name:
            SpeakerParametricGainCmdString = 'GA"{}">0>3\r'.format(name)
            res = self.parse(self.__UpdateHelper('SpeakerParametricGain', SpeakerParametricGainCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('SpeakerParametricGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Speaker Parametric Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeakerParametricGain')

    def SetStandardMixerLevel(self, value, qualifier):

        Index1States = {
            'Input':    '1',
            'Output':   '2'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        index2 = qualifier['Index 2']
        value = float('{:.1f}'.format(value))

        if name and index1 in Index1States and 1 <= int(index2) <= 32 and -60.5 <= value <= 12.0:
            index2 = (int(index2) * 2) - 1
            StandardMixerLevelCmdString = 'SA"{}">{}>{}={:.1f}\r'.format(name, Index1States[index1], index2, value)
            self.__SetHelper('StandardMixerLevel', StandardMixerLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandardMixerLevel')

    def UpdateStandardMixerLevel(self, value, qualifier):

        Index1States = {
            'Input':    '1',
            'Output':   '2'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        index2 = qualifier['Index 2']

        if name and index1 in Index1States and 1 <= int(index2) <= 32:
            index2 = (int(index2) * 2) - 1
            StandardMixerLevelCmdString = 'GA"{}">{}>{}\r'.format(name, Index1States[index1], index2)
            res = self.parse(self.__UpdateHelper('StandardMixerLevel', StandardMixerLevelCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('StandardMixerLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Standard Mixer Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateStandardMixerLevel')

    def SetStandardMixerMute(self, value, qualifier):

        Index1States = {
            'Input':    '1',
            'Output':   '2'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        index2 = qualifier['Index 2']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and index1 in Index1States and 1 <= int(index2) <= 32 and value in ValueStateValues:
            index2 = int(index2) * 2
            StandardMixerMuteCmdString = 'SA"{}">{}>{}={}\r'.format(name, Index1States[index1], index2, ValueStateValues[value])
            self.__SetHelper('StandardMixerMute', StandardMixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandardMixerMute')

    def UpdateStandardMixerMute(self, value, qualifier):

        Index1States = {
            'Input':    '1',
            'Output':   '2'
        }

        name = qualifier['Name']
        index1 = qualifier['Index 1']
        index2 = qualifier['Index 2']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and index1 in Index1States and 1 <= int(index2) <= 32:
            index2 = int(index2) * 2
            StandardMixerMuteCmdString = 'GA"{}">{}>{}\r'.format(name, Index1States[index1], index2)
            res = self.parse(self.__UpdateHelper('StandardMixerMute', StandardMixerMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('StandardMixerMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Standard Mixer Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateStandardMixerMute')

    def SetStandardMixerRouting(self, value, qualifier):

        name = qualifier['Name']
        _input = qualifier['Input']
        output = qualifier['Output']

        ValueStateValues = {
            'Route':    'O',
            'Unroute':  'F'
        }

        if name and 1 <= int(_input) <= 32 and 1 <= int(output) <= 32 and value in ValueStateValues:
            StandardMixerRoutingCmdString = 'SA"{}">4>({},{})={}\r'.format(name, _input, output, ValueStateValues[value])
            self.__SetHelper('StandardMixerRouting', StandardMixerRoutingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandardMixerRouting')

    def UpdateStandardMixerRouting(self, value, qualifier):

        name = qualifier['Name']
        _input = qualifier['Input']
        output = qualifier['Output']

        ValueStateValues = {
            'O': 'Route',
            'F': 'Unroute'
        }

        if name and 1 <= int(_input) <= 32 and 1 <= int(output) <= 32:
            StandardMixerRoutingCmdString = 'GA"{}">4>({},{})\r'.format(name, _input, output)
            res = self.parse(self.__UpdateHelper('StandardMixerRouting', StandardMixerRoutingCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('StandardMixerRouting', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Standard Mixer Routing: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateStandardMixerRouting')

    def SetToneControlGain(self, value, qualifier):

        TypeStates = {
            'Low':  '1',
            'Mid':  '3',
            'High': '5'
        }

        name = qualifier['Name']
        _type = qualifier['Type']
        value = float('{:.1f}'.format(value))

        if name and _type in TypeStates and -15.0 <= value <= 15.0:
            ToneControlGainCmdString = 'SA"{}">{}={:.1f}\r'.format(name, TypeStates[_type], value)
            self.__SetHelper('ToneControlGain', ToneControlGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetToneControlGain')

    def UpdateToneControlGain(self, value, qualifier):

        TypeStates = {
            'Low':  '1',
            'Mid':  '3',
            'High': '5'
        }

        name = qualifier['Name']
        _type = qualifier['Type']

        if name and _type in TypeStates:
            ToneControlGainCmdString = 'GA"{}">{}\r'.format(name, TypeStates[_type])
            res = self.parse(self.__UpdateHelper('ToneControlGain', ToneControlGainCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    self.WriteStatus('ToneControlGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Tone Control Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateToneControlGain')

    def SetUSBLevel(self, value, qualifier):

        ChannelStates = {
            'Left':     '1',
            'Right':    '2'
        }

        name = qualifier['Name']
        channel = qualifier['Channel']
        value = float('{:.1f}'.format(value))

        if name and channel in ChannelStates and -60.5 <= value <= 12.0:
            USBLevelCmdString = 'SA"{}">{}>1={:.1f}\r'.format(name, ChannelStates[channel], value)
            self.__SetHelper('USBLevel', USBLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBLevel')

    def UpdateUSBLevel(self, value, qualifier):

        ChannelStates = {
            'Left':     '1',
            'Right':    '2'
        }

        name = qualifier['Name']
        channel = qualifier['Channel']

        if name and channel in ChannelStates:
            USBLevelCmdString = 'GA"{}">{}>1\r'.format(name, ChannelStates[channel])
            res = self.parse(self.__UpdateHelper('USBLevel', USBLevelCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('USBLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['USB Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateUSBLevel')

    def SetUSBMute(self, value, qualifier):

        ChannelStates = {
            'Left':     '1',
            'Right':    '2'
        }

        name = qualifier['Name']
        channel = qualifier['Channel']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and channel in ChannelStates and value in ValueStateValues:
            USBMuteCmdString = 'SA"{}">{}>2={}\r'.format(name, ChannelStates[channel], ValueStateValues[value])
            self.__SetHelper('USBMute', USBMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBMute')

    def UpdateUSBMute(self, value, qualifier):

        ChannelStates = {
            'Left':     '1',
            'Right':    '2'
        }

        name = qualifier['Name']
        channel = qualifier['Channel']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name and channel in ChannelStates:
            USBMuteCmdString = 'GA"{}">{}>2\r'.format(name, ChannelStates[channel])
            res = self.parse(self.__UpdateHelper('USBMute', USBMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('USBMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['USB Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateUSBMute')

    def SetVoIPAction(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'Make Call':        '2',
            'End Call':         '3',
            'Answer Call':      '4',
            'Transfer Call':    '5'
        }

        dial_string = qualifier['Dial String']

        if name and value in ValueStateValues:
            if value in {'Make Call', 'Transfer Call'}:
                if dial_string:
                    VoIPActionCmdString = 'MA"{}">{}="{}"\r'.format(name, ValueStateValues[value], dial_string)
                else:
                    self.Discard('Invalid Command for SetVoIPAction')
                    return
            else:
                VoIPActionCmdString = 'MA"{}">{}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('VoIPAction', VoIPActionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoIPAction')
    def UpdateVoIPCallActive(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name:
            VoIPCallActiveCmdString = 'GA"{}">0>6\r'.format(name)
            res = self.parse(self.__UpdateHelper('VoIPCallActive', VoIPCallActiveCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('VoIPCallActive', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['VoIP Call Active: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVoIPCallActive')

    def UpdateVoIPCallerID(self, value, qualifier):

        name = qualifier['Name']

        if name:

            VoIPCallerIDCmdString = 'GA"{}">0>2\r'.format(name)
            res = self.parse(self.__UpdateHelper('VoIPCallerID', VoIPCallerIDCmdString, value, qualifier))
            if res:
                try:
                    res = res.split('<')
                    self.WriteStatus('VoIPCallerID', res[0][1:].strip(),     {'Name': name, 'Type': 'Name'})
                    self.WriteStatus('VoIPCallerID', res[1][:-2].strip(),     {'Name': name, 'Type': 'Hostname'})
                except (ValueError, IndexError):
                    self.Error(['VoIP Caller ID: Invalid/unexpected response'])
        else:
            self.Discard('Device Is Busy for UpdateVoIPCallerID')

    def UpdateVoIPCallStatus(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            '"INCOMING"':       'Incoming',
            '"DIALING"':        'Dialing',
            '"RINGBACK"':       'Ringback',
            '"ACTIVE"':         'Active',
            '"HANGUP"':         'Hangup',
            '"HOLD_STATE_PEER"': 'Hold State Peer'
        }

        if name:
            VoIPCallStatusCmdString = 'GA"{}">0>1\r'.format(name)
            res = self.parse(self.__UpdateHelper('VoIPCallStatus', VoIPCallStatusCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('VoIPCallStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['VoIP Call Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVoIPCallStatus')

    def SetVoIPDialKey(self, value, qualifier):

        name = qualifier['Name']

        if name and value in '0123456789#*':
            VoIPDialKeyCmdString = 'MA"{}">1={}\r'.format(name, value)
            self.__SetHelper('VoIPDialKey', VoIPDialKeyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoIPDialKey')
    def SetVoIPLevel(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if name and -60.5 <= value <= 12.0:
            VoIPLevelCmdString = 'SA"{}">1>1={:.1f}\r'.format(name, value)
            self.__SetHelper('VoIPLevel', VoIPLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoIPLevel')

    def UpdateVoIPLevel(self, value, qualifier):

        name = qualifier['Name']

        if name:
            VoIPLevelCmdString = 'GA"{}">1>1\r'.format(name)
            res = self.parse(self.__UpdateHelper('VoIPLevel', VoIPLevelCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('VoIPLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['VoIP Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVoIPLevel')

    def SetVoIPMute(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and value in ValueStateValues:
            VoIPMuteCmdString = 'SA"{}">1>2={}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('VoIPMute', VoIPMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoIPMute')

    def UpdateVoIPMute(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name:
            VoIPMuteCmdString = 'GA"{}">1>2\r'.format(name)
            res = self.parse(self.__UpdateHelper('VoIPMute', VoIPMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('VoIPMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['VoIP Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVoIPMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        error_map = {
            '\x1501': 'Invalid Module Name (no match found for module name - or duplicate name)',
            '\x1502': 'Illegal Index (index value or quantity incorrect for specific module)',
            '\x1503': 'Value is out-of-range (value is not permitted for the specified parameter)',
            '\x1599': 'Unknown error'
        }
        if response:
            response = response.decode()
            if response and response in error_map:
                self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, error_map[response])])
                response = ''
    
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or command == 'UserDefinedCommand' or command in {'GroupLevel', 'GroupMute', 'ParameterRecall'}:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.set_regex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.get_regex)
            return self.__CheckResponseForErrors(command, res)
     
            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.lastPTSNCallerIDUpdate = defaultdict(float)
        self.lastVoIPCallerIDUpdate = defaultdict(float)
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

