# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import struct

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
            'AuxInFaderLevel': {'Parameters':['Number'], 'Status': {}},
            'AuxInFaderMute': {'Parameters':['Number'], 'Status': {}},
            'BusFaderLevel': {'Parameters':['Number'], 'Status': {}},
            'BusFaderMute': {'Parameters':['Number'], 'Status': {}},
            'ChannelFaderLevel': {'Parameters':['Number'], 'Status': {}},
            'ChannelFaderMute': {'Parameters':['Number'], 'Status': {}},
            'DCAFaderLevel': {'Parameters':['Number'], 'Status': {}},
            'DCAFaderMute': {'Parameters':['Number'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'FXReturnFaderLevel': {'Parameters':['Number'], 'Status': {}},
            'FXReturnFaderMute': {'Parameters':['Number'], 'Status': {}},
            'GroupMute': {'Parameters':['Number'], 'Status': {}},
            'MainFaderLevel': {'Parameters':['Type'], 'Status': {}},
            'MainFaderMute': {'Parameters':['Type'], 'Status': {}},
            'MatrixFaderLevel': {'Parameters':['Number'], 'Status': {}},
            'MatrixFaderMute': {'Parameters':['Number'], 'Status': {}},
            'SceneRecall': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'auxin/0?([1-8])/mix/fader\x00{1,4},f\x00\x00([\x00-\xFF]{4})'), self.__MatchAuxInFaderLevel, None)
            self.AddMatchString(re.compile(b'auxin/0?([1-8])/mix/on\x00{1,4},i\x00\x00\x00\x00\x00([\x00\x01])'), self.__MatchAuxInFaderMute, None)
            self.AddMatchString(re.compile(b'bus/([0-9]{1,2})/mix/fader\x00{1,4},f\x00\x00([\x00-\xFF]{4})'), self.__MatchBusFaderLevel, None)
            self.AddMatchString(re.compile(b'bus/([0-9]{1,2})/mix/on\x00{1,4},i\x00\x00\x00\x00\x00([\x00\x01])'), self.__MatchBusFaderMute, None)
            self.AddMatchString(re.compile(b'ch/([0-9]{1,2})/mix/fader\x00{1,4},f\x00\x00([\x00-\xFF]{4})'), self.__MatchChannelFaderLevel, None)
            self.AddMatchString(re.compile(b'ch/([0-9]{1,2})/mix/on\x00{1,4},i\x00\x00\x00\x00\x00([\x00\x01])'), self.__MatchChannelFaderMute, None)
            self.AddMatchString(re.compile(b'dca/0?([1-8])/fader\x00{1,4},f\x00\x00([\x00-\xFF]{4})'), self.__MatchDCAFaderLevel, None)
            self.AddMatchString(re.compile(b'dca/0?([1-8])/on\x00{1,4},i\x00\x00\x00\x00\x00([\x00\x01])'), self.__MatchDCAFaderMute, None)
            self.AddMatchString(re.compile(b'info\x00{1,4},ssss\x00\x00\x00(?:[^\x00]+\x00{1,4}){3}([^\x00]+)\x00{1,4}'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'fxrtn/0?([1-8])/mix/fader\x00{1,4},f\x00\x00([\x00-\xFF]{4})'), self.__MatchFXReturnFaderLevel, None)
            self.AddMatchString(re.compile(b'fxrtn/0?([1-8])/mix/on\x00{1,4},i\x00\x00\x00\x00\x00([\x00\x01])'), self.__MatchFXReturnFaderMute, None)
            self.AddMatchString(re.compile(b'config/mute/0?([1-6])\x00{1,4},i\x00\x00\x00\x00\x00([\x00\x01])'), self.__MatchGroupMute, None)
            self.AddMatchString(re.compile(b'main/(m|st)/mix/fader\x00{1,4},f\x00\x00([\x00-\xFF]{4})'), self.__MatchMainFaderLevel, None)
            self.AddMatchString(re.compile(b'main/(m|st)/mix/on\x00{1,4},i\x00\x00\x00\x00\x00([\x00\x01])'), self.__MatchMainFaderMute, None)
            self.AddMatchString(re.compile(b'mtx/0?([1-6])/mix/fader\x00{1,4},f\x00\x00([\x00-\xFF]{4})'), self.__MatchMatrixFaderLevel, None)
            self.AddMatchString(re.compile(b'mtx/0?([1-6])/mix/on\x00{1,4},i\x00\x00\x00\x00\x00([\x00\x01])'), self.__MatchMatrixFaderMute, None)

    def pad(self, value):

        if not isinstance(value, str):
            raise ValueError()

        to_pad = 4 - (len(value) % 4)
        return (value + ('\x00' * to_pad)).encode(encoding='iso-8859-1')

    def itoh(self, value):

        if not isinstance(value, int):
            raise ValueError()

        return struct.pack('>I', value)

    def ftoh(self, value):

        if not isinstance(value, float):
            raise ValueError()

        return struct.pack('>f', value)

    def hftoi(self, value):
        if not isinstance(value, bytes):
            raise ValueError()

        return int(round(struct.unpack('>f', value)[0], 2) * 100)

    def build_set_string(self, command, types, *values):
        try:
            command = self.pad(command) + self.pad(',' + types)

            for i in range(0, len(types)):
                if types[i] == 's':
                    command += self.pad(values[i])
                elif types[i] == 'f':
                    command += self.ftoh(values[i])
                elif types[i] == 'i':
                    command += self.itoh(values[i])
                else:
                    raise ValueError()
            return command

        except ValueError:
            self.Discard('Invalid Command')

    def build_get_string(self, command):

        return self.pad(command)
    
    def SetAuxInFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        number_val = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(number_val) <= 8:
            AuxInFaderLevelCmdString = self.build_set_string('/auxin/{0:02d}/mix/fader'.format(int(number_val)),
                                                             'f',
                                                             value / 100)
            self.__SetHelper('AuxInFaderLevel', AuxInFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAuxInFaderLevel')

    def UpdateAuxInFaderLevel(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 8:
            AuxInFaderLevelCmdString = self.build_get_string('/auxin/{0:02d}/mix/fader'.format(int(number_val)))
            self.__UpdateHelper('AuxInFaderLevel', AuxInFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAuxInFaderLevel')

    def __MatchAuxInFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = self.hftoi(match.group(2))
        self.WriteStatus('AuxInFaderLevel', value, qualifier)

    def SetAuxInFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On':  0, 
            'Off': 1
        }

        number_val = qualifier['Number']
        if value in ValueStateValues and 1 <= int(number_val) <= 8:
            AuxInFaderMuteCmdString = self.build_set_string('/auxin/{0:02d}/mix/on'.format(int(number_val)),
                                                            'i',
                                                            ValueStateValues[value])
            self.__SetHelper('AuxInFaderMute', AuxInFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAuxInFaderMute')

    def UpdateAuxInFaderMute(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 8:
            AuxInFaderMuteCmdString = self.build_get_string('/auxin/{0:02d}/mix/'.format(int(number_val)))
            self.__UpdateHelper('AuxInFaderMute', AuxInFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAuxInFaderMute')

    def __MatchAuxInFaderMute(self, match, tag):

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('AuxInFaderMute', value, qualifier)

    def SetBusFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 16 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BusFaderLevelCmdString = self.build_set_string('/bus/{0:02d}/mix/fader'.format(int(number_val)),
                                                           'f',
                                                           value / 100)
            self.__SetHelper('BusFaderLevel', BusFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBusFaderLevel')

    def UpdateBusFaderLevel(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 16:
            BusFaderLevelCmdString = self.build_get_string('/bus/{0:02d}/mix/fader'.format(int(number_val)))
            self.__UpdateHelper('BusFaderLevel', BusFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBusFaderLevel')

    def __MatchBusFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = self.hftoi(match.group(2))
        self.WriteStatus('BusFaderLevel', value, qualifier)

    def SetBusFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On':   0,
            'Off':  1
        }

        number_val = qualifier['Number']
        if value in ValueStateValues and 1 <= int(number_val) <= 16:
            BusFaderMuteCmdString = self.build_set_string('/bus/{0:02d}/mix/on'.format(int(number_val)),
                                                          'i',
                                                          ValueStateValues[value])
            self.__SetHelper('BusFaderMute', BusFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBusFaderMute')

    def UpdateBusFaderMute(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 16:
            BusFaderMuteCmdString = self.build_get_string('/bus/{0:02d}/mix/'.format(int(number_val)))
            self.__UpdateHelper('BusFaderMute', BusFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBusFaderMute')

    def __MatchBusFaderMute(self, match, tag):

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('BusFaderMute', value, qualifier)

    def SetChannelFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        number_val = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(number_val) <= 32:
            ChannelFaderLevelCmdString = self.build_set_string('/ch/{0:02d}/mix/fader'.format(int(number_val)),
                                                               'f',
                                                               value / 100)
            self.__SetHelper('ChannelFaderLevel', ChannelFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelFaderLevel')

    def UpdateChannelFaderLevel(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 32:
            ChannelFaderLevelCmdString = self.build_get_string('/ch/{0:02d}/mix/fader'.format(int(number_val)))
            self.__UpdateHelper('ChannelFaderLevel', ChannelFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelFaderLevel')

    def __MatchChannelFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = self.hftoi(match.group(2))
        self.WriteStatus('ChannelFaderLevel', value, qualifier)

    def SetChannelFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On':   0,
            'Off':  1
        }

        number_val = qualifier['Number']
        if value in ValueStateValues and 1 <= int(number_val) <= 32:
            ChannelFaderMuteCmdString = self.build_set_string('/ch/{0:02d}/mix/on'.format(int(number_val)),
                                                              'i',
                                                              ValueStateValues[value])
            self.__SetHelper('ChannelFaderMute', ChannelFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelFaderMute')

    def UpdateChannelFaderMute(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 32:
            ChannelFaderMuteCmdString = self.build_get_string('/ch/{0:02d}/mix/'.format(int(number_val)))
            self.__UpdateHelper('ChannelFaderMute', ChannelFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelFaderMute')

    def __MatchChannelFaderMute(self, match, tag):

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('ChannelFaderMute', value, qualifier)

    def SetDCAFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        number_val = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(number_val) <= 8:
            DCAFaderLevelCmdString = self.build_set_string('/dca/{0}/fader'.format(int(number_val)),
                                                           'f',
                                                           value / 100)
            self.__SetHelper('DCAFaderLevel', DCAFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDCAFaderLevel')

    def UpdateDCAFaderLevel(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 8:
            DCAFaderLevelCmdString = self.build_get_string('/dca/{0}/fader'.format(int(number_val)))
            self.__UpdateHelper('DCAFaderLevel', DCAFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDCAFaderLevel')

    def __MatchDCAFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = self.hftoi(match.group(2))
        self.WriteStatus('DCAFaderLevel', value, qualifier)

    def SetDCAFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On':   0,
            'Off':  1
        }

        number_val = qualifier['Number']
        if value in ValueStateValues and 1 <= int(number_val) <= 8:
            DCAFaderMuteCmdString = self.build_set_string('/dca/{0}/on'.format(int(number_val)),
                                                          'i',
                                                          ValueStateValues[value])
            self.__SetHelper('DCAFaderMute', DCAFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDCAFaderMute')

    def UpdateDCAFaderMute(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 8:
            DCAFaderMuteCmdString = self.build_get_string('/dca/{0}/on/'.format(int(number_val)))
            self.__UpdateHelper('DCAFaderMute', DCAFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDCAFaderMute')

    def __MatchDCAFaderMute(self, match, tag):

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('DCAFaderMute', value, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = self.build_get_string('/info')
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):
        
        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetFXReturnFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        number_val = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(number_val) <= 8:
            FXReturnFaderLevelCmdString = self.build_set_string('/fxrtn/{0:02d}/mix/fader'.format(int(number_val)),
                                                                'f',
                                                                value / 100)
            self.__SetHelper('FXReturnFaderLevel', FXReturnFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFXReturnFaderLevel')

    def UpdateFXReturnFaderLevel(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 8:
            FXReturnFaderLevelCmdString = self.build_get_string('/fxrtn/{0:02d}/mix/fader'.format(int(number_val)))
            self.__UpdateHelper('FXReturnFaderLevel', FXReturnFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFXReturnFaderLevel')

    def __MatchFXReturnFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = self.hftoi(match.group(2))
        self.WriteStatus('FXReturnFaderLevel', value, qualifier)

    def SetFXReturnFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On':   0,
            'Off':  1
        }

        number_val = qualifier['Number']
        if value in ValueStateValues and 1 <= int(number_val) <= 8:
            FXReturnFaderMuteCmdString = self.build_set_string('/fxrtn/{0:02d}/mix/on'.format(int(number_val)),
                                                               'i',
                                                               ValueStateValues[value])
            self.__SetHelper('FXReturnFaderMute', FXReturnFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFXReturnFaderMute')

    def UpdateFXReturnFaderMute(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 8:
            FXReturnFaderMuteCmdString = self.build_get_string('/fxrtn/{0:02d}/mix/'.format(int(number_val)))
            self.__UpdateHelper('FXReturnFaderMute', FXReturnFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFXReturnFaderMute')

    def __MatchFXReturnFaderMute(self, match, tag):

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('FXReturnFaderMute', value, qualifier)

    def SetGroupMute(self, value, qualifier):

        ValueStateValues = {
            'On':  'ON',
            'Off': 'OFF'
        }

        number_val = qualifier['Number']
        if value in ValueStateValues and 1 <= int(number_val) <= 6:
            GroupMuteCmdString = self.build_set_string('/config/mute/{0}'.format(int(number_val)),
                                                       's',
                                                       ValueStateValues[value])
            self.__SetHelper('GroupMute', GroupMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 6:
            GroupMuteCmdString = self.build_get_string('/config/mute/{0}'.format(int(number_val)))
            self.__UpdateHelper('GroupMute', GroupMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def __MatchGroupMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('GroupMute', value, qualifier)

    def SetMainFaderLevel(self, value, qualifier):

        TypeStates = {
            'Mono':   'm', 
            'Stereo': 'st'
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        type_val = qualifier['Type']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and type_val in TypeStates:
            MainFaderLevelCmdString = self.build_set_string('/main/{0}/mix/fader'.format(TypeStates[type_val]),
                                                            'f',
                                                            value / 100)
            self.__SetHelper('MainFaderLevel', MainFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMainFaderLevel')

    def UpdateMainFaderLevel(self, value, qualifier):

        TypeStates = {
            'Mono':   'm', 
            'Stereo': 'st'
        }

        type_val = qualifier['Type']
        if type_val in TypeStates:
            MainFaderLevelCmdString = self.build_get_string('/main/{0}/mix/fader'.format(TypeStates[type_val]))
            self.__UpdateHelper('MainFaderLevel', MainFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMainFaderLevel')

    def __MatchMainFaderLevel(self, match, tag):

        TypeStates = {
            'm':  'Mono',
            'st': 'Stereo'
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        value = self.hftoi(match.group(2))
        self.WriteStatus('MainFaderLevel', value, qualifier)

    def SetMainFaderMute(self, value, qualifier):

        TypeStates = {
            'Mono':   'm', 
            'Stereo': 'st'
        }

        ValueStateValues = {
            'On':  0, 
            'Off': 1
        }

        type_val = qualifier['Type']
        if value in ValueStateValues and type_val in TypeStates:
            MainFaderMuteCmdString = self.build_set_string('/main/{0}/mix/on'.format(TypeStates[type_val]),
                                                           'i',
                                                           ValueStateValues[value])
            self.__SetHelper('MainFaderMute', MainFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMainFaderMute')

    def UpdateMainFaderMute(self, value, qualifier):

        TypeStates = {
            'Mono':   'm', 
            'Stereo': 'st'
        }

        type_val = qualifier['Type']
        if type_val in TypeStates:
            MainFaderMuteCmdString = self.build_get_string('/main/{0}/mix/'.format(TypeStates[type_val]))
            self.__UpdateHelper('MainFaderMute', MainFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMainFaderMute')

    def __MatchMainFaderMute(self, match, tag):

        TypeStates = {
            'm':  'Mono',
            'st': 'Stereo'
        }

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('MainFaderMute', value, qualifier)

    def SetMatrixFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        number_val = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(number_val) <= 6:
            MatrixFaderLevelCmdString = self.build_set_string('/mtx/{0:02d}/mix/fader'.format(int(number_val)),
                                                              'f',
                                                              value / 100)
            self.__SetHelper('MatrixFaderLevel', MatrixFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixFaderLevel')

    def UpdateMatrixFaderLevel(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 6:
            MatrixFaderLevelCmdString = self.build_get_string('/mtx/{0:02d}/mix/fader'.format(int(number_val)))
            self.__UpdateHelper('MatrixFaderLevel', MatrixFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixFaderLevel')

    def __MatchMatrixFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = self.hftoi(match.group(2))
        self.WriteStatus('MatrixFaderLevel', value, qualifier)

    def SetMatrixFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On':   0,
            'Off':  1
        }

        number_val = qualifier['Number']
        if value in ValueStateValues and 1 <= int(number_val) <= 6:
            MatrixFaderMuteCmdString = self.build_set_string('/mtx/{0:02d}/mix/on'.format(int(number_val)),
                                                             'i',
                                                             ValueStateValues[value])
            self.__SetHelper('MatrixFaderMute', MatrixFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixFaderMute')

    def UpdateMatrixFaderMute(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= 6:
            MatrixFaderMuteCmdString = self.build_get_string('/mtx/{0:02d}/mix/'.format(int(number_val)))
            self.__UpdateHelper('MatrixFaderMute', MatrixFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixFaderMute')

    def __MatchMatrixFaderMute(self, match, tag):

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }

        qualifier = {}
        qualifier['Number'] = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('MatrixFaderMute', value, qualifier)

    def SetSceneRecall(self, value, qualifier):

        if 1 <= int(value) <= 100:
            SceneRecallCmdString = self.build_set_string('/load',
                                                         'si',
                                                         'scene', int(value) - 1)
            self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneRecall')

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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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