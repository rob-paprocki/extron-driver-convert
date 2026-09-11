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
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Firmware': { 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'InputVolume': {'Parameters':['Input'], 'Status': {}},
            'MatrixMixerMute': {'Parameters':['Input','Output'], 'Status': {}},
            'OutputMute': {'Parameters':['Output'], 'Status': {}},
            'OutputVolume': {'Parameters':['Output'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'SerialNumber': { 'Status': {}},
            'Volume': {'Parameters': ['Channel'], 'Status': {}}
        }

        self.RunModeDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) (?:[sg]et)? ?AMP:Ch/Mute ([0-3]) 0 ([01]).*\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devstatus error "(none|warning|error|fault).*"\n'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devinfo version ["\x1c]([\w.]+)["\x1d].*\n'), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) (?:[sg]et)? ?PCD:Input/On (\d{1,2}) 0 ([01]).*\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) (?:[sg]et)? ?PCD:Input/Level (\d{1,2}) 0 (-?\d+).*\n'), self.__MatchInputVolume, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) (?:[sg]et)? ?PCD:MatrixMixer/Send/On (\d{1,2}) ([0-7]) ([01]).*\n'), self.__MatchMatrixMixerMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) (?:[sg]et)? ?PCD:MatrixMixer/Out/On ([0-7]) 0 ([01]).*\n'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) (?:[sg]et)? ?PCD:MatrixMixer/Out/Level ([0-7]) 0 (-?\d+).*\n'), self.__MatchOutputVolume, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) (?:[sg]et)? ?AMP:Power 0 0 ([01]).*\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devinfo serialno ["\x1c]([\w.]+)["\x1d].*\n'), self.__MatchSerialNumber, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) (?:[sg]et)? ?AMP:Ch/Volume ([0-3]) 0 (-?\d+).*\n'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devstatus runmode "normal"\n'), self.__MatchRunMode, None)
            
    def __MatchRunMode(self, match, tag):
        
        self.RunModeDisabled = False

        self.Send('scpmode encoding ascii\n')
        self.Send('scpmode valuetype raw\n')

    def SetAudioMute(self, value, qualifier):

        ChannelStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }
        ch = qualifier['Channel']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if ch in ChannelStates and value in ValueStateValues:
            AudioMuteCmdString = 'set AMP:Ch/Mute {} 0 {}\n'.format(ChannelStates[ch], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ChannelStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }
        ch = qualifier['Channel']

        if ch in ChannelStates:
            AudioMuteCmdString = 'get AMP:Ch/Mute {} 0\n'.format(ChannelStates[ch])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ChannelStates = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'devstatus error\n'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            'none':     'Normal',
            'warning':  'Warning',
            'error':    'Error',
            'fault':    'Fault'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def UpdateFirmware(self, value, qualifier):

        FirmwareCmdString = 'devinfo version\n'
        self.__UpdateHelper('Firmware', FirmwareCmdString, value, qualifier)

    def __MatchFirmware(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Firmware', value, None)

    def SetInputMute(self, value, qualifier):

        InputStates = {
            'Dante Input 1': '0',
            'Dante Input 2': '1',
            'Dante Input 3': '2',
            'Dante Input 4': '3',
            'Dante Input 5': '4',
            'Dante Input 6': '5',
            'Dante Input 7': '6',
            'Dante Input 8': '7',
            'Dante Input 9': '8',
            'Dante Input 10': '9',
            'Dante Input 11': '10',
            'Dante Input 12': '11',
            'Dante Input 13': '12',
            'Dante Input 14': '13',
            'Dante Input 15': '14',
            'Dante Input 16': '15',
            'Analog Input 1': '16',
            'Analog Input 2': '17',
            'Analog Input 3': '18',
            'Analog Input 4': '19'
            }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if qualifier['Input'] in InputStates and value in ValueStateValues:
            InputMuteCmdString = 'set PCD:Input/On {} 0 {}\n'.format(InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        InputStates = {
            'Dante Input 1': '0',
            'Dante Input 2': '1',
            'Dante Input 3': '2',
            'Dante Input 4': '3',
            'Dante Input 5': '4',
            'Dante Input 6': '5',
            'Dante Input 7': '6',
            'Dante Input 8': '7',
            'Dante Input 9': '8',
            'Dante Input 10': '9',
            'Dante Input 11': '10',
            'Dante Input 12': '11',
            'Dante Input 13': '12',
            'Dante Input 14': '13',
            'Dante Input 15': '14',
            'Dante Input 16': '15',
            'Analog Input 1': '16',
            'Analog Input 2': '17',
            'Analog Input 3': '18',
            'Analog Input 4': '19'
            }

        if qualifier['Input'] in InputStates:
            InputMuteCmdString = 'get PCD:Input/On {} 0\n'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        InputStates = {
            '0': 'Dante Input 1',
            '1': 'Dante Input 2',
            '2': 'Dante Input 3',
            '3': 'Dante Input 4',
            '4': 'Dante Input 5',
            '5': 'Dante Input 6',
            '6': 'Dante Input 7',
            '7': 'Dante Input 8',
            '8': 'Dante Input 9',
            '9': 'Dante Input 10',
            '10': 'Dante Input 11',
            '11': 'Dante Input 12',
            '12': 'Dante Input 13',
            '13': 'Dante Input 14',
            '14': 'Dante Input 15',
            '15': 'Dante Input 16',
            '16': 'Analog Input 1',
            '17': 'Analog Input 2',
            '18': 'Analog Input 3',
            '19': 'Analog Input 4'
            }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetInputVolume(self, value, qualifier):

        InputStates = {
            'Dante Input 1': '0',
            'Dante Input 2': '1',
            'Dante Input 3': '2',
            'Dante Input 4': '3',
            'Dante Input 5': '4',
            'Dante Input 6': '5',
            'Dante Input 7': '6',
            'Dante Input 8': '7',
            'Dante Input 9': '8',
            'Dante Input 10': '9',
            'Dante Input 11': '10',
            'Dante Input 12': '11',
            'Dante Input 13': '12',
            'Dante Input 14': '13',
            'Dante Input 15': '14',
            'Dante Input 16': '15',
            'Analog Input 1': '16',
            'Analog Input 2': '17',
            'Analog Input 3': '18',
            'Analog Input 4': '19'
            }

        if qualifier['Input'] in InputStates and -90 <= value <= 10:
            InputVolumeCmdString = 'set PCD:Input/Level {} 0 {}\n'.format(InputStates[qualifier['Input']], int(value * 100))
            self.__SetHelper('InputVolume', InputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputVolume')

    def UpdateInputVolume(self, value, qualifier):

        InputStates = {
            'Dante Input 1': '0',
            'Dante Input 2': '1',
            'Dante Input 3': '2',
            'Dante Input 4': '3',
            'Dante Input 5': '4',
            'Dante Input 6': '5',
            'Dante Input 7': '6',
            'Dante Input 8': '7',
            'Dante Input 9': '8',
            'Dante Input 10': '9',
            'Dante Input 11': '10',
            'Dante Input 12': '11',
            'Dante Input 13': '12',
            'Dante Input 14': '13',
            'Dante Input 15': '14',
            'Dante Input 16': '15',
            'Analog Input 1': '16',
            'Analog Input 2': '17',
            'Analog Input 3': '18',
            'Analog Input 4': '19'
            }

        if qualifier['Input'] in InputStates:
            InputVolumeCmdString = 'get PCD:Input/Level {} 0\n'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('InputVolume', InputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputVolume')

    def __MatchInputVolume(self, match, tag):

        InputStates = {
            '0': 'Dante Input 1',
            '1': 'Dante Input 2',
            '2': 'Dante Input 3',
            '3': 'Dante Input 4',
            '4': 'Dante Input 5',
            '5': 'Dante Input 6',
            '6': 'Dante Input 7',
            '7': 'Dante Input 8',
            '8': 'Dante Input 9',
            '9': 'Dante Input 10',
            '10': 'Dante Input 11',
            '11': 'Dante Input 12',
            '12': 'Dante Input 13',
            '13': 'Dante Input 14',
            '14': 'Dante Input 15',
            '15': 'Dante Input 16',
            '16': 'Analog Input 1',
            '17': 'Analog Input 2',
            '18': 'Analog Input 3',
            '19': 'Analog Input 4'
            }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = int(match.group(2).decode()) / 100
        if -90 <= value <= 10:
            self.WriteStatus('InputVolume', value, qualifier)

    def SetMatrixMixerMute(self, value, qualifier):

        InputStates = {
            'Dante Input 1': '0',
            'Dante Input 2': '1',
            'Dante Input 3': '2',
            'Dante Input 4': '3',
            'Dante Input 5': '4',
            'Dante Input 6': '5',
            'Dante Input 7': '6',
            'Dante Input 8': '7',
            'Dante Input 9': '8',
            'Dante Input 10': '9',
            'Dante Input 11': '10',
            'Dante Input 12': '11',
            'Dante Input 13': '12',
            'Dante Input 14': '13',
            'Dante Input 15': '14',
            'Dante Input 16': '15',
            'Analog Input 1': '16',
            'Analog Input 2': '17',
            'Analog Input 3': '18',
            'Analog Input 4': '19'
            }

        OutputStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'Dante Output 1': '4',
            'Dante Output 2': '5',
            'Dante Output 3': '6',
            'Dante Output 4': '7'
            }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if qualifier['Input'] in InputStates and qualifier['Output'] in OutputStates and value in ValueStateValues:
            MatrixMixerMuteCmdString = 'set PCD:MatrixMixer/Send/On {} {} {}\n'.format(InputStates[qualifier['Input']], OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('MatrixMixerMute', MatrixMixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerMute')

    def UpdateMatrixMixerMute(self, value, qualifier):

        InputStates = {
            'Dante Input 1': '0',
            'Dante Input 2': '1',
            'Dante Input 3': '2',
            'Dante Input 4': '3',
            'Dante Input 5': '4',
            'Dante Input 6': '5',
            'Dante Input 7': '6',
            'Dante Input 8': '7',
            'Dante Input 9': '8',
            'Dante Input 10': '9',
            'Dante Input 11': '10',
            'Dante Input 12': '11',
            'Dante Input 13': '12',
            'Dante Input 14': '13',
            'Dante Input 15': '14',
            'Dante Input 16': '15',
            'Analog Input 1': '16',
            'Analog Input 2': '17',
            'Analog Input 3': '18',
            'Analog Input 4': '19'
            }

        OutputStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'Dante Output 1': '4',
            'Dante Output 2': '5',
            'Dante Output 3': '6',
            'Dante Output 4': '7'
            }

        if qualifier['Input'] in InputStates and qualifier['Output'] in OutputStates:
            MatrixMixerMuteCmdString = 'get PCD:MatrixMixer/Send/On {} {}\n'.format(InputStates[qualifier['Input']], OutputStates[qualifier['Output']])
            self.__UpdateHelper('MatrixMixerMute', MatrixMixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixMixerMute')

    def __MatchMatrixMixerMute(self, match, tag):

        InputStates = {
            '0': 'Dante Input 1',
            '1': 'Dante Input 2',
            '2': 'Dante Input 3',
            '3': 'Dante Input 4',
            '4': 'Dante Input 5',
            '5': 'Dante Input 6',
            '6': 'Dante Input 7',
            '7': 'Dante Input 8',
            '8': 'Dante Input 9',
            '9': 'Dante Input 10',
            '10': 'Dante Input 11',
            '11': 'Dante Input 12',
            '12': 'Dante Input 13',
            '13': 'Dante Input 14',
            '14': 'Dante Input 15',
            '15': 'Dante Input 16',
            '16': 'Analog Input 1',
            '17': 'Analog Input 2',
            '18': 'Analog Input 3',
            '19': 'Analog Input 4'
            }

        OutputStates = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'Dante Output 1',
            '5': 'Dante Output 2',
            '6': 'Dante Output 3',
            '7': 'Dante Output 4'
            }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        qualifier['Output'] = OutputStates[match.group(2).decode()]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('MatrixMixerMute', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        OutputStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'Dante Output 1': '4',
            'Dante Output 2': '5',
            'Dante Output 3': '6',
            'Dante Output 4': '7'
            }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if qualifier['Output'] in OutputStates and value in ValueStateValues:
            OutputMuteCmdString = 'set PCD:MatrixMixer/Out/On {} 0 {}\n'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        OutputStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'Dante Output 1': '4',
            'Dante Output 2': '5',
            'Dante Output 3': '6',
            'Dante Output 4': '7'
            }

        if qualifier['Output'] in OutputStates:
            OutputMuteCmdString = 'get PCD:MatrixMixer/Out/On {} 0\n'.format(OutputStates[qualifier['Output']])
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        OutputStates = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'Dante Output 1',
            '5': 'Dante Output 2',
            '6': 'Dante Output 3',
            '7': 'Dante Output 4'
            }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetOutputVolume(self, value, qualifier):

        OutputStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'Dante Output 1': '4',
            'Dante Output 2': '5',
            'Dante Output 3': '6',
            'Dante Output 4': '7'
            }

        if qualifier['Output'] in OutputStates and -90 <= value <= 10:
            OutputVolumeCmdString = 'set PCD:MatrixMixer/Out/Level {} 0 {}\n'.format(OutputStates[qualifier['Output']], int(value * 100))
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        OutputStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'Dante Output 1': '4',
            'Dante Output 2': '5',
            'Dante Output 3': '6',
            'Dante Output 4': '7'
            }

        if qualifier['Output'] in OutputStates:
            OutputVolumeCmdString = 'get PCD:MatrixMixer/Out/Level {} 0\n'.format(OutputStates[qualifier['Output']])
            self.__UpdateHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputVolume')

    def __MatchOutputVolume(self, match, tag):

        OutputStates = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'Dante Output 1',
            '5': 'Dante Output 2',
            '6': 'Dante Output 3',
            '7': 'Dante Output 4'
            }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = int(match.group(2).decode()) / 100
        if -90 <= value <= 10:
            self.WriteStatus('OutputVolume', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':       '1',
            'Standby':  '0'
        }

        if value in ValueStateValues:
            PowerCmdString = 'set AMP:Power 0 0 {}\n'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        if self.RunModeDisabled:
            self.Send('devstatus runmode\n')
        
        PowerCmdString = 'get AMP:Power 0 0\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Standby'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 32:
            PresetRecallCmdString = 'ssrecall_ex preset {}\n'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
            
    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 32:
            PresetSaveCmdString = 'ssupdate_ex preset {}\n'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')
            
    def UpdateSerialNumber(self, value, qualifier):

        SerialNumberCmdString = 'devinfo serialno\n'
        self.__UpdateHelper('SerialNumber', SerialNumberCmdString, value, qualifier)

    def __MatchSerialNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SerialNumber', value, None)

    def SetVolume(self, value, qualifier):

        ChannelStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }
        ch = qualifier['Channel']

        if ch in ChannelStates and -99 <= value <= 0:
            VolumeCmdString = 'set AMP:Ch/Volume {} 0 {}\n'.format(ChannelStates[ch], int(value * 100))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ChannelStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }
        ch = qualifier['Channel']

        if ch in ChannelStates:
            VolumeCmdString = 'get AMP:Ch/Volume {} 0\n'.format(ChannelStates[ch])
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        ChannelStates = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        value = int(match.group(2).decode()) / 100
        if -99 <= value <= 0:
            self.WriteStatus('Volume', value, qualifier)

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
        
        self.RunModeDisabled = True
        
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