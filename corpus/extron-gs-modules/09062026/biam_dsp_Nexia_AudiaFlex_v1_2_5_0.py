from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
import copy


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
            'Audia': self.biam_25_149_A,
            'Nexia': self.biam_25_149_N,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AECEnable': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'AECInputGain': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'AECInputLevel': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'AECInputMute': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'AutomixerCrosspointMute': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'AutomixerInputLevel': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'AutomixerInputMute': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'AutomixerOutputLevel': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'AutomixerOutputMute': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'FaderLevel': {'Parameters': ['Device Number', 'Instance ID', 'Channel'], 'Status': {}},
            'FaderMute': {'Parameters': ['Device Number', 'Instance ID', 'Channel'], 'Status': {}},
            'IOInputGain': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'IOInputLevel': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'IOInputMute': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'IOOutputLevel': {'Parameters': ['Device Number', 'Instance ID', 'Output'], 'Status': {}},
            'IOOutputMute': {'Parameters': ['Device Number', 'Instance ID', 'Output'], 'Status': {}},
            'LogicMeter': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'LogicState': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'MatrixMixerCrosspointLevel': {'Parameters': ['Device Number', 'Instance ID', 'Input', 'Output'], 'Status': {}},
            'MatrixMixerCrosspointMute': {'Parameters': ['Device Number', 'Instance ID', 'Input', 'Output'], 'Status': {}},
            'MatrixMixerInputLevel': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'MatrixMixerInputMute': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'MatrixMixerOutputLevel': {'Parameters': ['Device Number', 'Instance ID', 'Output'], 'Status': {}},
            'MatrixMixerOutputMute': {'Parameters': ['Device Number', 'Instance ID', 'Output'], 'Status': {}},
            'MuteBlock': {'Parameters': ['Device Number', 'Instance ID', 'Channel'], 'Status': {}},
            'IPAddress': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'RoomCombineOutputLevel': {'Parameters': ['Device Number', 'Instance ID', 'Output'], 'Status': {}},
            'RoomCombineOutputMute': {'Parameters': ['Device Number', 'Instance ID', 'Output'], 'Status': {}},
            'RoomCombineWall': {'Parameters': ['Device Number', 'Instance ID', 'Wall'], 'Status': {}},
            'RouterCrosspointMute': {'Parameters': ['Device Number', 'Instance ID', 'Input', 'Output'], 'Status': {}},
            'SourceSelectionSource': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'StandardMixerCrosspointMute': {'Parameters': ['Device Number', 'Instance ID', 'Input', 'Output'], 'Status': {}},
            'StandardMixerInputLevel': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'StandardMixerInputMute': {'Parameters': ['Device Number', 'Instance ID', 'Input'], 'Status': {}},
            'StandardMixerOutputLevel': {'Parameters': ['Device Number', 'Instance ID', 'Output'], 'Status': {}},
            'StandardMixerOutputMute': {'Parameters': ['Device Number', 'Instance ID', 'Output'], 'Status': {}},
            'TIAutoAnswer': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'TICallerID': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'TIDTMF': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'TIHook': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'TILastNumber': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'TIPhoneEchoCancellation': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'TIPhoneReceiveLevel': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'TIPhoneReceiveMute': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'TIPhoneTransmitLevel': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'TIPhoneTransmitMute': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'TISpeedDial': {'Parameters': ['Device Number', 'Instance ID'], 'Status': {}},
            'VoIPAutoAnswer': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
            'VoIPCallerID': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
            'VoIPDTMF': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
            'VoIPHook': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
            'VoIPLastNumber': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
            'VoIPReceiveLevel': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
            'VoIPReceiveMute': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
            'VoIPRingIndicator': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
            'VoIPSpeedDial': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
            'VoIPTransmitLevel': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
            'VoIPTransmitMute': {'Parameters': ['Device Number', 'Instance ID', 'Line'], 'Status': {}},
        }

        self.__matchList = []
        self.TIRedialString = {}
        self.VoIPRedialString = {}

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Welcome to the Biamp Telnet server'), self.__MatchWelcome, None)
            self.AddMatchString(compile(b'#GETD 0 IPADDR ([.0-9]+)\r\n'), self.__MatchIPAddress, None)
            self.AddMatchString(compile(b'-ERR:(.+)'), self.__MatchError, None)

    def __MatchWelcome(self, match, tag):
        self.SetEchoOff()

    def SetEchoOff(self):
        self.Send(b'\xFF\xFE\x01')

    def SetAECEnable(self, value, qualifier):

        InputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }

        if 'AECEnable' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AECENABLE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchAECEnable, None)
            self.__matchList.append('AECEnable')

        InputMuteCmdString = 'SETD {0} AECENABLE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], InputMuteStateValues[value])
        self.__SetHelper('AECEnable', InputMuteCmdString, value, qualifier)

    def UpdateAECEnable(self, value, qualifier):

        if 'AECEnable' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AECENABLE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchAECEnable, None)
            self.__matchList.append('AECEnable')

        InputMuteCmdString = 'GETD {0} AECENABLE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('AECEnable', InputMuteCmdString, value, qualifier)

    def __MatchAECEnable(self, match, tag):

        InputMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = InputMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('AECEnable', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetAECInputGain(self, value, qualifier):

        GainConstraints = {
            'Min': 0,
            'Max': 66
        }
        if value < GainConstraints['Min'] or value > GainConstraints['Max']:
            self.Discard('Invalid Command for SetAECInputGain')
        else:
            if 'AECInputGain' not in self.__matchList:
                self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AECMICGAIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchAECInputGain, None)
                self.__matchList.append('AECInputGain')

            InputGainCmdString = 'SETD {0} AECMICGAIN {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], value)
            self.__SetHelper('AECInputGain', InputGainCmdString, value, qualifier)

    def UpdateAECInputGain(self, value, qualifier):

        if 'AECInputGain' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AECMICGAIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchAECInputGain, None)
            self.__matchList.append('AECInputGain')

        InputGainCmdString = 'GETD {0} AECMICGAIN {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('AECInputGain', InputGainCmdString, value, qualifier)

    def __MatchAECInputGain(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('AECInputGain', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetAECInputLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetAECInputLevel')
        else:
            if 'AECInputLevel' not in self.__matchList:
                self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AECINPLVL ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchAECInputLevel, None)
                self.__matchList.append('AECInputLevel')

            InputLevelCmdString = 'SETD {0} AECINPLVL {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], value)
            self.__SetHelper('AECInputLevel', InputLevelCmdString, value, qualifier)

    def UpdateAECInputLevel(self, value, qualifier):

        if 'AECInputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AECINPLVL ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchAECInputLevel, None)
            self.__matchList.append('AECInputLevel')

        InputLevelCmdString = 'GETD {0} AECINPLVL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('AECInputLevel', InputLevelCmdString, value, qualifier)

    def __MatchAECInputLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('AECInputLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetAECInputMute(self, value, qualifier):

        InputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'AECInputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AECINPMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchAECInputMute, None)
            self.__matchList.append('AECInputMute')

        InputMuteCmdString = 'SETD {0} AECINPMUTE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], InputMuteStateValues[value])
        self.__SetHelper('AECInputMute', InputMuteCmdString, value, qualifier)

    def UpdateAECInputMute(self, value, qualifier):

        if 'AECInputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AECINPMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchAECInputMute, None)
            self.__matchList.append('AECInputMute')

        InputMuteCmdString = 'GETD {0} AECINPMUTE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('AECInputMute', InputMuteCmdString, value, qualifier)

    def __MatchAECInputMute(self, match, tag):

        InputMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        value = InputMuteStateNames[match.group(5)]
        self.WriteStatus('AECInputMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetAutomixerCrosspointMute(self, value, qualifier):

        CrosspointMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'AutomixerCrosspointMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AMMUTEXP ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchAutomixerCrosspointMute, None)
            self.__matchList.append('AutomixerCrosspointMute')

        CrosspointMuteCmdString = 'SETD {0} AMMUTEXP {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], CrosspointMuteStateValues[value])
        self.__SetHelper('AutomixerCrosspointMute', CrosspointMuteCmdString, value, qualifier)

    def UpdateAutomixerCrosspointMute(self, value, qualifier):

        if 'AutomixerCrosspointMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AMMUTEXP ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchAutomixerCrosspointMute, None)
            self.__matchList.append('AutomixerCrosspointMute')

        CrosspointMuteCmdString = 'GETD {0} AMMUTEXP {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('AutomixerCrosspointMute', CrosspointMuteCmdString, value, qualifier)

    def __MatchAutomixerCrosspointMute(self, match, tag):

        CrosspointMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = CrosspointMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('AutomixerCrosspointMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetAutomixerInputLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'AutomixerInputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AMLVLIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchAutomixerInputLevel, None)
            self.__matchList.append('AutomixerInputLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetAutomixerInputLevel')
        else:
            InputLevelCmdString = 'SETD {0} AMLVLIN {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], value)
            self.__SetHelper('AutomixerInputLevel', InputLevelCmdString, value, qualifier)

    def UpdateAutomixerInputLevel(self, value, qualifier):

        if 'AutomixerInputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AMLVLIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchAutomixerInputLevel, None)
            self.__matchList.append('AutomixerInputLevel')

        InputLevelCmdString = 'GETD {0} AMLVLIN {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('AutomixerInputLevel', InputLevelCmdString, value, qualifier)

    def __MatchAutomixerInputLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('AutomixerInputLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetAutomixerInputMute(self, value, qualifier):

        InputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'AutomixerInputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AMMUTEIN ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchAutomixerInputMute, None)
            self.__matchList.append('AutomixerInputMute')

        InputMuteCmdString = 'SETD {0} AMMUTEIN {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], InputMuteStateValues[value])
        self.__SetHelper('AutomixerInputMute', InputMuteCmdString, value, qualifier)

    def UpdateAutomixerInputMute(self, value, qualifier):

        if 'AutomixerInputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AMMUTEIN ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchAutomixerInputMute, None)
            self.__matchList.append('AutomixerInputMute')

        InputMuteCmdString = 'GETD {0} AMMUTEIN {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('AutomixerInputMute', InputMuteCmdString, value, qualifier)

    def __MatchAutomixerInputMute(self, match, tag):

        InputMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = InputMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('AutomixerInputMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetAutomixerOutputLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'AutomixerOutputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AMLVLOUT ([^<&>\'. ]+) (-?\d+)\.\d{6} '), self.__MatchAutomixerOutputLevel, None)
            self.__matchList.append('AutomixerOutputLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetAutomixerOutputLevel')
        else:
            OutputLevelCmdString = 'SETD {0} AMLVLOUT {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], value)
            self.__SetHelper('AutomixerOutputLevel', OutputLevelCmdString, value, qualifier)

    def UpdateAutomixerOutputLevel(self, value, qualifier):

        if 'AutomixerOutputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AMLVLOUT ([^<&>\'. ]+) (-?\d+)\.\d{6} '), self.__MatchAutomixerOutputLevel, None)
            self.__matchList.append('AutomixerOutputLevel')

        OutputLevelCmdString = 'GETD {0} AMLVLOUT {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('AutomixerOutputLevel', OutputLevelCmdString, value, qualifier)

    def __MatchAutomixerOutputLevel(self, match, tag):

        value = int(match.group(4))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        self.WriteStatus('AutomixerOutputLevel', value, {'Device Number': devNum, 'Instance ID': instID})

    def SetAutomixerOutputMute(self, value, qualifier):

        OutputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'AutomixerOutputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AMMUTEOUT ([^<&>\'. ]+) ([01]) '), self.__MatchAutomixerOutputMute, None)
            self.__matchList.append('AutomixerOutputMute')

        OutputMuteCmdString = 'SETD {0} AMMUTEOUT {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], OutputMuteStateValues[value])
        self.__SetHelper('AutomixerOutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateAutomixerOutputMute(self, value, qualifier):

        if 'AutomixerOutputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) AMMUTEOUT ([^<&>\'. ]+) ([01]) '), self.__MatchAutomixerOutputMute, None)
            self.__matchList.append('AutomixerOutputMute')

        OutputMuteCmdString = 'GETD {0} AMMUTEOUT {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('AutomixerOutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchAutomixerOutputMute(self, match, tag):

        OutpuMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = OutpuMuteStateNames[match.group(4)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        self.WriteStatus('AutomixerOutputMute', value, {'Device Number': devNum, 'Instance ID': instID})

    def SetFaderLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'FaderLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) FDRLVL ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchFaderLevel, None)
            self.__matchList.append('FaderLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetFaderLevel')
        else:
            FaderLevelCmdString = 'SETD {0} FDRLVL {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Channel'], value)
            self.__SetHelper('FaderLevel', FaderLevelCmdString, value, qualifier)

    def UpdateFaderLevel(self, value, qualifier):

        if 'FaderLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) FDRLVL ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchFaderLevel, None)
            self.__matchList.append('FaderLevel')

        FaderLevelCmdString = 'GETD {0} FDRLVL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Channel'])
        self.__UpdateHelper('FaderLevel', FaderLevelCmdString, value, qualifier)

    def __MatchFaderLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('FaderLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Channel': input_})

    def SetFaderMute(self, value, qualifier):

        FaderMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'FaderMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) FDRMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchFaderMute, None)
            self.__matchList.append('FaderMute')

        FaderMuteCmdString = 'SETD {0} FDRMUTE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Channel'], FaderMuteStateValues[value])
        self.__SetHelper('FaderMute', FaderMuteCmdString, value, qualifier)

    def UpdateFaderMute(self, value, qualifier):

        if 'FaderMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) FDRMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchFaderMute, None)
            self.__matchList.append('FaderMute')

        FaderMuteCmdString = 'GETD {0} FDRMUTE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Channel'])
        self.__UpdateHelper('FaderMute', FaderMuteCmdString, value, qualifier)

    def __MatchFaderMute(self, match, tag):

        FaderMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = FaderMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('FaderMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Channel': input_})

    def SetIOInputGain(self, value, qualifier):

        GainConstraints = {
            'Min': 0,
            'Max': 66
        }
        if 'IOInputGain' not in self.__matchList:
            if self.Model == 'Audia':
                self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MICGAIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchIOInputGain, None)
            else:
                self.AddMatchString(compile(b'#(SETD|GETD) (\d+) INPGAIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchIOInputGain, None)
            self.__matchList.append('IOInputGain')

        if value < GainConstraints['Min'] or value > GainConstraints['Max']:
            self.Discard('Invalid Command for SetIOInputGain')
        else:
            attribute = 'MICGAIN' if self.Model == 'Audia' else 'INPGAIN'
            InputGainCmdString = 'SETD {0} {4} {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], value, attribute)
            self.__SetHelper('IOInputGain', InputGainCmdString, value, qualifier)

    def UpdateIOInputGain(self, value, qualifier):

        if 'IOInputGain' not in self.__matchList:
            if self.Model == 'Audia':
                self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MICGAIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchIOInputGain, None)
            else:
                self.AddMatchString(compile(b'#(SETD|GETD) (\d+) INPGAIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchIOInputGain, None)
            self.__matchList.append('IOInputGain')

        attribute = 'MICGAIN' if self.Model == 'Audia' else 'INPGAIN'
        InputGainCmdString = 'GETD {0} {3} {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], attribute)
        self.__UpdateHelper('IOInputGain', InputGainCmdString, value, qualifier)

    def __MatchIOInputGain(self, match, tag):
        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('IOInputGain', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetIOInputLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'IOInputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) INPLVL ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchIOInputLevel, None)
            self.__matchList.append('IOInputLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetIOInputLevel')
        else:
            InputLevelCmdString = 'SETD {0} INPLVL {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], value)
            self.__SetHelper('IOInputLevel', InputLevelCmdString, value, qualifier)

    def UpdateIOInputLevel(self, value, qualifier):

        if 'IOInputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) INPLVL ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchIOInputLevel, None)
            self.__matchList.append('IOInputLevel')

        InputLevelCmdString = 'GETD {0} INPLVL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('IOInputLevel', InputLevelCmdString, value, qualifier)

    def __MatchIOInputLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('IOInputLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetIOInputMute(self, value, qualifier):

        InputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'IOInputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) INPMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchIOInputMute, None)
            self.__matchList.append('IOInputMute')

        InputMuteCmdString = 'SETD {0} INPMUTE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], InputMuteStateValues[value])
        self.__SetHelper('IOInputMute', InputMuteCmdString, value, qualifier)

    def UpdateIOInputMute(self, value, qualifier):

        if 'IOInputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) INPMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchIOInputMute, None)
            self.__matchList.append('IOInputMute')

        InputMuteCmdString = 'GETD {0} INPMUTE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('IOInputMute', InputMuteCmdString, value, qualifier)

    def __MatchIOInputMute(self, match, tag):

        InputMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = InputMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('IOInputMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetIOOutputLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 0
        }
        if 'IOOutputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) OUTLVL ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchIOOutputLevel, None)
            self.__matchList.append('IOOutputLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetIOOutputLevel')
        else:
            OutputLevelCmdString = 'SETD {0} OUTLVL {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'], value)
            self.__SetHelper('IOOutputLevel', OutputLevelCmdString, value, qualifier)

    def UpdateIOOutputLevel(self, value, qualifier):

        if 'IOOutputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) OUTLVL ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchIOOutputLevel, None)
            self.__matchList.append('IOOutputLevel')

        OutputLevelCmdString = 'GETD {0} OUTLVL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'])
        self.__UpdateHelper('IOOutputLevel', OutputLevelCmdString, value, qualifier)

    def __MatchIOOutputLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        Output = str(int(match.group(4)))
        self.WriteStatus('IOOutputLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Output': Output})

    def SetIOOutputMute(self, value, qualifier):

        OutputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'IOOutputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) OUTMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchIOOutputMute, None)
            self.__matchList.append('IOOutputMute')

        OutputMuteCmdString = 'SETD {0} OUTMUTE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'], OutputMuteStateValues[value])
        self.__SetHelper('IOOutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateIOOutputMute(self, value, qualifier):

        if 'IOOutputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) OUTMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchIOOutputMute, None)
            self.__matchList.append('IOOutputMute')

        OutputMuteCmdString = 'GETD {0} OUTMUTE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'])
        self.__UpdateHelper('IOOutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchIOOutputMute(self, match, tag):

        OutputMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = OutputMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        Output = str(int(match.group(4)))
        self.WriteStatus('IOOutputMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Output': Output})

    def UpdateLogicMeter(self, value, qualifier):

        if 'LogicMeter' not in self.__matchList:
            self.AddMatchString(compile(b'#(GETD) (\d+) LGCMTRSTATE ([^<&>\'. ]+) (\d+) (0|1) '), self.__MatchLogicMeter, None)
            self.__matchList.append('LogicMeter')

        cmdString = 'GETD {0} LGCMTRSTATE {1} {2} \n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('LogicMeter', cmdString, value, qualifier)

    def __MatchLogicMeter(self, match, tag):

        value = match.group(5).decode()
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        output = str(int(match.group(4)))
        self.WriteStatus('LogicMeter', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': output})

    def SetLogicState(self, value, qualifier):

        if 'LogicState' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) LGSTATE ([^<&>\'. ]+) (\d+) (0|1) '), self.__MatchLogicState, None)
            self.__matchList.append('LogicState')

        cmdString = 'SETD {0} LGSTATE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], value)
        self.__SetHelper('LogicState', cmdString, value, qualifier)

    def UpdateLogicState(self, value, qualifier):

        if 'LogicState' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) LGSTATE ([^<&>\'. ]+) (\d+) (0|1) '), self.__MatchLogicState, None)
            self.__matchList.append('LogicState')

        cmdString = 'GETD {0} LGSTATE {1} {2} \n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('LogicState', cmdString, value, qualifier)

    def __MatchLogicState(self, match, tag):

        value = match.group(5).decode()
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('LogicState', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetMatrixMixerCrosspointLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 0
        }
        if 'MatrixMixerCrosspointLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMLVLXP ([^<&>\'. ]+) (\d+) (\d+) (-?\d+)\.\d{6} '), self.__MatchMatrixMixerCrosspointLevel, None)
            self.__matchList.append('MatrixMixerCrosspointLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetMatrixMixerCrosspointLevel')
        else:
            CrosspointLevelCmdString = 'SETD {0} MMLVLXP {1} {2} {3} {4}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], qualifier['Output'], value)
            self.__SetHelper('MatrixMixerCrosspointLevel', CrosspointLevelCmdString, value, qualifier)

    def UpdateMatrixMixerCrosspointLevel(self, value, qualifier):

        if 'MatrixMixerCrosspointLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMLVLXP ([^<&>\'. ]+) (\d+) (\d+) (-?\d+)\.\d{6} '), self.__MatchMatrixMixerCrosspointLevel, None)
            self.__matchList.append('MatrixMixerCrosspointLevel')

        CrosspointLevelCmdString = 'GETD {0} MMLVLXP {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], qualifier['Output'])
        self.__UpdateHelper('MatrixMixerCrosspointLevel', CrosspointLevelCmdString, value, qualifier)

    def __MatchMatrixMixerCrosspointLevel(self, match, tag):

        value = int(match.group(6))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        output = str(int(match.group(5)))
        self.WriteStatus('MatrixMixerCrosspointLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_, 'Output': output})

    def SetMatrixMixerCrosspointMute(self, value, qualifier):

        CrosspointMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'MatrixMixerCrosspointMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMMUTEXP ([^<&>\'. ]+) (\d+) (\d+) ([01]) '), self.__MatchMatrixMixerCrosspointMute, None)
            self.__matchList.append('MatrixMixerCrosspointMute')

        CrosspointMuteCmdString = 'SETD {0} MMMUTEXP {1} {2} {3} {4}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], qualifier['Output'], CrosspointMuteStateValues[value])
        self.__SetHelper('MatrixMixerCrosspointMute', CrosspointMuteCmdString, value, qualifier)

    def UpdateMatrixMixerCrosspointMute(self, value, qualifier):

        if 'MatrixMixerCrosspointMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMMUTEXP ([^<&>\'. ]+) (\d+) (\d+) ([01]) '), self.__MatchMatrixMixerCrosspointMute, None)
            self.__matchList.append('MatrixMixerCrosspointMute')

        CrosspointMuteCmdString = 'GETD {0} MMMUTEXP {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], qualifier['Output'])
        self.__UpdateHelper('MatrixMixerCrosspointMute', CrosspointMuteCmdString, value, qualifier)

    def __MatchMatrixMixerCrosspointMute(self, match, tag):

        CrosspointMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = CrosspointMuteStateNames[match.group(6)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        output = str(int(match.group(5)))
        self.WriteStatus('MatrixMixerCrosspointMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_, 'Output': output})

    def SetMatrixMixerInputLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'MatrixMixerInputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMLVLIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchMatrixMixerInputLevel, None)
            self.__matchList.append('MatrixMixerInputLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetMatrixMixerInputLevel')
        else:
            InputLevelCmdString = 'SETD {0} MMLVLIN {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], value)
            self.__SetHelper('MatrixMixerInputLevel', InputLevelCmdString, value, qualifier)

    def UpdateMatrixMixerInputLevel(self, value, qualifier):

        if 'MatrixMixerInputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMLVLIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchMatrixMixerInputLevel, None)
            self.__matchList.append('MatrixMixerInputLevel')

        InputLevelCmdString = 'GETD {0} MMLVLIN {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('MatrixMixerInputLevel', InputLevelCmdString, value, qualifier)

    def __MatchMatrixMixerInputLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('MatrixMixerInputLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetMatrixMixerInputMute(self, value, qualifier):

        InputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'MatrixMixerInputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMMUTEIN ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchMatrixMixerInputMute, None)
            self.__matchList.append('MatrixMixerInputMute')

        InputMuteCmdString = 'SETD {0} MMMUTEIN {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], InputMuteStateValues[value])
        self.__SetHelper('MatrixMixerInputMute', InputMuteCmdString, value, qualifier)

    def UpdateMatrixMixerInputMute(self, value, qualifier):

        if 'MatrixMixerInputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMMUTEIN ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchMatrixMixerInputMute, None)
            self.__matchList.append('MatrixMixerInputMute')

        InputMuteCmdString = 'GETD {0} MMMUTEIN {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('MatrixMixerInputMute', InputMuteCmdString, value, qualifier)

    def __MatchMatrixMixerInputMute(self, match, tag):

        InputMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = InputMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('MatrixMixerInputMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetMatrixMixerOutputLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'MatrixMixerOutputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMLVLOUT ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchMatrixMixerOutputLevel, None)
            self.__matchList.append('MatrixMixerOutputLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetMatrixMixerOutputLevel')
        else:
            OutputLevelCmdString = 'SETD {0} MMLVLOUT {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'], value)
            self.__SetHelper('MatrixMixerOutputLevel', OutputLevelCmdString, value, qualifier)

    def UpdateMatrixMixerOutputLevel(self, value, qualifier):

        if 'MatrixMixerOutputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMLVLOUT ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchMatrixMixerOutputLevel, None)
            self.__matchList.append('MatrixMixerOutputLevel')

        OutputLevelCmdString = 'GETD {0} MMLVLOUT {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'])
        self.__UpdateHelper('MatrixMixerOutputLevel', OutputLevelCmdString, value, qualifier)

    def __MatchMatrixMixerOutputLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        Output = str(int(match.group(4)))
        self.WriteStatus('MatrixMixerOutputLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Output': Output})

    def SetMatrixMixerOutputMute(self, value, qualifier):

        OutputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'MatrixMixerOutputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMMUTEOUT ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchMatrixMixerOutputMute, None)
            self.__matchList.append('MatrixMixerOutputMute')

        OutputMuteCmdString = 'SETD {0} MMMUTEOUT {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'], OutputMuteStateValues[value])
        self.__SetHelper('MatrixMixerOutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateMatrixMixerOutputMute(self, value, qualifier):

        if 'MatrixMixerOutputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MMMUTEOUT ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchMatrixMixerOutputMute, None)
            self.__matchList.append('MatrixMixerOutputMute')

        OutputMuteCmdString = 'GETD {0} MMMUTEOUT {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'])
        self.__UpdateHelper('MatrixMixerOutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchMatrixMixerOutputMute(self, match, tag):

        OutputMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = OutputMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        Output = str(int(match.group(4)))
        self.WriteStatus('MatrixMixerOutputMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Output': Output})

    def SetMuteBlock(self, value, qualifier):

        MuteBlockStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'MuteBlock' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MBMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchMuteBlock, None)
            self.__matchList.append('MuteBlock')

        MuteBlockCmdString = 'SETD {0} MBMUTE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Channel'], MuteBlockStateValues[value])
        self.__SetHelper('MuteBlock', MuteBlockCmdString, value, qualifier)

    def UpdateMuteBlock(self, value, qualifier):

        if 'MuteBlock' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) MBMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchMuteBlock, None)
            self.__matchList.append('MuteBlock')

        MuteBlockCmdString = 'GETD {0} MBMUTE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Channel'])
        self.__UpdateHelper('MuteBlock', MuteBlockCmdString, value, qualifier)

    def __MatchMuteBlock(self, match, tag):

        MuteBlockStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = MuteBlockStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('MuteBlock', value, {'Device Number': devNum, 'Instance ID': instID, 'Channel': input_})

    def UpdateIPAddress(self, value, qualifier):

        self.__UpdateHelper('IPAddress', 'GETD 0 IPADDR\n', value, qualifier)

    def __MatchIPAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('IPAddress', value, None)

    def SetPresetRecall(self, value, qualifier):

        PresetConstraints = {
            'Min': 1001,
            'Max': 1128
        }
        if int(value) < PresetConstraints['Min'] or int(value) > PresetConstraints['Max']:
            self.Discard('Invalid Command for SetPresetRecall')
        else:
            PresetCmdString = 'RECALL 0 PRESET {0}\n'.format(value)
            self.__SetHelper('PresetRecall', PresetCmdString, value, qualifier)

    def SetRoomCombineOutputLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'RoomCombineOutputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) RMCMBLVL ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchRoomCombineOutputLevel, None)
            self.__matchList.append('RoomCombineOutputLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetRoomCombineOutputLevel')
        else:
            OutputLevelCmdString = 'SETD {0} RMCMBLVL {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'], value)
            self.__SetHelper('RoomCombineOutputLevel', OutputLevelCmdString, value, qualifier)

    def UpdateRoomCombineOutputLevel(self, value, qualifier):

        if 'RoomCombineOutputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) RMCMBLVL ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchRoomCombineOutputLevel, None)
            self.__matchList.append('RoomCombineOutputLevel')

        OutputLevelCmdString = 'GETD {0} RMCMBLVL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'])
        self.__UpdateHelper('RoomCombineOutputLevel', OutputLevelCmdString, value, qualifier)

    def __MatchRoomCombineOutputLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        Output = str(int(match.group(4)))
        self.WriteStatus('RoomCombineOutputLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Output': Output})

    def SetRoomCombineOutputMute(self, value, qualifier):

        OutputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'RoomCombineOutputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) RMCMBMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchRoomCombineOutputMute, None)
            self.__matchList.append('RoomCombineOutputMute')

        OutputMuteCmdString = 'SETD {0} RMCMBMUTE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'], OutputMuteStateValues[value])
        self.__SetHelper('RoomCombineOutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateRoomCombineOutputMute(self, value, qualifier):

        if 'RoomCombineOutputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) RMCMBMUTE ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchRoomCombineOutputMute, None)
            self.__matchList.append('RoomCombineOutputMute')

        OutputMuteCmdString = 'GETD {0} RMCMBMUTE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'])
        self.__UpdateHelper('RoomCombineOutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchRoomCombineOutputMute(self, match, tag):

        OutputMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = OutputMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        Output = str(int(match.group(4)))
        self.WriteStatus('RoomCombineOutputMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Output': Output})

    def SetRoomCombineWall(self, value, qualifier):

        RoomCombineWallStateValues = {
            'Closed': '1',
            'Open': '0',
        }
        if 'RoomCombineWall' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) RMCMBWALL ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchRoomCombineWall, None)
            self.__matchList.append('RoomCombineWall')

        RoomCombineWallCmdString = 'SETD {0} RMCMBWALL {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Wall'], RoomCombineWallStateValues[value])
        self.__SetHelper('RoomCombineWall', RoomCombineWallCmdString, value, qualifier)

    def UpdateRoomCombineWall(self, value, qualifier):

        if 'RoomCombineWall' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) RMCMBWALL ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchRoomCombineWall, None)
            self.__matchList.append('RoomCombineWall')

        RoomCombineWallCmdString = 'GETD {0} RMCMBWALL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Wall'])
        self.__UpdateHelper('RoomCombineWall', RoomCombineWallCmdString, value, qualifier)

    def __MatchRoomCombineWall(self, match, tag):

        RoomCombineWallStateNames = {
            b'1': 'Closed',
            b'0': 'Open'
        }

        value = RoomCombineWallStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        wall = str(int(match.group(4)))
        self.WriteStatus('RoomCombineWall', value, {'Device Number': devNum, 'Instance ID': instID, 'Wall': wall})

    def SetRouterCrosspointMute(self, value, qualifier):

        if 'RouterCrosspointMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) RTRMUTEXP ([^<&>\'. ]+) (\d+) (\d+) ([01]) '), self.__MatchRouterCrosspointMute, None)
            self.__matchList.append('RouterCrosspointMute')

        val = '1' if value == 'On' else '0'
        CrosspointMuteCmdString = 'SETD {0} RTRMUTEXP {1} {2} {3} {4}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], qualifier['Output'], val)
        self.__SetHelper('RouterCrosspointMute', CrosspointMuteCmdString, value, qualifier)

    def UpdateRouterCrosspointMute(self, value, qualifier):

        if 'RouterCrosspointMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) RTRMUTEXP ([^<&>\'. ]+) (\d+) (\d+) ([01]) '), self.__MatchRouterCrosspointMute, None)
            self.__matchList.append('RouterCrosspointMute')

        CrosspointMuteCmdString = 'GETD {0} RTRMUTEXP {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], qualifier['Output'])
        self.__UpdateHelper('RouterCrosspointMute', CrosspointMuteCmdString, value, qualifier)

    def __MatchRouterCrosspointMute(self, match, tag):

        statesName = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = statesName[match.group(6)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        output = str(int(match.group(5)))
        self.WriteStatus('RouterCrosspointMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_, 'Output': output})

    def SetSourceSelectionSource(self, value, qualifier):
        if 'SourceSelectionSource' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SRCSELSRC ([^<&>\'. ]+) 1 (\d{1,2}) '), self.__MatchSourceSelectionSource, None)
            self.__matchList.append('SourceSelectionSource')

        if value == 'None' or 1 <= int(value) <= 16:
            val = '0' if value == 'None' else value
            SourceSelectionSourceCmdString = 'SETD {0} SRCSELSRC {1} 1 {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], val)
            if self.__SafeToSet('SourceSelectionSource'):
                self.WriteSourceSelectionSource(value, qualifier, 'Emulated')
                self.__SetHelper('SourceSelectionSource', SourceSelectionSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSourceSelectionSource')

    def UpdateSourceSelectionSource(self, value, qualifier):
        if 'SourceSelectionSource' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SRCSELSRC ([^<&>\'. ]+) 1 (\d{1,2}) '), self.__MatchSourceSelectionSource, None)
            self.__matchList.append('SourceSelectionSource')

        SourceSelectionSourceCmdString = 'GETD {0} SRCSELSRC {1} 1\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('SourceSelectionSource', SourceSelectionSourceCmdString, value, qualifier)

    def __MatchSourceSelectionSource(self, match, tag):
        value = match.group(4).decode()
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()

        value = 'None' if value == '0' else value
        self.WriteStatus('SourceSelectionSource', value, {'Device Number': devNum, 'Instance ID': instID})

    def SetStandardMixerCrosspointMute(self, value, qualifier):

        CrosspointMuteStateValues = {
            'On': '0',
            'Off': '1',
        }
        if 'StandardMixerCrosspointMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SMMUTEXP ([^<&>\'. ]+) (\d+) (\d+) ([01]) '), self.__MatchStandardMixerCrosspointMute, None)
            self.__matchList.append('StandardMixerCrosspointMute')

        CrosspointMuteCmdString = 'SETD {0} SMMUTEXP {1} {2} {3} {4}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], qualifier['Output'], CrosspointMuteStateValues[value])
        self.__SetHelper('StandardMixerCrosspointMute', CrosspointMuteCmdString, value, qualifier)

    def UpdateStandardMixerCrosspointMute(self, value, qualifier):

        if 'StandardMixerCrosspointMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SMMUTEXP ([^<&>\'. ]+) (\d+) (\d+) ([01]) '), self.__MatchStandardMixerCrosspointMute, None)
            self.__matchList.append('StandardMixerCrosspointMute')

        CrosspointMuteCmdString = 'GETD {0} SMMUTEXP {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], qualifier['Output'])
        self.__UpdateHelper('StandardMixerCrosspointMute', CrosspointMuteCmdString, value, qualifier)

    def __MatchStandardMixerCrosspointMute(self, match, tag):

        CrosspointMuteStateNames = {
            b'0': 'On',
            b'1': 'Off'
        }

        value = CrosspointMuteStateNames[match.group(6)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        output = str(int(match.group(5)))
        self.WriteStatus('StandardMixerCrosspointMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_, 'Output': output})

    def SetStandardMixerInputLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'StandardMixerInputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SMLVLIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchStandardMixerInputLevel, None)
            self.__matchList.append('StandardMixerInputLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetStandardMixerInputLevel')
        else:
            InputLevelCmdString = 'SETD {0} SMLVLIN {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], value)
            self.__SetHelper('StandardMixerInputLevel', InputLevelCmdString, value, qualifier)

    def UpdateStandardMixerInputLevel(self, value, qualifier):

        if 'StandardMixerInputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SMLVLIN ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchStandardMixerInputLevel, None)
            self.__matchList.append('StandardMixerInputLevel')

        InputLevelCmdString = 'GETD {0} SMLVLIN {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('StandardMixerInputLevel', InputLevelCmdString, value, qualifier)

    def __MatchStandardMixerInputLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('StandardMixerInputLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetStandardMixerInputMute(self, value, qualifier):

        InputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'StandardMixerInputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SMMUTEIN ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchStandardMixerInputMute, None)
            self.__matchList.append('StandardMixerInputMute')

        InputMuteCmdString = 'SETD {0} SMMUTEIN {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'], InputMuteStateValues[value])
        self.__SetHelper('StandardMixerInputMute', InputMuteCmdString, value, qualifier)

    def UpdateStandardMixerInputMute(self, value, qualifier):

        if 'StandardMixerInputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SMMUTEIN ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchStandardMixerInputMute, None)
            self.__matchList.append('StandardMixerInputMute')

        InputMuteCmdString = 'GETD {0} SMMUTEIN {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Input'])
        self.__UpdateHelper('StandardMixerInputMute', InputMuteCmdString, value, qualifier)

    def __MatchStandardMixerInputMute(self, match, tag):

        InputMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = InputMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        input_ = str(int(match.group(4)))
        self.WriteStatus('StandardMixerInputMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Input': input_})

    def SetStandardMixerOutputLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'StandardMixerOutputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SMLVLOUT ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchStandardMixerOutputLevel, None)
            self.__matchList.append('StandardMixerOutputLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetStandardMixerOutputLevel')
        else:
            OutputLevelCmdString = 'SETD {0} SMLVLOUT {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'], value)
            self.__SetHelper('StandardMixerOutputLevel', OutputLevelCmdString, value, qualifier)

    def UpdateStandardMixerOutputLevel(self, value, qualifier):

        if 'StandardMixerOutputLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SMLVLOUT ([^<&>\'. ]+) (\d+) (-?\d+)\.\d{6} '), self.__MatchStandardMixerOutputLevel, None)
            self.__matchList.append('StandardMixerOutputLevel')

        OutputLevelCmdString = 'GETD {0} SMLVLOUT {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'])
        self.__UpdateHelper('StandardMixerOutputLevel', OutputLevelCmdString, value, qualifier)

    def __MatchStandardMixerOutputLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        Output = str(int(match.group(4)))
        self.WriteStatus('StandardMixerOutputLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Output': Output})

    def SetStandardMixerOutputMute(self, value, qualifier):

        OutputMuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'StandardMixerOutputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SMMUTEOUT ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchStandardMixerOutputMute, None)
            self.__matchList.append('StandardMixerOutputMute')

        OutputMuteCmdString = 'SETD {0} SMMUTEOUT {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'], OutputMuteStateValues[value])
        self.__SetHelper('StandardMixerOutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateStandardMixerOutputMute(self, value, qualifier):

        if 'StandardMixerOutputMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) SMMUTEOUT ([^<&>\'. ]+) (\d+) ([01]) '), self.__MatchStandardMixerOutputMute, None)
            self.__matchList.append('StandardMixerOutputMute')

        OutputMuteCmdString = 'GETD {0} SMMUTEOUT {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Output'])
        self.__UpdateHelper('StandardMixerOutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchStandardMixerOutputMute(self, match, tag):

        OutputMuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = OutputMuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        Output = str(int(match.group(4)))
        self.WriteStatus('StandardMixerOutputMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Output': Output})

    def SetTIAutoAnswer(self, value, qualifier):

        AutoAnswerStateValues = {
            'Off': '0',
            '1 Ring': '1',
            '2 Rings': '2',
            '3 Rings': '3',
            '4 Rings': '4',
            '5 Rings': '5',
        }

        if 'TIAutoAnswer' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TIAUTOANSWER ([^<&>\'. ]+) ([0-5]) '), self.__MatchTIAutoAnswer, None)
            self.__matchList.append('TIAutoAnswer')

        TIAutoAnswerCmdString = 'SETD {0} TIAUTOANSWER {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], AutoAnswerStateValues[value])
        self.__SetHelper('TIAutoAnswer', TIAutoAnswerCmdString, value, qualifier)

    def UpdateTIAutoAnswer(self, value, qualifier):

        if 'TIAutoAnswer' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TIAUTOANSWER ([^<&>\'. ]+) ([0-5]) '), self.__MatchTIAutoAnswer, None)
            self.__matchList.append('TIAutoAnswer')

        AutoAnswerCmdString = 'GETD {0} TIAUTOANSWER {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('TIAutoAnswer', AutoAnswerCmdString, value, qualifier)

    def __MatchTIAutoAnswer(self, match, tag):

        AutoAnswerStateNames = {
            b'0': 'Off',
            b'1': '1 Ring',
            b'2': '2 Rings',
            b'3': '3 Rings',
            b'4': '4 Rings',
            b'5': '5 Rings',
        }
        value = AutoAnswerStateNames[match.group(4)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        self.WriteStatus('TIAutoAnswer', value, {'Device Number': devNum, 'Instance ID': instID})

    def UpdateTICallerID(self, value, qualifier):

        if 'TICallerID' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d{1,2}) TICIDUSER ([^<&>\'. ]+) "(|\d{8})" "(\+?\d{0,11})" "(.*)" ?\r\n'), self.__MatchTICallerID, None)
            self.__matchList.append('TICallerID')

        devNum = qualifier['Device Number']
        if 1 <= int(devNum) <= 16:
            TICallerIDCmdString = 'GETD {0} TICIDUSER {1}\n'.format(devNum, qualifier['Instance ID'])
            self.__UpdateHelper('TICallerID', TICallerIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTICallerID')

    def __MatchTICallerID(self, match, tag):

        DeviceNumberStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16'
        }

        qualifier = {'Device Number': DeviceNumberStates[match.group(2).decode()], 'Instance ID': match.group(3).decode()}
        number = match.group(5).decode()
        name = match.group(6).decode()

        if number:
            if name:
                value = '{0} : {1}'.format(name, number)
            else:
                value = number
        else:
            value = ''
        self.WriteStatus('TICallerID', value, qualifier)

    def SetTIDTMF(self, value, qualifier):

        if 1 <= int(qualifier['Device Number']) <= 16 and value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']:
            TIDTMFCmdString = 'DIAL {0} TIPHONENUM {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], value)
            self.__SetHelper('TIDTMF', TIDTMFCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTIDTMF')

    def SetTIHook(self, value, qualifier):

        TIHookStateValues = {
            'On': '1',
            'Off': '0',
        }

        if 'TIHook' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TIHOOKSTATE ([^<&>\'. ]+) ([01]) '), self.__MatchTIHook, None)
            self.__matchList.append('TIHook')

        if value in TIHookStateValues:
            TIHookCmdString = 'SETD {0} TIHOOKSTATE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], TIHookStateValues[value])
            self.__SetHelper('TIHook', TIHookCmdString, value, qualifier)
        elif value == 'Flash':
            DialCmdString = 'FLASH {0} TILINE {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
            self.__SetHelper('TIHook', DialCmdString, value, qualifier)
        elif value == 'Dial':
            dialstring = qualifier['Number']
            if dialstring:
                DialCmdString = 'DIAL {0} TIPHONENUM {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], dialstring)
                self.__SetHelper('TIHook', DialCmdString, value, qualifier)
                try:
                    self.TIRedialString[qualifier['Instance ID']] = dialstring
                except:
                    self.TIRedialString[qualifier['Instance ID']] = {}
                    self.TIRedialString[qualifier['Instance ID']] = dialstring
        elif value == 'Redial':
            try:
                if self.TIRedialString[qualifier['Instance ID']]:
                    DialCmdString = 'DIAL {0} TIPHONENUM {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], self.TIRedialString[qualifier['Instance ID']])
                    self.__SetHelper('TIHook', DialCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetTIHook')
            except KeyError:
                self.TIRedialString[qualifier['Instance ID']] = {}

        elif value == 'Clear Redial':
            try:
                if self.TIRedialString[qualifier['Instance ID']]:
                    self.TIRedialString[qualifier['Instance ID']] = ''
            except KeyError:
                self.TIRedialString[qualifier['Instance ID']] = {}

    def UpdateTIHook(self, value, qualifier):

        if 'TIHook' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TIHOOKSTATE ([^<&>\'. ]+) ([01]) '), self.__MatchTIHook, None)
            self.__matchList.append('TIHook')

        TIHookCmdString = 'GETD {0} TIHOOKSTATE {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('TIHook', TIHookCmdString, value, qualifier)

    def __MatchTIHook(self, match, tag):

        TIHookStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = TIHookStateNames[match.group(4)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        self.WriteStatus('TIHook', value, {'Device Number': devNum, 'Instance ID': instID})

    def UpdateTILastNumber(self, value, qualifier):

        if 'TILastNumber' not in self.__matchList:
            self.AddMatchString(compile(b'#GETD (\d+) TILASTNUM ([^<&>\'. ]+) (.*)\r\n'), self.__MatchTILastNumber, None)
            self.__matchList.append('TILastNumber')

        LastNumberCmdString = 'GETD {0} TILASTNUM {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('TILastNumber', LastNumberCmdString, value, qualifier)

    def __MatchTILastNumber(self, match, tag):

        value = match.group(3).decode()
        devNum = str(int(match.group(1)))
        instID = match.group(2).decode()
        self.WriteStatus('TILastNumber', value, {'Device Number': devNum, 'Instance ID': instID})

    def SetTIPhoneEchoCancellation(self, value, qualifier):

        EchoCancellationStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'TIPhoneEchoCancellation' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TIRXLEC ([^<&>\'. ]+) ([01]) '), self.__MatchTIPhoneEchoCancellation, None)
            self.__matchList.append('TIPhoneEchoCancellation')

        EchoCancellationCmdString = 'SETD {0} TIRXLEC {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], EchoCancellationStateValues[value])
        self.__SetHelper('TIPhoneEchoCancellation', EchoCancellationCmdString, value, qualifier)

    def UpdateTIPhoneEchoCancellation(self, value, qualifier):

        if 'TIPhoneEchoCancellation' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TIRXLEC ([^<&>\'. ]+) ([01]) '), self.__MatchTIPhoneEchoCancellation, None)
            self.__matchList.append('TIPhoneEchoCancellation')

        EchoCancellationCmdString = 'GETD {0} TIRXLEC {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('TIPhoneEchoCancellation', EchoCancellationCmdString, value, qualifier)

    def __MatchTIPhoneEchoCancellation(self, match, tag):

        EchoCancellationStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = EchoCancellationStateNames[match.group(4)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        self.WriteStatus('TIPhoneEchoCancellation', value, {'Device Number': devNum, 'Instance ID': instID})

    def SetTIPhoneReceiveLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'TIPhoneReceiveLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TIRXLVL ([^<&>\'. ]+) (-?\d+)\.\d{6} '), self.__MatchTIPhoneReceiveLevel, None)
            self.__matchList.append('TIPhoneReceiveLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetTIPhoneReceiveLevel')
        else:
            LevelCmdString = 'SETD {0} TIRXLVL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], value)
            self.__SetHelper('TIPhoneReceiveLevel', LevelCmdString, value, qualifier)

    def UpdateTIPhoneReceiveLevel(self, value, qualifier):

        if 'TIPhoneReceiveLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TIRXLVL ([^<&>\'. ]+) (-?\d+)\.\d{6} '), self.__MatchTIPhoneReceiveLevel, None)
            self.__matchList.append('TIPhoneReceiveLevel')

        LevelCmdString = 'GETD {0} TIRXLVL {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('TIPhoneReceiveLevel', LevelCmdString, value, qualifier)

    def __MatchTIPhoneReceiveLevel(self, match, tag):

        value = int(match.group(4))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        self.WriteStatus('TIPhoneReceiveLevel', value, {'Device Number': devNum, 'Instance ID': instID})

    def SetTIPhoneReceiveMute(self, value, qualifier):

        MuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'TIPhoneReceiveMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TIRXMUTE ([^<&>\'. ]+) ([01]) '), self.__MatchTIPhoneReceiveMute, None)
            self.__matchList.append('TIPhoneReceiveMute')

        MuteCmdString = 'SETD {0} TIRXMUTE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], MuteStateValues[value])
        self.__SetHelper('TIPhoneReceiveMute', MuteCmdString, value, qualifier)

    def UpdateTIPhoneReceiveMute(self, value, qualifier):

        if 'TIPhoneReceiveMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TIRXMUTE ([^<&>\'. ]+) ([01]) '), self.__MatchTIPhoneReceiveMute, None)
            self.__matchList.append('TIPhoneReceiveMute')

        MuteCmdString = 'GETD {0} TIRXMUTE {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('TIPhoneReceiveMute', MuteCmdString, value, qualifier)

    def __MatchTIPhoneReceiveMute(self, match, tag):

        MuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = MuteStateNames[match.group(4)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        self.WriteStatus('TIPhoneReceiveMute', value, {'Device Number': devNum, 'Instance ID': instID})

    def SetTIPhoneTransmitLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 0
        }
        if 'TIPhoneTransmitLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TITXLVL ([^<&>\'. ]+) (-?\d+)\.\d{6} '), self.__MatchTIPhoneTransmitLevel, None)
            self.__matchList.append('TIPhoneTransmitLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetTIPhoneTransmitLevel')
        else:
            LevelCmdString = 'SETD {0} TITXLVL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], value)
            self.__SetHelper('TIPhoneTransmitLevel', LevelCmdString, value, qualifier)

    def UpdateTIPhoneTransmitLevel(self, value, qualifier):

        if 'TIPhoneTransmitLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TITXLVL ([^<&>\'. ]+) (-?\d+)\.\d{6} '), self.__MatchTIPhoneTransmitLevel, None)
            self.__matchList.append('TIPhoneTransmitLevel')

        LevelCmdString = 'GETD {0} TITXLVL {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('TIPhoneTransmitLevel', LevelCmdString, value, qualifier)

    def __MatchTIPhoneTransmitLevel(self, match, tag):

        value = int(match.group(4))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        self.WriteStatus('TIPhoneTransmitLevel', value, {'Device Number': devNum, 'Instance ID': instID})

    def SetTIPhoneTransmitMute(self, value, qualifier):

        MuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'TIPhoneTransmitMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TITXMUTE ([^<&>\'. ]+) ([01]) '), self.__MatchTIPhoneTransmitMute, None)
            self.__matchList.append('TIPhoneTransmitMute')

        MuteCmdString = 'SETD {0} TITXMUTE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], MuteStateValues[value])
        self.__SetHelper('TIPhoneTransmitMute', MuteCmdString, value, qualifier)

    def UpdateTIPhoneTransmitMute(self, value, qualifier):

        if 'TIPhoneTransmitMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) TITXMUTE ([^<&>\'. ]+) ([01]) '), self.__MatchTIPhoneTransmitMute, None)
            self.__matchList.append('TIPhoneTransmitMute')

        MuteCmdString = 'GETD {0} TITXMUTE {1}\n'.format(qualifier['Device Number'], qualifier['Instance ID'])
        self.__UpdateHelper('TIPhoneTransmitMute', MuteCmdString, value, qualifier)

    def __MatchTIPhoneTransmitMute(self, match, tag):

        MuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = MuteStateNames[match.group(4)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        self.WriteStatus('TIPhoneTransmitMute', value, {'Device Number': devNum, 'Instance ID': instID})

    def SetTISpeedDial(self, value, qualifier):

        SpeedDialConstraints = {
            'Min': 1,
            'Max': 16
        }
        val = int(value)
        if SpeedDialConstraints['Min'] <= val <= SpeedDialConstraints['Max']:
            DialCmdString = 'DIAL {0} TISPEEDDIAL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], value)
            self.__SetHelper('TISpeedDial', DialCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTISpeedDial')

    def SetVoIPAutoAnswer(self, value, qualifier):

        AutoAnswerStateValues = {
            'Off': '0',
            'On': '1',
        }

        if 'VoIPAutoAnswer' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPAAENABLE ([^<&>\'. ]+) (1|2) (0|1) '), self.__MatchVoIPAutoAnswer, None)
            self.__matchList.append('VoIPAutoAnswer')

        VoIPAutoAnswerCmdString = 'SETD {0} VOIPAAENABLE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'], AutoAnswerStateValues[value])
        self.__SetHelper('VoIPAutoAnswer', VoIPAutoAnswerCmdString, value, qualifier)

    def UpdateVoIPAutoAnswer(self, value, qualifier):

        if 'VoIPAutoAnswer' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPAAENABLE ([^<&>\'. ]+) (1|2) (0|1) '), self.__MatchVoIPAutoAnswer, None)
            self.__matchList.append('VoIPAutoAnswer')

        AutoAnswerCmdString = 'GETD {0} VOIPAAENABLE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
        self.__UpdateHelper('VoIPAutoAnswer', AutoAnswerCmdString, value, qualifier)

    def __MatchVoIPAutoAnswer(self, match, tag):

        AutoAnswerStateNames = {
            b'0': 'Off',
            b'1': 'On',
        }
        value = AutoAnswerStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        line = str(int(match.group(4)))
        self.WriteStatus('VoIPAutoAnswer', value, {'Device Number': devNum, 'Instance ID': instID, 'Line': line})

    def UpdateVoIPCallerID(self, value, qualifier):

        if 'VoIPCallerID' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d{1,2}) VOIPCIDUSER ([^<&>\'. ]+) (1|2) "(|\d{8})" ?"(\+?\d{0,11})" ?"(.*)" ?\r\n'), self.__MatchVoIPCallerID, None)
            self.__matchList.append('VoIPCallerID')

        devNum = qualifier['Device Number']
        line = qualifier['Line']
        if 1 <= int(devNum) <= 16 and line in ['1', '2']:
            VoIPCallerIDCmdString = 'GETD {0} VOIPCIDUSER {1} {2}\n'.format(devNum, qualifier['Instance ID'], line)
            self.__UpdateHelper('VoIPCallerID', VoIPCallerIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVoIPCallerID')

    def __MatchVoIPCallerID(self, match, tag):

        DeviceNumberStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16'
        }

        LineStates = {
            '1': '1',
            '2': '2'
        }

        qualifier = {'Device Number': DeviceNumberStates[match.group(2).decode()], 'Instance ID': match.group(3).decode(), 'Line': LineStates[match.group(4).decode()]}
        name = match.group(7).decode()
        number = match.group(6).decode()

        if number:
            if name:
                value = '{0} : {1}'.format(name, number)
            else:
                value = number
        else:
            value = ''
        self.WriteStatus('VoIPCallerID', value, qualifier)

    def SetVoIPDTMF(self, value, qualifier):

        if 1 <= int(qualifier['Device Number']) <= 16 and qualifier['Line'] in ['1', '2'] and value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']:
            VoIPDTMFCmdString = 'DIAL {0} VOIPPHONENUM {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'], value)
            self.__SetHelper('VoIPDTMF', VoIPDTMFCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoIPDTMF')

    def SetVoIPHook(self, value, qualifier):

        VoIPHookStateValues = {
            'On': '1',
            'Off': '0',
        }

        if 'VoIPHook' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPHOOKSTATE ([^<&>\'. ]+) (1|2) ([01]) '), self.__MatchVoIPHook, None)
            self.__matchList.append('VoIPHook')

        if value in VoIPHookStateValues:
            VoIPHookCmdString = 'SETD {0} VOIPHOOKSTATE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'], VoIPHookStateValues[value])
            self.__SetHelper('VoIPHook', VoIPHookCmdString, value, qualifier)
        elif value == 'Dial':
            dialstring = qualifier['Number']
            if dialstring:
                DialCmdString = 'DIAL {0} VOIPPHONENUM {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'], dialstring)
                self.__SetHelper('VoIPHook', DialCmdString, value, qualifier)

                try:
                    self.VoIPRedialString[qualifier['Instance ID']][qualifier['Line']] = dialstring

                except:
                    self.VoIPRedialString[qualifier['Instance ID']] = {'1': '', '2': ''}
                    self.VoIPRedialString[qualifier['Instance ID']][qualifier['Line']] = dialstring
        elif value == 'Redial':
            try:
                if self.VoIPRedialString[qualifier['Instance ID']][qualifier['Line']]:
                    dialstring = self.VoIPRedialString[qualifier['Instance ID']][qualifier['Line']]
                    DialCmdString = 'DIAL {0} VOIPPHONENUM {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'], dialstring)
                    self.__SetHelper('VoIPHook', DialCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetVoIPHook')
            except KeyError:
                self.VoIPRedialString[qualifier['Instance ID']] = {'1': '', '2': ''}
        elif value == 'Answer':
            cmdString = 'ANS {0} VOIPCALL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
            self.__SetHelper('VoIPHook', cmdString, value, qualifier)
        elif value == 'End/Reject':
            cmdString = 'END {0} VOIPCALL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
            self.__SetHelper('VoIPHook', cmdString, value, qualifier)
        elif value == 'Hold':
            cmdString = 'HOLD {0} VOIPCALL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
            self.__SetHelper('VoIPHook', cmdString, value, qualifier)
        elif value == 'Resume':
            cmdString = 'RESUME {0} VOIPCALL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
            self.__SetHelper('VoIPHook', cmdString, value, qualifier)
        elif value == 'Clear Redial':
            try:
                if self.VoIPRedialString[qualifier['Instance ID']][qualifier['Line']]:
                    self.VoIPRedialString[qualifier['Instance ID']][qualifier['Line']] = ''

            except KeyError:
                self.VoIPRedialString[qualifier['Instance ID']][qualifier['Line']] = {'1': '', '2': ''}

    def UpdateVoIPHook(self, value, qualifier):

        if 'VoIPHook' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPHOOKSTATE ([^<&>\'. ]+) (1|2) ([01]) '), self.__MatchVoIPHook, None)
            self.__matchList.append('VoIPHook')

        VoIPHookCmdString = 'GETD {0} VOIPHOOKSTATE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
        self.__UpdateHelper('VoIPHook', VoIPHookCmdString, value, qualifier)

    def __MatchVoIPHook(self, match, tag):

        VoIPHookStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = VoIPHookStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        line = str(int(match.group(4)))
        self.WriteStatus('VoIPHook', value, {'Device Number': devNum, 'Instance ID': instID, 'Line': line, 'Number': ''})

    def UpdateVoIPLastNumber(self, value, qualifier):

        if 'VoIPLastNumber' not in self.__matchList:
            self.AddMatchString(compile(b'#GETD (\d+) VOIPLASTNUM ([^<&>\'. ]+) (1|2) (\d+)\r\n'), self.__MatchVoIPLastNumber, None)
            self.__matchList.append('VoIPLastNumber')

        LastNumberCmdString = 'GETD {0} VOIPLASTNUM {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
        self.__UpdateHelper('VoIPLastNumber', LastNumberCmdString, value, qualifier)

    def __MatchVoIPLastNumber(self, match, tag):

        value = match.group(4).decode()
        devNum = str(int(match.group(1)))
        instID = match.group(2).decode()
        line = str(int(match.group(3)))
        self.WriteStatus('VoIPLastNumber', value, {'Device Number': devNum, 'Instance ID': instID, 'Line': line})

    def SetVoIPReceiveLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 12
        }
        if 'VoIPReceiveLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPRXLVL ([^<&>\'. ]+) (0|1) (-?\d+)\.\d{6} '), self.__MatchVoIPReceiveLevel, None)
            self.__matchList.append('VoIPReceiveLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetVoIPReceiveLevel')
        else:
            LevelCmdString = 'SETD {0} VOIPRXLVL {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'], value)
            self.__SetHelper('VoIPReceiveLevel', LevelCmdString, value, qualifier)

    def UpdateVoIPReceiveLevel(self, value, qualifier):

        if 'VoIPReceiveLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPRXLVL ([^<&>\'. ]+) (0|1) (-?\d+)\.\d{6} '), self.__MatchVoIPReceiveLevel, None)
            self.__matchList.append('VoIPReceiveLevel')

        LevelCmdString = 'GETD {0} VOIPRXLVL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
        self.__UpdateHelper('VoIPReceiveLevel', LevelCmdString, value, qualifier)

    def __MatchVoIPReceiveLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        line = str(int(match.group(4)))
        self.WriteStatus('VoIPReceiveLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Line': line})

    def SetVoIPReceiveMute(self, value, qualifier):

        MuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'VoIPReceiveMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPRXMUTE ([^<&>\'. ]+) (1|2) ([01]) '), self.__MatchVoIPReceiveMute, None)
            self.__matchList.append('VoIPReceiveMute')

        MuteCmdString = 'SETD {0} VOIPRXMUTE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'], MuteStateValues[value])
        self.__SetHelper('VoIPReceiveMute', MuteCmdString, value, qualifier)

    def UpdateVoIPReceiveMute(self, value, qualifier):

        if 'VoIPReceiveMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPRXMUTE ([^<&>\'. ]+) (1|2) ([01]) '), self.__MatchVoIPReceiveMute, None)
            self.__matchList.append('VoIPReceiveMute')

        MuteCmdString = 'GETD {0} VOIPRXMUTE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
        self.__UpdateHelper('VoIPReceiveMute', MuteCmdString, value, qualifier)

    def __MatchVoIPReceiveMute(self, match, tag):

        MuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = MuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        line = str(int(match.group(4)))
        self.WriteStatus('VoIPReceiveMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Line': line})

    def UpdateVoIPRingIndicator(self, value, qualifier):

        if 'VoIPRingIndicator' not in self.__matchList:
            self.AddMatchString(compile(b'#GETD (\d+) VOIPRISTATE ([^<&>\'. ]+) (1|2) (\d+) '), self.__MatchVoIPRingIndicator, None)
            self.__matchList.append('VoIPRingIndicator')

        RingIndicatorCmdString = 'GETD {0} VOIPRISTATE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
        self.__UpdateHelper('VoIPRingIndicator', RingIndicatorCmdString, value, qualifier)

    def __MatchVoIPRingIndicator(self, match, tag):

        StateNames = {
            b'1': 'Ringing',
            b'0': 'Not Ringing'
        }
        value = StateNames[match.group(4)]
        devNum = str(int(match.group(1)))
        instID = match.group(2).decode()
        line = str(int(match.group(3)))
        self.WriteStatus('VoIPRingIndicator', value, {'Device Number': devNum, 'Instance ID': instID, 'Line': line})

    def SetVoIPSpeedDial(self, value, qualifier):

        SpeedDialConstraints = {
            'Min': 1,
            'Max': 16
        }
        val = int(value)
        if SpeedDialConstraints['Min'] <= val <= SpeedDialConstraints['Max']:
            DialCmdString = 'DIAL {0} VOIPSPEEDDIAL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'], val)
            self.__SetHelper('VoIPSpeedDial', DialCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoIPSpeedDial')

    def SetVoIPTransmitLevel(self, value, qualifier):

        LevelConstraints = {
            'Min': -100,
            'Max': 0
        }
        if 'VoIPTransmitLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPTXLVL ([^<&>\'. ]+) (1|2) (-?\d+)\.\d{6} '), self.__MatchVoIPTransmitLevel, None)
            self.__matchList.append('VoIPTransmitLevel')

        if value < LevelConstraints['Min'] or value > LevelConstraints['Max']:
            self.Discard('Invalid Command for SetVoIPTransmitLevel')
        else:
            LevelCmdString = 'SETD {0} VOIPTXLVL {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'], value)
            self.__SetHelper('VoIPTransmitLevel', LevelCmdString, value, qualifier)

    def UpdateVoIPTransmitLevel(self, value, qualifier):

        if 'VoIPTransmitLevel' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPTXLVL ([^<&>\'. ]+) (1|2) (-?\d+)\.\d{6} '), self.__MatchVoIPTransmitLevel, None)
            self.__matchList.append('VoIPTransmitLevel')

        LevelCmdString = 'GETD {0} VOIPTXLVL {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
        self.__UpdateHelper('VoIPTransmitLevel', LevelCmdString, value, qualifier)

    def __MatchVoIPTransmitLevel(self, match, tag):

        value = int(match.group(5))
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        line = str(int(match.group(4)))
        self.WriteStatus('VoIPTransmitLevel', value, {'Device Number': devNum, 'Instance ID': instID, 'Line': line})

    def SetVoIPTransmitMute(self, value, qualifier):

        MuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if 'VoIPTransmitMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPTXMUTE ([^<&>\'. ]+) (1|2) ([01]) '), self.__MatchVoIPTransmitMute, None)
            self.__matchList.append('VoIPTransmitMute')

        MuteCmdString = 'SETD {0} VOIPTXMUTE {1} {2} {3}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'], MuteStateValues[value])
        self.__SetHelper('VoIPTransmitMute', MuteCmdString, value, qualifier)

    def UpdateVoIPTransmitMute(self, value, qualifier):

        if 'VoIPTransmitMute' not in self.__matchList:
            self.AddMatchString(compile(b'#(SETD|GETD) (\d+) VOIPTXMUTE ([^<&>\'. ]+) (1|2) ([01]) '), self.__MatchVoIPTransmitMute, None)
            self.__matchList.append('VoIPTransmitMute')

        MuteCmdString = 'GETD {0} VOIPTXMUTE {1} {2}\n'.format(qualifier['Device Number'], qualifier['Instance ID'], qualifier['Line'])
        self.__UpdateHelper('VoIPTransmitMute', MuteCmdString, value, qualifier)

    def __MatchVoIPTransmitMute(self, match, tag):

        MuteStateNames = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = MuteStateNames[match.group(5)]
        devNum = str(int(match.group(2)))
        instID = match.group(3).decode()
        line = str(int(match.group(4)))
        self.WriteStatus('VoIPTransmitMute', value, {'Device Number': devNum, 'Instance ID': instID, 'Line': line})

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

    def __MatchError(self, match, tag):

        self.Error([match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.SetEchoOff()

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def biam_25_149_A(self):
        self.Model = 'Audia'

    def biam_25_149_N(self):
        self.Model = 'Nexia'

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


class SerialClass(SerialInterface, DeviceClass):
    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
