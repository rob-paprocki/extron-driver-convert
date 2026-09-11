# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import unpack

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
        self._ReplyPort = 0
        
        self.Models = {
            'Duecanali 804 DSP+D': self.psft_25_3633_duo,
            'Duecanali 1604 DSP+D': self.psft_25_3633_duo,
            'Duecanali 4804 DSP+D': self.psft_25_3633_duo,
            'Ottocanali 12K4 DSP+D': self.psft_25_3633_otto,
            'Ottocanali 8K4 DSP+D': self.psft_25_3633_otto,
            'Ottocanali 4K4 DSP+D': self.psft_25_3633_otto,
            'Quattrocanali 1204 DSP+D': self.psft_25_3633_quattro,
            'Quattrocanali 2404 DSP+D': self.psft_25_3633_quattro,
            'Quattrocanali 4804 DSP+D': self.psft_25_3633_quattro,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelAlarmStatus': {'Parameters':['Type','Channel'], 'Status': {}},
            'ChannelBroadcastImpedance': {'Parameters':['Channel'], 'Status': {}},
            'ChannelFrequencySpecificImpedance': {'Parameters':['Channel'], 'Status': {}},
            'ChannelInputPilotToneLevel': {'Parameters':['Channel'], 'Status': {}},
            'ChannelLoadStatus': {'Parameters':['Type','Channel'], 'Status': {}},
            'ChannelValueDetected': {'Parameters':['Type','Channel'], 'Status': {}},
            'ChannelValueValidity': {'Parameters':['Type','Channel'], 'Status': {}},
            'GlobalAlarmStatus': {'Parameters':['Type'], 'Status': {}},
            'GPIOAlarmStatus': {'Parameters':['Channel'], 'Status': {}},
            'InputGain': {'Parameters':['Channel'], 'Status': {}},
            'InputMute': {'Parameters':['Channel'], 'Status': {}},
            'OutputGain': {'Parameters':['Channel'], 'Status': {}},
            'OutputMute': {'Parameters':['Channel'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetDelete': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}}
        }
                    
        self.table = []
        poly = 0xA001
        for byte in range(256): 
            crc = byte
            for bit in range(8):
                if crc & 1:
                    crc = poly ^ (crc >> 1)
                else:
                    crc = crc >> 1              
            self.table.append(crc >> 0)
            
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02\xF2[\x00-\xFF]{2}\x14\x00\x00\x00\x01([\x00-\xFF])\x00\x00([\x00-\xFF]{2})([\x00\x01])([\x00\x01])([\x00-\xFF]{2})([\x00\x01])([\x00\x01])([\x00-\xFF]{2})([\x00\x01])([\x00\x01])[\x00-\xFF]{3}\x00\x00\x00\x0D\x03'), self.__MatchChannelBroadcastImpedance, None)
            self.AddMatchString(re.compile(b'\x02\xE2[\x00-\xFF]{2}\x04\x00\x00\x00([\x00-\xFF])([\x00\x01])([\x00-\x04])\x00[\x00-\xFF]{2}\x1D\x03'), self.__MatchChannelLoadStatus, None)
            self.AddMatchString(re.compile(b'\x02\xE6[\x00-\xFF]{2}\\x28\x00\x00\x00\x01([\x00-\xFF])\x00\x00[\x00-\xFF]{3}([\x00-\xFF])([\x00-\xFF]{32})[\x00-\xFF]{2}\x19\x03'), self.__MatchGlobalAlarmStatus, None)
            self.AddMatchString(re.compile(b'\x02\xFE[\x00-\xFF]{2}\x34\x00\x00\x00\x01[\x02\x04\x08]\x00\x00([\x00-\xFF]{32})([\x01\x00]{16})[\x00-\xFF]{2}\x01\x03'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'\x02\xF1[\x00-\xFF]{2}\x04\x00\x00\x00\x01(\x02|\x01)\x00\x00[\x00-\xFF]{2}\x0E\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02[\x00-\xFF]{7}([\x02-\xFF]|\x00)[\x00-\xFF]+?\x03'), self.__MatchError, None)

    @property
    def ReplyPort(self):
        return self._ReplyPort

    @ReplyPort.setter
    def ReplyPort(self, value):
        if 1 <= int(value) <= 65535:
            if int(value) == 1234:
                self._ReplyPort = 0
            else:
                self._ReplyPort = int(value)
        else:
            self.Error(['Reply Port Out of Range'])

    def CalcChecksum(self, data):
        value = 0
        for ch in data:
            value = self.table[(ch ^ value) & 0xff] ^ (value >> 8)
        val = chr(value & 0xff) + chr(value >> 8)
        return val.encode(encoding='iso-8859-1')
    
    def UpdateChannelAlarmStatus(self, value, qualifier):

        TypeStates = ['Input Clip', 'Over Temperature', 'Rail Voltage Fault', 'Other Fault']
        
        type_val = qualifier['Type']
        channel_val = qualifier['Channel']
        if type_val in TypeStates and channel_val in self.ChannelStates: 
            self.UpdateGlobalAlarmStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelAlarmStatus')

    def UpdateChannelBroadcastImpedance(self, value, qualifier):

        channel_val = qualifier['Channel']

        if channel_val in self.ChannelStates:
            ChannelBroadcastImpedanceCmdString = b''.join([b'\x02\x0D\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), self.ChannelStates[channel_val], b'\x00\x00\xF2\x03'])
            self.__UpdateHelper('ChannelBroadcastImpedance', ChannelBroadcastImpedanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelBroadcastImpedance')

    def __MatchChannelBroadcastImpedance(self, match, tag):

        DetectedStateValues = {
            b'\x01': 'Detected',
            b'\x00': 'Not Detected'
            }

        ValidityStateValues = {
            b'\x01': 'Valid',
            b'\x00': 'Not Valid'
            }
        _channel = str(int.from_bytes(match.group(1), "little") + 1)
        try:
            inputPilotToneLevelValue = int.from_bytes(match.group(2), "little")
            self.WriteStatus('ChannelInputPilotToneLevel', inputPilotToneLevelValue, {'Channel': _channel})
        except (ValueError, IndexError, AttributeError):
            self.Error(['Channel Input Pilot Tone Level: Invalid/unexpected response'])
        try:
            frequencySpecificImpedanceValue = int.from_bytes(match.group(5), "little") / 10
            self.WriteStatus('ChannelFrequencySpecificImpedance', frequencySpecificImpedanceValue, {'Channel': _channel})
        except (ValueError, IndexError, AttributeError):
            self.Error(['Channel Frequency Specific Impedance: Invalid/unexpected response'])
        try:
            broadcastImpedanceValue = int.from_bytes(match.group(8), "little") / 10
            self.WriteStatus('ChannelBroadcastImpedance', broadcastImpedanceValue, {'Channel': _channel})
        except (ValueError, IndexError, AttributeError):
            self.Error(['Channel Broadcast Impedance: Invalid/unexpected response'])
        try:
            self.WriteStatus('ChannelValueDetected', DetectedStateValues[match.group(3)], {'Channel': _channel, 'Type': 'Input Pilot Tone Level'})
            self.WriteStatus('ChannelValueDetected', DetectedStateValues[match.group(6)], {'Channel': _channel, 'Type': 'Frequency Specific Impedance'})
            self.WriteStatus('ChannelValueDetected', DetectedStateValues[match.group(9)], {'Channel': _channel, 'Type': 'Broadcast Impedance'})
        except (ValueError, IndexError, AttributeError):
            self.Error(['Channel Value Detected: Invalid/unexpected response'])
        try:
            self.WriteStatus('ChannelValueValidity', ValidityStateValues[match.group(4)], {'Channel': _channel, 'Type': 'Input Pilot Tone Level'})
            self.WriteStatus('ChannelValueValidity', ValidityStateValues[match.group(7)], {'Channel': _channel, 'Type': 'Frequency Specific Impedance'})
            self.WriteStatus('ChannelValueValidity', ValidityStateValues[match.group(10)], {'Channel': _channel, 'Type': 'Broadcast Impedance'})
        except (ValueError, IndexError, AttributeError):
            self.Error(['Channel Value Validity: Invalid/unexpected response'])

    def UpdateChannelFrequencySpecificImpedance(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStates:
            self.UpdateChannelBroadcastImpedance(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelFrequencySpecificImpedance')

    def UpdateChannelInputPilotToneLevel(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStates:
            self.UpdateChannelBroadcastImpedance(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelInputPilotToneLevel')

    def UpdateChannelLoadStatus(self, value, qualifier):

        TypeStates = {
            'Nominal Impedance': b'\x00',
            'Load Monitor': b'\x01'
            }

        type_val = qualifier['Type']
        channel_val = qualifier['Channel']
        if type_val in TypeStates and channel_val in self.ChannelStates:
            crc16_val_buffer = b''.join([self.ChannelStates[channel_val], TypeStates[type_val], b'\x00\x00'])
            crc16_val = self.CalcChecksum(crc16_val_buffer)

            ChannelLoadStatusCmdString = b''.join([b'\x02\x1D\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), crc16_val_buffer, crc16_val, b'\xE2\x03'])
            self.__UpdateHelper('ChannelLoadStatus', ChannelLoadStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelLoadStatus')

    def __MatchChannelLoadStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Low Short Circuit',
            '2': 'Below Threshold',
            '3': 'Above Threshold',
            '4': 'Status Unavailable',
            }

        TypeStates = {
            '0': 'Nominal Impedance',
            '1': 'Load Monitor'
            }
        qualifier = {}
        qualifier['Type'] = TypeStates[str(int.from_bytes(match.group(2), "little"))]
        qualifier['Channel'] = str(int.from_bytes(match.group(1), "little") + 1)
        value = ValueStateValues[str(int.from_bytes(match.group(3), "little"))]
        self.WriteStatus('ChannelLoadStatus', value, qualifier)

    def UpdateChannelValueDetected(self, value, qualifier):

        TypeStates = ['Broadcast Impedance', 'Frequency Specific Impedance', 'Input Pilot Tone Level']

        type_val = qualifier['Type']
        channel_val = qualifier['Channel']
        if type_val in TypeStates and channel_val in self.ChannelStates:
            self.UpdateChannelBroadcastImpedance(value, {'Channel': channel_val})
        else:
            self.Discard('Invalid Command for UpdateChannelValueDetected')

    def UpdateChannelValueValidity(self, value, qualifier):

        TypeStates = ['Broadcast Impedance', 'Frequency Specific Impedance', 'Input Pilot Tone Level']

        type_val = qualifier['Type']
        channel_val = qualifier['Channel']
        if type_val in TypeStates and channel_val in self.ChannelStates:
            self.UpdateChannelBroadcastImpedance(value, {'Channel': channel_val})
        else:
            self.Discard('Invalid Command for UpdateChannelValueValidity')

    def UpdateGlobalAlarmStatus(self, value, qualifier):
            
        GlobalAlarmStatusCmdString = b''.join([b'\x02\x19\x00\x00\x00\x00', self._ReplyPort.to_bytes(2, 'little'), b'\x00\x00\xE6\x03'])
        self.__UpdateHelper('GlobalAlarmStatus', GlobalAlarmStatusCmdString, value, qualifier)

    def __MatchGlobalAlarmStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'Active', 
            '0' : 'Inactive'
        }
        gpio_values = bin(match.group(1)[0])[2:].zfill(8)
        for i in range(0, self.Channel):
            self.WriteStatus('GPIOAlarmStatus', ValueStateValues[gpio_values[7-i]], {'Channel' : str(i+1)})
        global_values = bin(match.group(2)[0])[2:].zfill(8)
        self.WriteStatus('GlobalAlarmStatus', ValueStateValues[global_values[1]], {'Type' : 'Fan Fault'})
        self.WriteStatus('GlobalAlarmStatus', ValueStateValues[global_values[3]], {'Type' : 'Digi Board Over Temperature'})
        self.WriteStatus('GlobalAlarmStatus', ValueStateValues[global_values[5]], {'Type' : 'DA Converter Configuration Fault'})
        self.WriteStatus('GlobalAlarmStatus', ValueStateValues[global_values[6]], {'Type' : 'AD Converter Configuration Fault'})
        channel_values = re.findall(b'([\x00-\xFF]{4})', match.group(3))
        for i in range(0, self.Channel):
            bin_val = bin(channel_values[i][-1])[2:].zfill(8)
            self.WriteStatus('ChannelAlarmStatus', ValueStateValues[bin_val[1]], {'Type' : 'Other Fault', 'Channel' : str(i+1)})
            self.WriteStatus('ChannelAlarmStatus', ValueStateValues[bin_val[3]], {'Type' : 'Rail Voltage Fault', 'Channel' : str(i+1)})
            self.WriteStatus('ChannelAlarmStatus', ValueStateValues[bin_val[4]], {'Type' : 'Over Temperature', 'Channel' : str(i+1)})
            self.WriteStatus('ChannelAlarmStatus', ValueStateValues[bin_val[7]], {'Type' : 'Input Clip', 'Channel' : str(i+1)})

    def UpdateGPIOAlarmStatus(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStates: 
            self.UpdateGlobalAlarmStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGPIOAlarmStatus')

    def SetInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -60,
            'Max' : 15
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in self.ChannelStates:
            if value < 0:
                temp_val = int(65536 + (value * 100)) # signed bytes
            else:
                temp_val = int(value * 100)
            crc16_val_buffer = b''.join([self.ChannelStates[channel_val], b'\x00', temp_val.to_bytes(2, 'little')])
            crc16_val = self.CalcChecksum(crc16_val_buffer)
            InputGainCmdString = b''.join([b'\x02\x05\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), crc16_val_buffer, crc16_val, b'\xFA\x03'])
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        channel_val = qualifier['Channel']

        if channel_val in self.ChannelStates:
            InputGainCmdString = b''.join([b'\x02\x01\x00\x00\x00\x00', self._ReplyPort.to_bytes(2, 'little'), b'\x00\x00\xFE\x03'])
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        temp_gain_values = match.group(1)
        gain_values = re.findall(b'([\x00-\xFF]{2})', temp_gain_values)
        
        for i in range(0, self.Channel):
            input_value = unpack('<h',gain_values[i+8])[0]/100
            self.WriteStatus('InputGain', input_value, {'Channel' : str(i+1)})

            output_value = unpack('<h',gain_values[i])[0]/100
            self.WriteStatus('OutputGain', output_value, {'Channel' : str(i+1)})
            
        temp_mute_values = match.group(2)
        mute_values = re.findall(b'(\x00|\x01)', temp_mute_values)
        for i in range(0, self.Channel):
            self.WriteStatus('InputMute', ValueStateValues[mute_values[i]], {'Channel' : str(i+1)})
            self.WriteStatus('OutputMute', ValueStateValues[mute_values[i+8]], {'Channel' : str(i+1)})

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01', 
            'Off' : b'\x00'
        }

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStates:
            crc16_val_buffer = b''.join([self.ChannelStates[channel_val], ValueStateValues[value], b'\x00', b'\x00'])
            crc16_val = self.CalcChecksum(crc16_val_buffer)
            InputMuteCmdString = b''.join([b'\x02\x02\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), crc16_val_buffer, crc16_val, b'\xFD\x03'])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStates:
            self.UpdateInputGain(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def SetOutputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -60,
            'Max' : 15
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in self.ChannelStates:
            if value < 0:
                temp_val = int(65536 + (value * 100)) # signed bytes
            else:
                temp_val = int(value * 100)
            crc16_val_buffer = b''.join([self.ChannelStates[channel_val], b'\x00', temp_val.to_bytes(2, 'little')])
            crc16_val = self.CalcChecksum(crc16_val_buffer)
            OutputGainCmdString = b''.join([b'\x02\x04\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), crc16_val_buffer, crc16_val, b'\xFB\x03'])
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStates:
            self.UpdateInputGain(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01', 
            'Off' : b'\x00'
        }

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStates:
            crc16_val_buffer = b''.join([self.ChannelStates[channel_val], ValueStateValues[value], b'\x00', b'\x00'])
            crc16_val = self.CalcChecksum(crc16_val_buffer)
            OutputMuteCmdString = b''.join([b'\x02\x03\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), crc16_val_buffer, crc16_val, b'\xFC\x03'])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStates:
            self.UpdateInputGain(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01', 
            'Off' : b'\x02'
        }

        crc16_val_buffer = b''.join([ValueStateValues[value], b'\x00\x00\x00'])
        crc16_val = self.CalcChecksum(crc16_val_buffer)
        PowerCmdString = b''.join([b'\x02\x0E\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), crc16_val_buffer, crc16_val, b'\xF1\x03'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

            
        PowerCmdString = b''.join([b'\x02\x0E\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), b'\x00\x00\x00\x00\x00\x00\xF1\x03'])
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x02' : 'On', 
            '\x01' : 'Off'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetDelete(self, value, qualifier):

        if 0 <= int(value) <= 200:
            crc16_val_buffer = b''.join([bytes([int(value)]), b'\x00\x00\x00'])
            crc16_val = self.CalcChecksum(crc16_val_buffer)
            PresetDeleteCmdString = b''.join([b'\x02\x09\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), crc16_val_buffer, crc16_val, b'\xF6\x03'])
            self.__SetHelper('PresetDelete', PresetDeleteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetDelete')

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 200:
            crc16_val_buffer = b''.join([bytes([int(value)]), b'\x00\x00\x00'])
            crc16_val = self.CalcChecksum(crc16_val_buffer)
            PresetRecallCmdString = b''.join([b'\x02\x07\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), crc16_val_buffer, crc16_val, b'\xF8\x03'])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 200:
            crc16_val_buffer = b''.join([bytes([int(value)]), b'\x00\x00\x00'])
            crc16_val = self.CalcChecksum(crc16_val_buffer)
            PresetSaveCmdString = b''.join([b'\x02\x0A\x00\x00\x04\x00', self._ReplyPort.to_bytes(2, 'little'), crc16_val_buffer, crc16_val, b'\xF5\x03'])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

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

        self.counter = 0

        self.Error(['Invalid Answer.'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
    
    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
    def psft_25_3633_duo(self):
        
        self.Channel = 2
        self.ChannelStates = {
            '1' : b'\x00', 
            '2' : b'\x01'
        }
        
    def psft_25_3633_quattro(self):
        
        self.Channel = 4
        self.ChannelStates = {
            '1' : b'\x00', 
            '2' : b'\x01', 
            '3' : b'\x02', 
            '4' : b'\x03'
        }

    def psft_25_3633_otto(self):
        
        self.Channel = 8
        self.ChannelStates = {
            '1' : b'\x00', 
            '2' : b'\x01', 
            '3' : b'\x02', 
            '4' : b'\x03', 
            '5' : b'\x04', 
            '6' : b'\x05', 
            '7' : b'\x06', 
            '8' : b'\x07'
        }

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