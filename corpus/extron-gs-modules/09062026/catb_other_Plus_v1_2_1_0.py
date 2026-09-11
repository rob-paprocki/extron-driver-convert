# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from collections import defaultdict
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
            'DeviceFeatureSet': { 'Status': {}},
            'DeviceType': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'InputGain': {'Parameters': ['Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputAudioActivity': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'RFPower': { 'Status': {}},
            'SerialNumber': { 'Status': {}},
            'SystemName': { 'Status': {}},
            'TransmitterBatteryLevel': {'Parameters': ['Transmitter'], 'Status': {}},
            'TransmitterFirmwareVersion': {'Parameters': ['Transmitter'], 'Status': {}},
            'TransmitterLinkState': {'Parameters': ['Transmitter'], 'Status': {}},
            'TransmitterName': {'Parameters': ['Transmitter'], 'Status': {}},
            'TransmitterPairing': {'Parameters': ['Transmitter'], 'Status': {}},
            'TransmitterRSSI': {'Parameters': ['Transmitter'], 'Status': {}},
            'TransmitterSerialNumber': {'Parameters': ['Transmitter'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{"rx":{"device":{"featureset":([123])}},"error":0}'), self.__MatchDeviceFeatureSet, None)

            self.AddMatchString(re.compile(b'{"rx":{"device":{"device_type":"(dual|quad)"}},"error":0}'), self.__MatchDeviceType, None)

            self.AddMatchString(re.compile(b'{"rx":{"device":{"firmware_info":"(.+?)"}},"error":0}'), self.__MatchFirmwareVersion, None)

            self.AddMatchString(re.compile(b'{"rx":{"settings":{"input":{"(mic[1-4])":{"gain":([0-8])}}}},"error":0}'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'{"rx":{"settings":{"input":{"other":{"(aux)":{"gain":([0-8])}}}}},"error":0}'), self.__MatchInputGain, 'Aux')
            self.AddMatchString(re.compile(b'{"rx":{"settings":{"input":{"dante":{"(ch[1-4])":{"gain":([0-8])}}}}},"error":0}'), self.__MatchInputGain, 'Dante')

            self.AddMatchString(re.compile(b'{"rx":{"audio":{"input":{"(mic[1-4]|usb|aux)":{"mute":([01])}}}},"error":0}'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'{"rx":{"audio":{"input":{"dante":{"(ch[1-4])":{"mute":([01])}}}}},"error":0}'), self.__MatchInputMute, 'Dante')
            # When a transmitter is not connected, error is returned and used for status
            self.AddMatchString(re.compile(b'{"rx":{"audio":{"input":{"(mic[1-4])":{"mute":null}}}},"error":415}'), self.__MatchInputMute, 'Not Found')

            self.AddMatchString(re.compile(b'{"rx":{"audio":{"output":{"(mixout|direct|dante)":{"(rca|3pin|usb|ch[1-4])":{"activity":(-?\d+.\d+)}}}}},"error":0}'), self.__MatchOutputAudioActivity, None)

            self.AddMatchString(re.compile(b'{"rx":{"audio":{"output":{"(mixout|dante|direct)":{"(rca|3pin|usb|ch[1-4])":{"mute":([01])}}}}},"error":0}'), self.__MatchOutputMute, None)

            self.AddMatchString(re.compile(b'{"rx":{"device":{"rf_power":([0-5])}},"error":0}'), self.__MatchRFPower, None)

            self.AddMatchString(re.compile(b'{"rx":{"device":{"serial":"(.*?)"}},"error":0}'), self.__MatchSerialNumber, None)

            self.AddMatchString(re.compile(b'{"rx":{"device":{"name":"?(.*?)"?}},"error":0}'), self.__MatchSystemName, None)

            self.AddMatchString(re.compile(b'{"tx([1-4])":{"device":{"battery":(\d+)}},"error":0}'), self.__MatchTransmitterBatteryLevel, None)
            # When a transmitter is not connected, error is returned and used for status
            self.AddMatchString(re.compile(b'{"tx([1-4])":{"device":{"battery":null}},"error":415}'), self.__MatchTransmitterBatteryLevel, 'Not Found')

            self.AddMatchString(re.compile(b'{"rx":{"device":{"mic([1-4])_link_state":([0-3])}},"error":0}'), self.__MatchTransmitterLinkState, None)


            self.AddMatchString(re.compile(b'{"tx([1-4])":{"device":{"firmware_info":"(.*?)"}},"error":0}'), self.__MatchTransmitterFirmwareVersion, None)
            # When a transmitter is not connected, error is returned and used for status
            self.AddMatchString(re.compile(b'{"tx([1-4])":{"device":{"firmware_info":null}},"error":415}'), self.__MatchTransmitterFirmwareVersion, 'Not Found')

            self.AddMatchString(re.compile(b'{"tx([1-4])":{"device":{"rssi":(-?\d+)}},"error":0}'), self.__MatchTransmitterRSSI, None)
            # When a transmitter is not connected, error is returned and used for status
            self.AddMatchString(re.compile(b'{"tx([1-4])":{"device":{"rssi":null}},"error":415}'), self.__MatchTransmitterRSSI, 'Not Found')

            self.AddMatchString(re.compile(b'{"tx([1-4])":{"device":{"serial":"(.+?)"}},"error":0}'), self.__MatchTransmitterSerialNumber, None)
            # When a transmitter is not connected, error is returned and used for status
            self.AddMatchString(re.compile(b'{"tx([1-4])":{"device":{"serial":null}},"error":415}'), self.__MatchTransmitterSerialNumber, 'Not Found')

            self.AddMatchString(re.compile(b'{"tx([1-4])":{"device":{"name":"?(.*?)"?}},"error":0}'), self.__MatchTransmitterName, None)
            # When a transmitter is not connected, error is returned and used for status
            self.AddMatchString(re.compile(b'{"tx([1-4])":{"device":{"name":null}},"error":415}'), self.__MatchTransmitterName, 'Not Found')

            self.AddMatchString(re.compile(b'{"[tr]x".*?,"error":(4\d+)}'), self.__MatchError, None)

    def UpdateDeviceFeatureSet(self, value, qualifier):

        DeviceFeatureSetCmdString = '{"rx":{"device":{"featureset":null}}}'
        self.__UpdateHelper('DeviceFeatureSet', DeviceFeatureSetCmdString, value, qualifier)

    def __MatchDeviceFeatureSet(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceFeatureSet', value, None)
        
    def UpdateDeviceType(self, value, qualifier):

        DeviceTypeCmdString = '{"rx":{"device":{"device_type":null}}}'
        self.__UpdateHelper('DeviceType', DeviceTypeCmdString, value, qualifier)

    def __MatchDeviceType(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('DeviceType', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '{"rx":{"device":{"firmware_info":null}}}'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetInputGain(self, value, qualifier):

        ChannelStates = {
            'Mic 1':    '{{"rx":{{"settings":{{"input":{{"mic1":{{"gain":{}}}}}}}}}}}',
            'Mic 2':    '{{"rx":{{"settings":{{"input":{{"mic2":{{"gain":{}}}}}}}}}}}',
            'Mic 3':    '{{"rx":{{"settings":{{"input":{{"mic3":{{"gain":{}}}}}}}}}}}',
            'Mic 4':    '{{"rx":{{"settings":{{"input":{{"mic4":{{"gain":{}}}}}}}}}}}',
            'Aux':      '{{"rx":{{"settings":{{"input":{{"other":{{"aux":{{"gain":{}}}}}}}}}}}}}',
            'Dante 1':  '{{"rx":{{"settings":{{"input":{{"dante":{{"ch1":{{"gain":{}}}}}}}}}}}}}',
            'Dante 2':  '{{"rx":{{"settings":{{"input":{{"dante":{{"ch2":{{"gain":{}}}}}}}}}}}}}',
            'Dante 3':  '{{"rx":{{"settings":{{"input":{{"dante":{{"ch3":{{"gain":{}}}}}}}}}}}}}',
            'Dante 4':  '{{"rx":{{"settings":{{"input":{{"dante":{{"ch4":{{"gain":{}}}}}}}}}}}}}'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates and -20 <= value <= 20:
            InputGainCmdString = ChannelStates[channel].format(int(value // 5) + 4)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        ChannelStates = {
            'Mic 1':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"settings":{"input":{"mic1":{"gain":null}}}}}]}',
            'Mic 2':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"settings":{"input":{"mic2":{"gain":null}}}}}]}',
            'Mic 3':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"settings":{"input":{"mic3":{"gain":null}}}}}]}',
            'Mic 4':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"settings":{"input":{"mic4":{"gain":null}}}}}]}',
            'Aux':      '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"settings":{"input":{"other":{"aux":{"gain":null}}}}}}]}',
            'Dante 1':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"settings":{"input":{"dante":{"ch1":{"gain":null}}}}}}]}',
            'Dante 2':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"settings":{"input":{"dante":{"ch2":{"gain":null}}}}}}]}',
            'Dante 3':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"settings":{"input":{"dante":{"ch3":{"gain":null}}}}}}]}',
            'Dante 4':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"settings":{"input":{"dante":{"ch4":{"gain":null}}}}}}]}'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates:
            InputGainCmdString = ChannelStates[channel]
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        ChannelStates = {
            'mic1': 'Mic 1',
            'mic2': 'Mic 2',
            'mic3': 'Mic 3',
            'mic4': 'Mic 4',
            'aux':  'Aux',
            'ch1':  'Dante 1',
            'ch2':  'Dante 2',
            'ch3':  'Dante 3',
            'ch4':  'Dante 4'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        value = (int(match.group(2).decode()) - 4) * 5
        self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        ChannelStates = {
            'Mic 1':    '{{"rx":{{"audio":{{"input":{{"mic1":{{"mute":{}}}}}}}}}}}',
            'Mic 2':    '{{"rx":{{"audio":{{"input":{{"mic2":{{"mute":{}}}}}}}}}}}',
            'Mic 3':    '{{"rx":{{"audio":{{"input":{{"mic3":{{"mute":{}}}}}}}}}}}',
            'Mic 4':    '{{"rx":{{"audio":{{"input":{{"mic4":{{"mute":{}}}}}}}}}}}',
            'USB':      '{{"rx":{{"audio":{{"input":{{"usb":{{"mute":{}}}}}}}}}}}',
            'Aux':      '{{"rx":{{"audio":{{"input":{{"aux":{{"mute":{}}}}}}}}}}}',
            'Dante 1':  '{{"rx":{{"audio":{{"input":{{"dante":{{"ch1":{{"mute":{}}}}}}}}}}}}}',
            'Dante 2':  '{{"rx":{{"audio":{{"input":{{"dante":{{"ch2":{{"mute":{}}}}}}}}}}}}}',
            'Dante 3':  '{{"rx":{{"audio":{{"input":{{"dante":{{"ch3":{{"mute":{}}}}}}}}}}}}}',
            'Dante 4':  '{{"rx":{{"audio":{{"input":{{"dante":{{"ch4":{{"mute":{}}}}}}}}}}}}}'
        }
        channel = qualifier['Channel']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if channel in ChannelStates and value in ValueStateValues:
            InputMuteCmdString = ChannelStates[channel].format(ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        if value is None and qualifier['Channel'] in ['Mic 1', 'Mic 2', 'Mic 3', 'Mic 4']:
            self.UpdateTransmitterLinkState(None, {'Transmitter': qualifier['Channel'][-1]})
            return
        else:
            value = None

        ChannelStates = {
            'Mic 1':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"input":{"mic1":{"mute":null}}}}}]}',
            'Mic 2':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"input":{"mic2":{"mute":null}}}}}]}',
            'Mic 3':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"input":{"mic3":{"mute":null}}}}}]}',
            'Mic 4':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"input":{"mic4":{"mute":null}}}}}]}',
            'USB':      '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"input":{"usb":{"mute":null}}}}}]}',
            'Aux':      '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"input":{"aux":{"mute":null}}}}}]}',
            'Dante 1':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"input":{"dante":{"ch1":{"mute":null}}}}}}]}',
            'Dante 2':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"input":{"dante":{"ch2":{"mute":null}}}}}}]}',
            'Dante 3':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"input":{"dante":{"ch3":{"mute":null}}}}}}]}',
            'Dante 4':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"input":{"dante":{"ch4":{"mute":null}}}}}}]}'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates:

            InputMuteCmdString = ChannelStates[channel]
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ChannelStates = {
            'mic1': 'Mic 1',
            'mic2': 'Mic 2',
            'mic3': 'Mic 3',
            'mic4': 'Mic 4',
            'usb':  'USB',
            'aux':  'Aux',
            'ch1':  'Dante 1',
            'ch2':  'Dante 2',
            'ch3':  'Dante 3',
            'ch4':  'Dante 4'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        if tag == 'Not Found':
            self.WriteStatus('InputMute', 'Not Found', qualifier)
        else:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('InputMute', value, qualifier)

    def UpdateOutputAudioActivity(self, value, qualifier):

        ChannelStates = {
            'RCA':      '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"mixout":{"rca":{"activity":null}}}}}}]}',
            '3 Pin':    '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"mixout":{"3pin":{"activity":null}}}}}}]}',
            'USB':      '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"mixout":{"usb":{"activity":null}}}}}}]}',
            'Mic 1':    '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"direct":{"ch1":{"activity":null}}}}}}]}',
            'Mic 2':    '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"direct":{"ch2":{"activity":null}}}}}}]}',
            'Mic 3':    '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"direct":{"ch3":{"activity":null}}}}}}]}',
            'Mic 4':    '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"direct":{"ch4":{"activity":null}}}}}}]}',
            'Dante 1':  '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"dante":{"ch1":{"activity":null}}}}}}]}',
            'Dante 2':  '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"dante":{"ch2":{"activity":null}}}}}}]}',
            'Dante 3':  '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"dante":{"ch3":{"activity":null}}}}}}]}',
            'Dante 4':  '{"subscribe":[{"#":{"enable":true,"period_ms":1000},"rx":{"audio":{"output":{"dante":{"ch4":{"activity":null}}}}}}]}'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates:
            OutputAudioActivityCmdString = ChannelStates[channel]
            self.__UpdateHelper('OutputAudioActivity', OutputAudioActivityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputAudioActivity')

    def __MatchOutputAudioActivity(self, match, tag):

        ChannelStates = {
            ('mixout', 'rca'):  'RCA',
            ('mixout', '3pin'): '3 Pin',
            ('mixout', 'usb'):  'USB',
            ('direct', 'ch1'):  'Mic 1',
            ('direct', 'ch2'):  'Mic 2',
            ('direct', 'ch3'):  'Mic 3',
            ('direct', 'ch4'):  'Mic 4',
            ('dante', 'ch1'):   'Dante 1',
            ('dante', 'ch2'):   'Dante 2',
            ('dante', 'ch3'):   'Dante 3',
            ('dante', 'ch4'):   'Dante 4'
        }

        qualifier = {
            'Channel': ChannelStates[(match.group(1).decode(), match.group(2).decode())]
        }
        
        value = float(match.group(3).decode())
        if -100 <= value:
            self.WriteStatus('OutputAudioActivity', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ChannelStates = {
            'RCA':      '{{"rx":{{"audio":{{"output":{{"mixout":{{"rca":{{"mute":{}}}}}}}}}}}}}',
            '3 Pin':    '{{"rx":{{"audio":{{"output":{{"mixout":{{"3pin":{{"mute":{}}}}}}}}}}}}}',
            'USB':      '{{"rx":{{"audio":{{"output":{{"mixout":{{"usb":{{"mute":{}}}}}}}}}}}}}',
            'Mic 1':    '{{"rx":{{"audio":{{"output":{{"direct":{{"ch1":{{"mute":{}}}}}}}}}}}}}',
            'Mic 2':    '{{"rx":{{"audio":{{"output":{{"direct":{{"ch2":{{"mute":{}}}}}}}}}}}}}',
            'Mic 3':    '{{"rx":{{"audio":{{"output":{{"direct":{{"ch3":{{"mute":{}}}}}}}}}}}}}',
            'Mic 4':    '{{"rx":{{"audio":{{"output":{{"direct":{{"ch4":{{"mute":{}}}}}}}}}}}}}',
            'Dante 1':  '{{"rx":{{"audio":{{"output":{{"dante":{{"ch1":{{"mute":{}}}}}}}}}}}}}',
            'Dante 2':  '{{"rx":{{"audio":{{"output":{{"dante":{{"ch2":{{"mute":{}}}}}}}}}}}}}',
            'Dante 3':  '{{"rx":{{"audio":{{"output":{{"dante":{{"ch3":{{"mute":{}}}}}}}}}}}}}',
            'Dante 4':  '{{"rx":{{"audio":{{"output":{{"dante":{{"ch4":{{"mute":{}}}}}}}}}}}}}'
        }
        channel = qualifier['Channel']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if channel in ChannelStates and value in ValueStateValues:
            OutputMuteCmdString = ChannelStates[channel].format(ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):
        ChannelStates = {
            'RCA':      '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"mixout":{"rca":{"mute":null}}}}}}]}',
            '3 Pin':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"mixout":{"3pin":{"mute":null}}}}}}]}',
            'USB':      '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"mixout":{"usb":{"mute":null}}}}}}]}',
            'Mic 1':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"direct":{"ch1":{"mute":null}}}}}}]}',
            'Mic 2':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"direct":{"ch2":{"mute":null}}}}}}]}',
            'Mic 3':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"direct":{"ch3":{"mute":null}}}}}}]}',
            'Mic 4':    '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"direct":{"ch4":{"mute":null}}}}}}]}',
            'Dante 1':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"dante":{"ch1":{"mute":null}}}}}}]}',
            'Dante 2':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"dante":{"ch2":{"mute":null}}}}}}]}',
            'Dante 3':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"dante":{"ch3":{"mute":null}}}}}}]}',
            'Dante 4':  '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"audio":{"output":{"dante":{"ch4":{"mute":null}}}}}}]}'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates:
            OutputMuteCmdString = ChannelStates[channel]
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ChannelStates = {
            ('mixout', 'rca'):  'RCA',
            ('mixout', '3pin'): '3 Pin',
            ('mixout', 'usb'):  'USB',
            ('direct', 'ch1'):  'Mic 1',
            ('direct', 'ch2'):  'Mic 2',
            ('direct', 'ch3'):  'Mic 3',
            ('direct', 'ch4'):  'Mic 4',
            ('dante', 'ch1'):   'Dante 1',
            ('dante', 'ch2'):   'Dante 2',
            ('dante', 'ch3'):   'Dante 3',
            ('dante', 'ch4'):   'Dante 4'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Channel': ChannelStates[(match.group(1).decode(), match.group(2).decode())]
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetRFPower(self, value, qualifier):

        if 8 <= value <= 18:
            RFPowerCmdString = '{{"rx":{{"device":{{"rf_power":{}}}}}}}'.format(int(value // 2) - 4)
            self.__SetHelper('RFPower', RFPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRFPower')

    def UpdateRFPower(self, value, qualifier):

        RFPowerCmdString = '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"device":{"rf_power":null}}}]}'
        self.__UpdateHelper('RFPower', RFPowerCmdString, value, qualifier)

    def __MatchRFPower(self, match, tag):

        value = (int(match.group(1).decode()) + 4) * 2
        self.WriteStatus('RFPower', value, None)

    def UpdateSerialNumber(self, value, qualifier):

        SerialNumberCmdString = '{"rx":{"device":{"serial":null}}}'
        self.__UpdateHelper('SerialNumber', SerialNumberCmdString, value, qualifier)

    def __MatchSerialNumber(self, match, tag):

        value = match.group(1).decode().strip()
        self.WriteStatus('SerialNumber', value, None)

    def UpdateSystemName(self, value, qualifier):

        SystemNameCmdString = '{"subscribe":[{"#":{"enable":true,"period_ms":0},"rx":{"device":{"name":null}}}]}'
        self.__UpdateHelper('SystemName', SystemNameCmdString, value, qualifier)

    def __MatchSystemName(self, match, tag):

        value = match.group(1).decode().strip()
        self.WriteStatus('SystemName', value, None)

    def UpdateTransmitterBatteryLevel(self, value, qualifier):

        transmitter = int(qualifier['Transmitter'])

        if 1 <= transmitter <= 4:

            TransmitterBatteryLevelCmdString = '{{"tx{}":{{"device":{{"battery":null}}}}}}'.format(transmitter)
            self.__UpdateHelper('TransmitterBatteryLevel', TransmitterBatteryLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterBatteryLevel')

    def __MatchTransmitterBatteryLevel(self, match, tag):

        qualifier = {
            'Transmitter': match.group(1).decode()
        }

        if tag == 'Not Found':
            value = 0
        else:
            value = int(match.group(2).decode())

        if 0 <= value <= 100:
            self.WriteStatus('TransmitterBatteryLevel', value, qualifier)

    def UpdateTransmitterFirmwareVersion(self, value, qualifier):

        if value is None:
            self.UpdateTransmitterLinkState( None, qualifier)
            return
        else:
            value = None

        transmitter = int(qualifier['Transmitter'])

        if 1 <= transmitter <= 4:

            TransmitterFirmwareVersionCmdString = '{{"tx{}":{{"device":{{"firmware_info":null}}}}}}'.format(transmitter)
            self.__UpdateHelper('TransmitterFirmwareVersion', TransmitterFirmwareVersionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterFirmwareVersion')

    def __MatchTransmitterFirmwareVersion(self, match, tag):

        qualifier = {
            'Transmitter': match.group(1).decode()
        }

        if tag == 'Not Found':
            value = 'Not Found'
        else:
            value = match.group(2).decode().strip()

        self.WriteStatus('TransmitterFirmwareVersion', value, qualifier)

    def UpdateTransmitterLinkState(self, value, qualifier):

        transmitter = int(qualifier['Transmitter'])

        if 1 <= transmitter <= 4:
            TransmitterLinkStateCmdString = '{{"subscribe":[{{"#":{{"enable":true,"period_ms":0}},"rx":{{"device":{{"mic{}_link_state":null}}}}}}]}}'.format(transmitter)
            self.__UpdateHelper('TransmitterLinkState', TransmitterLinkStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterLinkState')

    def __MatchTransmitterLinkState(self, match, tag):

        ValueStateValues = {
            '1': 'Connected',
            '0': 'Disconnected',
            '2': 'Pairing', # Sent when the receiver channel is trying to pair
            '3': 'Charging' # Sent when the mic/transmitter is docked to its charger
        }

        qualifier = {
            'Transmitter': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TransmitterLinkState', value, qualifier)
        self.UpdateInputMute( '', {'Channel': 'Mic {}'.format(qualifier['Transmitter'])})
        self.UpdateTransmitterFirmwareVersion( '', {'Transmitter': qualifier['Transmitter']})
        self.UpdateTransmitterName( '', {'Transmitter': qualifier['Transmitter']})
        self.UpdateTransmitterRSSI( '', {'Transmitter': qualifier['Transmitter']})
        self.UpdateTransmitterSerialNumber( '', {'Transmitter': qualifier['Transmitter']})

    def UpdateTransmitterName(self, value, qualifier):

        if value is None:
            self.UpdateTransmitterLinkState( None, qualifier)
            return
        else:
            value = None

        transmitter = int(qualifier['Transmitter'])

        if 1 <= transmitter <= 4:
            TransmitterNameCmdString = '{{"subscribe":[{{"#":{{"enable":true,"period_ms":0}},"tx{}":{{"device":{{"name":null}}}}}}]}}'.format(transmitter)
            self.__UpdateHelper('TransmitterName', TransmitterNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterName')

    def __MatchTransmitterName(self, match, tag):

        qualifier = {
            'Transmitter': match.group(1).decode()
        }

        if tag == 'Not Found':
            value = 'Not Found'
        else:
            value = match.group(2).decode().strip()

        self.WriteStatus('TransmitterName', value, qualifier)

    def SetTransmitterPairing(self, value, qualifier):

        transmitter = int(qualifier['Transmitter'])

        if 1 <= transmitter <= 4:
            TransmitterPairingCmdString = '{{"rx":{{"device":{{"pair":{}}}}}}}'.format(transmitter)
            self.__SetHelper('TransmitterPairing', TransmitterPairingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitterPairing')

    def UpdateTransmitterRSSI(self, value, qualifier):

        if value is None:
            self.UpdateTransmitterLinkState( None, qualifier)
            return
        else:
            value = None

        transmitter = int(qualifier['Transmitter'])

        if 1 <= transmitter <= 4:

            TransmitterRSSICmdString = '{{"subscribe":[{{"#":{{"enable":true,"period_ms":1000}},"tx{}":{{"device":{{"rssi":null}}}}}}]}}'.format(transmitter)
            self.__UpdateHelper('TransmitterRSSI', TransmitterRSSICmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterRSSI')

    def __MatchTransmitterRSSI(self, match, tag):

        qualifier = {
            'Transmitter': match.group(1).decode()
        }

        if tag == 'Not Found':
            value = 0
        else:
            value = int(match.group(2).decode())

        self.WriteStatus('TransmitterRSSI', value, qualifier)

    def UpdateTransmitterSerialNumber(self, value, qualifier):

        if value is None:
            self.UpdateTransmitterLinkState( None, qualifier)
            return
        else:
            value = None

        transmitter = int(qualifier['Transmitter'])

        if 1 <= transmitter <= 4:
            TransmitterSerialNumberCmdString = '{{"tx{}":{{"device":{{"serial":null}}}}}}'.format(transmitter)
            self.__UpdateHelper('TransmitterSerialNumber', TransmitterSerialNumberCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterSerialNumber')

    def __MatchTransmitterSerialNumber(self, match, tag):

        qualifier = {
            'Transmitter': match.group(1).decode()
        }

        if tag == 'Not Found':
            value = 'Not Found'
        else:
            value = match.group(2).decode().strip()

        self.WriteStatus('TransmitterSerialNumber', value, qualifier)

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

        error_map = {
            '405': 'VALUE_OUT_OF_BOUNDS',
            '410': 'INCORRECT_VALUE',
            '415': 'UNREACHABLE_ENDPOINT',
            '425': 'MALFORMED_COMMAND',
            '430': 'UNSUPPORTED_FEATURE'
        }

        self.Error(['An error occurred: {}.'.format(error_map.get(match.group(1).decode(), 'Unknown error'))])

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