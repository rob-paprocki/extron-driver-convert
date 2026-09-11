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
            'MTX3': self.yama_25_367_MTX3,
            'MTX5-D': self.yama_25_367_MTX5,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CurrentFileInformation': { 'Status': {}},
            'DCAAssignControl': {'Parameters':['Input','Group'], 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'GroupLevel': {'Parameters': ['Group'], 'Status': {}},
            'GroupMasterDCALevel': {'Parameters':['Group'], 'Status': {}},
            'GroupMasterDCAMute': {'Parameters':['Group'], 'Status': {}},
            'GroupMute': {'Parameters': ['Group'], 'Status': {}},
            'InputLevel': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'MatrixTieLevel': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieMute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'SetCurrentFilePath': {'Parameters': ['Sub Folder Number', 'File Index'], 'Status': {}},
            'Transport': { 'Status': {}},
            'ZoneGroupMasterDCALevel': {'Parameters': ['Zone', 'Group'], 'Status': {}},
            'ZoneGroupMasterDCAMute': {'Parameters': ['Zone', 'Group'], 'Status': {}},
            'ZoneOutputMasterLevel': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneOutputMasterMute': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneSourceLevel': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneSourceMute': {'Parameters': ['Zone'], 'Status': {}},
        }

        self.RunModeDisabled = True
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) event MTX:AudioPlayer[SG]etCurrentSong ".+?\|filename=(.*)"\n'), self.__MatchCurrentFileInformation, None)
            self.AddMatchString(re.compile(b'OKm event MTX:AudioPlayer[SG]etCurrentSong "(sdcard is not inserted)"\n'), self.__MatchCurrentFileInformation, None)
            self.AddMatchString(re.compile(b'OKm event MTX:AudioPlayerGetCurrentSong "(song is not set up)"\n'), self.__MatchCurrentFileInformation, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60000/1/([0-9]{1,2})/([0-7])/0/0 0 0 ([01]).*\n'), self.__MatchDCAAssignControl, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60000/1/([0-9]{1,2})/([0-7])/0/0 0 0 ([01])\n'), self.__MatchDCAAssignControl, None)
            
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devstatus error "(none|flt|err|wrn).*"\n'), self.__MatchDeviceStatus, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60002/2/0/([0-7])/0/0 0 0 (-?[0-9]{1,5}).*\n'), self.__MatchGroupMasterDCALevel, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60002/2/0/([0-7])/0/0 0 0 (-?[0-9]{1,5})\n'), self.__MatchGroupMasterDCALevel, None)
            
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60003/2/0/([0-7])/0/0 0 0 ([01]).*\n'), self.__MatchGroupMasterDCAMute, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60003/2/0/([0-7])/0/0 0 0 ([01])\n'), self.__MatchGroupMasterDCAMute, None)
            
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60000/2/0/([0-7])/0/0 0 0 (-?[0-9]{1,5}).*\n'), self.__MatchGroupLevel, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60000/2/0/([0-7])/0/0 0 0 (-?[0-9]{1,5})\n'), self.__MatchGroupLevel, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60001/2/0/([0-7])/0/0 0 0 ([01]).*\n'), self.__MatchGroupMute, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60001/2/0/([0-7])/0/0 0 0 ([01])\n'), self.__MatchGroupMute, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60000/0/([0-9]{1,2})/0/0/0 0 0 (-?[0-9]{1,5}).*\n'), self.__MatchInputLevel, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60000/0/([0-9]{1,2})/0/0/0 0 0 (-?[0-9]{1,5})\n'), self.__MatchInputLevel, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60001/0/([0-9]{1,2})/0/0/0 0 0 ([01]).*\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60001/0/([0-9]{1,2})/0/0/0 0 0 ([01])\n'), self.__MatchInputMute, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/30002/1/([0-9]{1,2})/([0-9]{1,2})/0/0 0 0 (-?[0-9]{1,5}).*\n'), self.__MatchMatrixTieLevel, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/30002/1/([0-9]{1,2})/([0-9]{1,2})/0/0 0 0 (-?[0-9]{1,5})\n'), self.__MatchMatrixTieLevel, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/30002/1/([0-9]{1,2})/([0-9]{1,2})/1/0 0 0 ([01]).*\n'), self.__MatchMatrixTieMute, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/30002/1/([0-9]{1,2})/([0-9]{1,2})/1/0 0 0 ([01])\n'), self.__MatchMatrixTieMute, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/(?:20017|20024)/0/([0-9]{1,2})/0/0/0 0 0 (-?[0-9]{1,5}).*\n'), self.__MatchOutputLevel, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/(?:20017|20024)/0/([0-9]{1,2})/0/0/0 0 0 (-?[0-9]{1,5})\n'), self.__MatchOutputLevel, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/(?:20017|20024)/1/([0-9]{1,2})/0/0/0 0 0 ([01]).*\n'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/(?:20017|20024)/1/([0-9]{1,2})/0/0/0 0 0 ([01])\n'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'OK ssrecall ([0-9]{1,2})\n'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'OK sscurrent ([0-9]{1,2}) (?:unmodified|modified)\n'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'NOTIFY sscurrent ([0-9]{1,2})\n'), self.__MatchPresetRecall, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60002/1/([0-9]{1,2})/([0-7])/0/0 0 0 (-?[0-9]{1,5}).*\n'), self.__MatchZoneGroupMasterDCALevel, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60002/1/([0-9]{1,2})/([0-7])/0/0 0 0 (-?[0-9]{1,5})\n'), self.__MatchZoneGroupMasterDCALevel, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60003/1/([0-9]{1,2})/([0-7])/0/0 0 0 ([01]).*\n'), self.__MatchZoneGroupMasterDCAMute, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60003/1/([0-9]{1,2})/([0-7])/0/0 0 0 ([01])\n'), self.__MatchZoneGroupMasterDCAMute, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60002/0/([0-9]{1,2})/0/0/0 0 0 (-?[0-9]{1,5}).*\n'), self.__MatchZoneOutputMasterLevel, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60002/0/([0-9]{1,2})/0/0/0 0 0 (-?[0-9]{1,5})\n'), self.__MatchZoneOutputMasterLevel, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/60003/0/([0-9]{1,2})/0/0/0 0 0 ([01]).*\n'), self.__MatchZoneOutputMasterMute, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/60003/0/([0-9]{1,2})/0/0/0 0 0 ([01])\n'), self.__MatchZoneOutputMasterMute, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/(?:20013|20020)/1/([0-7])/0/0/0 0 0 (-?[0-9]{1,5}).*\n'), self.__MatchZoneSourceLevel, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/(?:20013|20020)/1/([0-7])/0/0/0 0 0 (-?[0-9]{1,5})\n'), self.__MatchZoneSourceLevel, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) set MTX:mem_512/(?:20013|20020)/1/([0-7])/0/1/0 0 0 ([01]).*\n'), self.__MatchZoneSourceMute, None)
            self.AddMatchString(re.compile(b'OK get MTX:mem_512/(?:20013|20020)/1/([0-7])/0/1/0 0 0 ([01])\n'), self.__MatchZoneSourceMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devstatus runmode "normal"\n'), self.__MatchRunMode, None)
            self.AddMatchString(re.compile(b'ERROR .* (.*)\n'), self.__MatchError, None)

    def __MatchRunMode(self, match, tag):

        self.RunModeDisabled = False

        self.Send('scpmode encoding ascii\n')

        self.Send('scpmode valuetype raw\n')

    def UpdateCurrentFileInformation(self, value, qualifier):

        CurrentFileInformationCmdString = 'event MTX:AudioPlayerGetCurrentSong ""\n'
        self.__UpdateHelper('CurrentFileInformation', CurrentFileInformationCmdString, value, qualifier)

    def __MatchCurrentFileInformation(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentFileInformation', value, None)

    def SetDCAAssignControl(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
            }

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
            }

        if (self.InputConstraints['Min'] <= int(qualifier['Input']) <= self.InputConstraints['Max']
            and qualifier['Group'] in GroupStates and value in ValueStateValues):
            DCAAssignControlCmdString = 'set MTX:mem_512/60000/1/{0}/{1}/0/0 0 0 {2}\n'.format(int(qualifier['Input']) - 1,
                                                GroupStates[qualifier['Group']], ValueStateValues[value])    
            self.__SetHelper('DCAAssignControl', DCAAssignControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDCAAssignControl')

    def UpdateDCAAssignControl(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
            }

        if (self.InputConstraints['Min'] <= int(qualifier['Input']) <= self.InputConstraints['Max']
                    and qualifier['Group'] in GroupStates):
            DCAAssignControlCmdString = 'get MTX:mem_512/60000/1/{0}/{1}/0/0 0 0\n'.format(int(qualifier['Input']) - 1,
                                                GroupStates[qualifier['Group']])
            self.__UpdateHelper('DCAAssignControl', DCAAssignControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDCAAssignControl')

    def __MatchDCAAssignControl(self, match, tag):

        GroupStates = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'E',
            '5': 'F',
            '6': 'G',
            '7': 'H',
            }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            }

        qualifier = {}
        qualifier['Input'] = str(int(match.group(1).decode()) + 1)
        qualifier['Group'] = GroupStates[match.group(2).decode()]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('DCAAssignControl', value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        if self.RunModeDisabled:
            self.Send('devstatus runmode\n')

        DeviceStatusCmdString = 'devstatus error\n'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        DeviceStatusNames = {
            'none': 'Normal',
            'err':  'Error',
            'flt':  'Fault',
            'wrn':  'Warning'
        }

        value = DeviceStatusNames[match.group(1).decode()] 
        self.WriteStatus('DeviceStatus', value, None)

    def SetGroupLevel(self, value, qualifier):

        GroupValues = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }

        if -138.01 <= value <= 10:
            GroupLevelCmdString = 'set MTX:mem_512/60000/2/0/{0}/0/0 0 0 {1}\n'.format(GroupValues[qualifier['Group']], int(value * 100))
            self.__SetHelper('GroupLevel', GroupLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupLevel')

    def UpdateGroupLevel(self, value, qualifier):

        GroupValues = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }

        GroupLevelCmdString = 'get MTX:mem_512/60000/2/0/{0}/0/0 0 0\n'.format(GroupValues[qualifier['Group']])
        self.__UpdateHelper('GroupLevel', GroupLevelCmdString, value, qualifier)

    def __MatchGroupLevel(self, match, tag):

        GroupNames = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'E',
            '5': 'F',
            '6': 'G',
            '7': 'H'
        }

        qualifier = {'Group': GroupNames[match.group(1).decode()]}
        value = int(match.group(2).decode()) / 100
        if -138.01 <= value <= 10:
            self.WriteStatus('GroupLevel', value, qualifier)
        else:
            self.Error(['Group Level: Invalid/unexpected response'])

    def SetGroupMasterDCALevel(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }

        ValueConstraints = {
            'Min': -138.01,
            'Max': 10
        }

        group_val = qualifier['Group']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and group_val in GroupStates:
            GroupMasterDCALevelCmdString = 'set MTX:mem_512/60002/2/0/{0}/0/0 0 0 {1}\n'.format(GroupStates[group_val], int(value * 100))
            self.__SetHelper('GroupMasterDCALevel', GroupMasterDCALevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMasterDCALevel')

    def UpdateGroupMasterDCALevel(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }

        group_val = qualifier['Group']
        if group_val in GroupStates:
            GroupMasterDCALevelCmdString = 'get MTX:mem_512/60002/2/0/{0}/0/0 0 0\n'.format(GroupStates[group_val])
            self.__UpdateHelper('GroupMasterDCALevel', GroupMasterDCALevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMasterDCALevel')

    def __MatchGroupMasterDCALevel(self, match, tag):

        GroupStates = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'E',
            '5': 'F',
            '6': 'G',
            '7': 'H'
        }

        qualifier = {'Group': GroupStates[match.group(1).decode()]}
        value = int(match.group(2).decode()) / 100
        if -138.1 <= value <= 10:
            self.WriteStatus('GroupMasterDCALevel', value, qualifier)
        else:
            self.Error(['Zone Group Master DCA Level: Invalid/unexpected response'])

    def SetGroupMasterDCAMute(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        group_val = qualifier['Group']
        if group_val in GroupStates and value in ValueStateValues:
            GroupMasterDCAMuteCmdString = 'set MTX:mem_512/60003/2/0/{0}/0/0 0 0 {1}\n'.format(GroupStates[group_val], ValueStateValues[value])
            self.__SetHelper('GroupMasterDCAMute', GroupMasterDCAMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMasterDCAMute')

    def UpdateGroupMasterDCAMute(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }
        
        group_val = qualifier['Group']
        if group_val in GroupStates:
            GroupMasterDCAMuteCmdString = 'get MTX:mem_512/60003/2/0/{0}/0/0 0 0\n'.format(GroupStates[group_val])
            self.__UpdateHelper('GroupMasterDCAMute', GroupMasterDCAMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMasterDCAMute')

    def __MatchGroupMasterDCAMute(self, match, tag):

        GroupStates = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'E',
            '5': 'F',
            '6': 'G',
            '7': 'H'
        }

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        qualifier = {}
        qualifier['Group'] = GroupStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('GroupMasterDCAMute', value, qualifier)

    def SetGroupMute(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }

        MuteValues = {
            'On':   '1',
            'Off':  '0'
        }

        GroupMuteCmdString = 'set MTX:mem_512/60001/2/0/{0}/0/0 0 0 {1}\n'.format(GroupStates[qualifier['Group']], MuteValues[value])
        self.__SetHelper('GroupMute', GroupMuteCmdString, value, qualifier)

    def UpdateGroupMute(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }

        GroupMuteCmdString = 'get MTX:mem_512/60001/2/0/{0}/0/0 0 0\n'.format(GroupStates[qualifier['Group']])
        self.__UpdateHelper('GroupMute', GroupMuteCmdString, value, qualifier)

    def __MatchGroupMute(self, match, tag):

        GroupNames = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'E',
            '5': 'F',
            '6': 'G',
            '7': 'H'
        }

        MuteNames = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Group': GroupNames[match.group(1).decode()]}
        value = MuteNames[match.group(2).decode()]
        self.WriteStatus('GroupMute', value, qualifier)

    def SetInputLevel(self, value, qualifier):

        if self.InputConstraints['Min'] <= int(qualifier['Input']) <= self.InputConstraints['Max'] and -138.01 <= value <= 10:
            InputLevelCmdString = 'set MTX:mem_512/60000/0/{0}/0/0/0 0 0 {1}\n'.format(int(qualifier['Input']) - 1, int(value * 100))
            self.__SetHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        if self.InputConstraints['Min'] <= int(qualifier['Input']) <= self.InputConstraints['Max']:
            InputLevelCmdString = 'get MTX:mem_512/60000/0/{0}/0/0/0 0 0\n'.format(int(qualifier['Input']) - 1)
            self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLevel')

    def __MatchInputLevel(self, match, tag):

        qualifier = {'Input': str(int(match.group(1).decode()) + 1)}
        value = int(match.group(2).decode()) / 100
        if -138.01 <= value <= 10:
            self.WriteStatus('InputLevel', value, qualifier)
        else:
            self.Error(['Input Level: Invalid/unexpected response'])

    def SetInputMute(self, value, qualifier):

        MuteValues = {
            'On':   '0',
            'Off':  '1'
        }

        if self.InputConstraints['Min'] <= int(qualifier['Input']) <= self.InputConstraints['Max']:
            InputMuteCmdString = 'set MTX:mem_512/60001/0/{0}/0/0/0 0 0 {1}\n'.format(int(qualifier['Input']) - 1, MuteValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        if self.InputConstraints['Min'] <= int(qualifier['Input']) <= self.InputConstraints['Max']:
            InputMuteCmdString = 'get MTX:mem_512/60001/0/{0}/0/0/0 0 0\n'.format(int(qualifier['Input']) - 1)
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        MuteValues = {
            '0': 'On',
            '1': 'Off'
        }

        qualifier = {'Input': str(int(match.group(1).decode()) + 1)}
        value = MuteValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetMatrixTieLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -138.01,
            'Max': 0
        }

        if all([ValueConstraints['Min'] <= value <= ValueConstraints['Max'],
                self.TieInputConstraints['Min'] <= int(qualifier['Input']) <= self.TieInputConstraints['Max'],
                self.OutputConstraints['Min'] <= int(qualifier['Output']) <= self.OutputConstraints['Max']]):
            MatrixTieLevelCmdString = 'set MTX:mem_512/30002/1/{0}/{1}/0/0 0 0 {2}\n'.format(int(qualifier['Input']) - 1, int(qualifier['Output']) - 1, int(value * 100))
            self.__SetHelper('MatrixTieLevel', MatrixTieLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieLevel')

    def UpdateMatrixTieLevel(self, value, qualifier):

        if all([self.TieInputConstraints['Min'] <= int(qualifier['Input']) <= self.TieInputConstraints['Max'],
                self.OutputConstraints['Min'] <= int(qualifier['Output']) <= self.OutputConstraints['Max']]):
            MatrixTieLevelCmdString = 'get MTX:mem_512/30002/1/{0}/{1}/0/0 0 0\n'.format(int(qualifier['Input']) - 1, int(qualifier['Output']) - 1)
            self.__UpdateHelper('MatrixTieLevel', MatrixTieLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixTieLevel')

    def __MatchMatrixTieLevel(self, match, tag):

        qualifier = {
            'Input':    str(int(match.group(1).decode()) + 1),
            'Output':   str(int(match.group(2).decode()) + 1)
        }

        value = int(match.group(3).decode()) / 100
        if -138.01 <= value <= 0:
            self.WriteStatus('MatrixTieLevel', value, qualifier)
        else:
            self.Error(['Matrix Tie Level: Invalid/unexpected response'])

    def SetMatrixTieMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '0',
            'Off':  '1'
        }

        if all([self.TieInputConstraints['Min'] <= int(qualifier['Input']) <= self.TieInputConstraints['Max'],
                self.OutputConstraints['Min'] <= int(qualifier['Output']) <= self.OutputConstraints['Max']]):
            MatrixTieMuteCmdString = 'set MTX:mem_512/30002/1/{0}/{1}/1/0 0 0 {2}\n'.format(int(qualifier['Input']) - 1, int(qualifier['Output']) - 1, ValueStateValues[value])
            self.__SetHelper('MatrixTieMute', MatrixTieMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieMute')

    def UpdateMatrixTieMute(self, value, qualifier):

        if all([self.TieInputConstraints['Min'] <= int(qualifier['Input']) <= self.TieInputConstraints['Max'],
                self.OutputConstraints['Min'] <= int(qualifier['Output']) <= self.OutputConstraints['Max']]):
            MatrixTieMuteCmdString = 'get MTX:mem_512/30002/1/{0}/{1}/1/0 0 0\n'.format(int(qualifier['Input']) - 1, int(qualifier['Output']) - 1)
            self.__UpdateHelper('MatrixTieMute', MatrixTieMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixTieMute')

    def __MatchMatrixTieMute(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        qualifier = {
            'Input':    str(int(match.group(1).decode()) + 1),
            'Output':   str(int(match.group(2).decode()) + 1)
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('MatrixTieMute', value, qualifier)

    def SetOutputLevel(self, value, qualifier):

        if self.OutputConstraints['Min'] <= int(qualifier['Output']) <= self.OutputConstraints['Max'] and -138.01 <= value <= 10:
            OutputLevelCmdString = 'set MTX:mem_512/{0}/0/{1}/0/0/0 0 0 {2}\n'.format(self.OutputLevelID, int(qualifier['Output']) - 1, int(value * 100))
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        if self.OutputConstraints['Min'] <= int(qualifier['Output']) <= self.OutputConstraints['Max']:
            OutputLevelCmdString = 'get MTX:mem_512/{0}/0/{1}/0/0/0 0 0\n'.format(self.OutputLevelID, int(qualifier['Output']) - 1)
            self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)

    def __MatchOutputLevel(self, match, tag):

        qualifier = {'Output': str(int(match.group(1).decode()) + 1)}
        value = int(match.group(2).decode()) / 100
        if -138.01 <= value <= 10:
            self.WriteStatus('OutputLevel', value, qualifier)
        else:
            self.Error(['Output Level: Invalid/unexpected response'])

    def SetOutputMute(self, value, qualifier):

        MuteValues = {
            'On':   '0',
            'Off':  '1'
        }

        if self.OutputConstraints['Min'] <= int(qualifier['Output']) <= self.OutputConstraints['Max']:
            OutputMuteCmdString = 'set MTX:mem_512/{0}/1/{1}/0/0/0 0 0 {2}\n'.format(self.OutputLevelID, int(qualifier['Output']) - 1, MuteValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateOutputMute(self, value, qualifier):

        if self.OutputConstraints['Min'] <= int(qualifier['Output']) <= self.OutputConstraints['Max']:
            OutputMuteCmdString = 'get MTX:mem_512/{0}/1/{1}/0/0/0 0 0\n'.format(self.OutputLevelID, int(qualifier['Output']) - 1)
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        MuteValues = {
            '0': 'On',
            '1': 'Off'
        }

        qualifier = {'Output': str(int(match.group(1).decode()) + 1)}
        value = MuteValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 50:
            PresetRecallCmdString = 'ssrecall {0}\n'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        PresetRecallCmdString = 'sscurrent\n'
        self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def __MatchPresetRecall(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PresetRecall', value, None)

    def SetSetCurrentFilePath(self, value, qualifier):

        subfoldernum = qualifier['Sub Folder Number']
        fileindex = qualifier['File Index']

        if 0 <= subfoldernum <= 100 and 0 <= fileindex <= 255:
            SetCurrentFilePathCmdString = 'event MTX:AudioPlayerSetCurrentSong "dirpath=0/{0}|fileindex={1}"\n'.format(subfoldernum, fileindex)
            self.__SetHelper('SetCurrentFilePath', SetCurrentFilePathCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetCurrentFilePath')

    def SetTransport(self, value, qualifier):

        TransportValues = {
            'Play':     'play',
            'Pause':    'pause',
            'Stop':     'stop',
            'Previous': 'prev',
            'Next':     'next'
        }

        TransportCmdString = 'event MTX:AudioPlayerTransport "operation={0}"\n'.format(TransportValues[value])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetZoneGroupMasterDCALevel(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }

        ValueConstraints = {
            'Min': -138.01,
            'Max': 10
        }

        zone_val = int(qualifier['Zone'])
        group_val = qualifier['Group']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and group_val in GroupStates and 1 <= zone_val <= self.zone_value:
            ZoneGroupMasterDCALevelCmdString = 'set MTX:mem_512/60002/1/{0}/{1}/0/0 0 0 {2}\n'.format(zone_val - 1, GroupStates[group_val], int(value * 100))
            self.__SetHelper('ZoneGroupMasterDCALevel', ZoneGroupMasterDCALevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneGroupMasterDCALevel')

    def UpdateZoneGroupMasterDCALevel(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }

        zone_val = int(qualifier['Zone'])
        group_val = qualifier['Group']
        if group_val in GroupStates and 1 <= zone_val <= self.zone_value:
            ZoneGroupMasterDCALevelCmdString = 'get MTX:mem_512/60002/1/{0}/{1}/0/0 0 0\n'.format(zone_val - 1, GroupStates[group_val])
            self.__UpdateHelper('ZoneGroupMasterDCALevel', ZoneGroupMasterDCALevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneGroupMasterDCALevel')

    def __MatchZoneGroupMasterDCALevel(self, match, tag):

        GroupStates = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'E',
            '5': 'F',
            '6': 'G',
            '7': 'H'
        }

        qualifier = {
            'Zone': str(int(match.group(1).decode()) + 1),
            'Group': GroupStates[match.group(2).decode()],
        }
        value = int(match.group(3).decode()) / 100
        if -138.1 <= value <= 10:
            self.WriteStatus('ZoneGroupMasterDCALevel', value, qualifier)
        else:
            self.Error(['Zone Group Master DCA Level: Invalid/unexpected response'])

    def SetZoneGroupMasterDCAMute(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }

        ValueStateValues = {
            'On':   '0',
            'Off':  '1'
        }

        zone_val = int(qualifier['Zone'])
        group_val = qualifier['Group']
        if group_val in GroupStates and 1 <= zone_val <= self.zone_value:
            ZoneGroupMasterDCAMuteCmdString = 'set MTX:mem_512/60003/1/{0}/{1}/0/0 0 0 {2}\n'.format(zone_val - 1, GroupStates[group_val], ValueStateValues[value])
            self.__SetHelper('ZoneGroupMasterDCAMute', ZoneGroupMasterDCAMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneGroupMasterDCAMute')

    def UpdateZoneGroupMasterDCAMute(self, value, qualifier):

        GroupStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7'
        }
        
        zone_val = int(qualifier['Zone'])
        group_val = qualifier['Group']
        if group_val in GroupStates and 1 <= zone_val <= self.zone_value:
            ZoneGroupMasterDCAMuteCmdString = 'get MTX:mem_512/60003/1/{0}/{1}/0/0 0 0\n'.format(zone_val - 1, GroupStates[group_val])
            self.__UpdateHelper('ZoneGroupMasterDCAMute', ZoneGroupMasterDCAMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneGroupMasterDCAMute')

    def __MatchZoneGroupMasterDCAMute(self, match, tag):

        GroupStates = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'E',
            '5': 'F',
            '6': 'G',
            '7': 'H'
        }

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        qualifier = {
            'Zone': str(int(match.group(1).decode()) + 1),
            'Group': GroupStates[match.group(2).decode()],
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('ZoneGroupMasterDCAMute', value, qualifier)

    def SetZoneOutputMasterLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -138.01,
            'Max': 10
        }

        zone_val = int(qualifier['Zone'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= zone_val <= self.zone_value:
            ZoneOutputMasterLevelCmdString = 'set MTX:mem_512/60002/0/{0}/0/0/0 0 0 {1}\n'.format(zone_val - 1, int(value * 100))
            self.__SetHelper('ZoneOutputMasterLevel', ZoneOutputMasterLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneOutputMasterLevel')

    def UpdateZoneOutputMasterLevel(self, value, qualifier):

        zone_val = int(qualifier['Zone'])
        if 1 <= zone_val <= self.zone_value:
            ZoneOutputMasterLevelCmdString = 'get MTX:mem_512/60002/0/{0}/0/0/0 0 0\n'.format(zone_val - 1)
            self.__UpdateHelper('ZoneOutputMasterLevel', ZoneOutputMasterLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneOutputMasterLevel')

    def __MatchZoneOutputMasterLevel(self, match, tag):

        qualifier = {'Zone': str(int(match.group(1).decode()) + 1)}
        value = int(match.group(2).decode()) / 100
        if -138.01 <= value <= 10:
            self.WriteStatus('ZoneOutputMasterLevel', value, qualifier)
        else:
            self.Error(['Zone Output Master Level: Invalid/unexpected response'])

    def SetZoneOutputMasterMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '0',
            'Off':  '1'
        }

        zone_val = int(qualifier['Zone'])
        if 1 <= zone_val <= self.zone_value:
            ZoneOutputMasterMuteCmdString = 'set MTX:mem_512/60003/0/{0}/0/0/0 0 0 {1}\n'.format(zone_val - 1, ValueStateValues[value])
            self.__SetHelper('ZoneOutputMasterMute', ZoneOutputMasterMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneOutputMasterMute')

    def UpdateZoneOutputMasterMute(self, value, qualifier):

        zone_val = int(qualifier['Zone'])
        if 1 <= zone_val <= self.zone_value:
            ZoneOutputMasterMuteCmdString = 'get MTX:mem_512/60003/0/{0}/0/0/0 0 0\n'.format(zone_val - 1)
            self.__UpdateHelper('ZoneOutputMasterMute', ZoneOutputMasterMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneOutputMasterMute')

    def __MatchZoneOutputMasterMute(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        qualifier = {'Zone':  str(int(match.group(1).decode()) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ZoneOutputMasterMute', value, qualifier)

    def SetZoneSourceLevel(self, value, qualifier):

        ModelStates = {
            'MTX3': '20013',
            'MTX5': '20020'
        }

        ValueConstraints = {
            'Min': -138.01,
            'Max': 0
        }

        zone_val = int(qualifier['Zone'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= zone_val <= 8:
            ZoneSourceLevelCmdString = 'set MTX:mem_512/{0}/1/{1}/0/0/0 0 0 {2}\n'.format(ModelStates[self.model], zone_val - 1, int(value * 100))
            self.__SetHelper('ZoneSourceLevel', ZoneSourceLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneSourceLevel')

    def UpdateZoneSourceLevel(self, value, qualifier):

        ModelStates = {
            'MTX3': '20013',
            'MTX5': '20020'
        }

        zone_val = int(qualifier['Zone'])
        if 1 <= zone_val <= 8:
            ZoneSourceLevelCmdString = 'get MTX:mem_512/{0}/1/{1}/0/0/0 0 0\n'.format(ModelStates[self.model], zone_val - 1)
            self.__UpdateHelper('ZoneSourceLevel', ZoneSourceLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneSourceLevel')

    def __MatchZoneSourceLevel(self, match, tag):

        qualifier = {'Zone': str(int(match.group(1).decode()) + 1)}
        value = int(match.group(2).decode()) / 100
        if -138.01 <= value <= 0:
            self.WriteStatus('ZoneSourceLevel', value, qualifier)
        else:
            self.Error(['Zone Source Level: Invalid/unexpected response'])

    def SetZoneSourceMute(self, value, qualifier):

        ModelStates = {
            'MTX3': '20013',
            'MTX5': '20020'
        }

        ValueStateValues = {
            'On':   '0',
            'Off':  '1'
        }

        zone_val = int(qualifier['Zone'])
        if 1 <= zone_val <= 8:
            ZoneSourceMuteCmdString = 'set MTX:mem_512/{0}/1/{1}/0/1/0 0 0 {2}\n'.format(ModelStates[self.model], zone_val - 1, ValueStateValues[value])
            self.__SetHelper('ZoneSourceMute', ZoneSourceMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneSourceMute')

    def UpdateZoneSourceMute(self, value, qualifier):

        ModelStates = {
            'MTX3': '20013',
            'MTX5': '20020'
        }
        zone_val = int(qualifier['Zone'])
        if 1 <= zone_val <= 8:
            ZoneSourceMuteCmdString = 'get MTX:mem_512/{0}/1/{1}/0/1/0 0 0\n'.format(ModelStates[self.model], zone_val - 1)
            self.__UpdateHelper('ZoneSourceMute', ZoneSourceMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneSourceMute')

    def __MatchZoneSourceMute(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        qualifier = {'Zone': str(int(match.group(1).decode()) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ZoneSourceMute', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.RunModeDisabled:
            self.Send('devstatus runmode\n')

        if not self.RunModeDisabled:
            self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.RunModeDisabled:
            self.Send('devstatus runmode\n')

        if self.Unidirectional == 'True' or self.RunModeDisabled:
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

        self.counter = 0

        error_map = {
            'UnknownCommand':   'Unknown command',
            'WrongFormat':      'Invalid parameter format',
            'InvalidArgument':  'Invalid argument',
            'UnknownAddress':   'Specified address does not exist',
            'UnknownEventID':   'Specified event ID does not exist',
            'TooLongCommand':   'Command was too long',
            'AccessDenied':     'Device is not in an normal running state',
            'Busy':             'Device is busy',
            'ReadOnly':         'Parameter is read-only',
            'NoPermission':     'No access permission',
            'InternalError':    'Internal error'
        }

        self.Error(['An error occurred: {}.'.format(error_map.get(match.group(1).decode(), 'Unknown error'))])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.RunModeDisabled = True

    def yama_25_367_MTX3(self):

        self.InputConstraints = {
            'Min': 1,
            'Max': 22
        }
        self.OutputConstraints = {
            'Min': 1,
            'Max': 8
        }
        self.TieInputConstraints = {
            'Min': 1,
            'Max': 26
        }

        self.OutputLevelID = '20017'
        self.zone_value = 8
        self.model = 'MTX3'

    def yama_25_367_MTX5(self):

        self.InputConstraints = {
            'Min': 1,
            'Max': 30
        }
        self.OutputConstraints = {
            'Min': 1,
            'Max': 16
        }
        self.TieInputConstraints = {
            'Min': 1,
            'Max': 34
        }

        self.OutputLevelID = '20024'
        self.zone_value = 16
        self.model = 'MTX5'

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