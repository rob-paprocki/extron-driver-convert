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
            'BusAssign': {'Parameters': ['Channel', 'Bus Channel'], 'Status': {}},
            'BusLevel': {'Parameters': ['Channel', 'Bus Channel'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'InputChannelSource': {'Parameters': ['Channel'], 'Status': {}},
            'InputLevel': {'Parameters': ['Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'InputSettingBusLevel': {'Parameters': ['Channel', 'Bus Channel'], 'Status': {}},
            'InputSettingGainLine': {'Parameters': ['Channel'], 'Status': {}},
            'InputSettingGainMic': {'Parameters': ['Channel'], 'Status': {}},
            'InputSettingLevel': {'Parameters': ['Channel'], 'Status': {}},
            'InputSettingMaxVolume': {'Parameters': ['Channel'], 'Status': {}},
            'InputSettingMaxVolumeEnable': {'Parameters': ['Channel'], 'Status': {}},
            'InputSettingMinVolume': {'Parameters': ['Channel'], 'Status': {}},
            'InputSettingMinVolumeEnable': {'Parameters': ['Channel'], 'Status': {}},
            'InputSettingMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputChannelSettingMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputChannelSettingSource': {'Parameters': ['Channel'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Channel'], 'Status': {}},
            'OutputLevelSettingLevel': {'Parameters': ['Channel'], 'Status': {}},
            'OutputLevelSettingMaxVolume': {'Parameters': ['Channel'], 'Status': {}},
            'OutputLevelSettingMaxVolumeEnable': {'Parameters': ['Channel'], 'Status': {}},
            'OutputLevelSettingMinVolume': {'Parameters': ['Channel'], 'Status': {}},
            'OutputLevelSettingMinVolumeEnable': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'SubInputSettingGain': {'Parameters': ['Channel'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'GBUS 0000 [\dA-F]{2} NC (\d|1\d),([1-9]|1[0-2]),([0-2]),(\d+) \r'), self.__MatchBusLevel, None)
            self.AddMatchString(re.compile(b'g_firmware_version 0000 [\dA-F]{2} NC (.+?) \r'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'g_input_channel_settings 0000 [\dA-F]{2} NC ([^\r]+) \r'), self.__MatchInputChannelSource, None)
            self.AddMatchString(re.compile(b'GICL 0000 [\dA-F]{2} NC (\d|1\d),(\d+) \r'), self.__MatchInputLevel, None)
            self.AddMatchString(re.compile(b'GICM 0000 [\dA-F]{2} NC (\d|1[0-9]),([01]) \r'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'g_input_channel_bus_settings 0000 [\dA-F]{2} NC (\d|1\d),([^\r]+) \r'), self.__MatchInputSettingBusLevel, None)
            self.AddMatchString(re.compile(rb'g_input_gain_level 0000 [\dA-F]{2} NC ([\d,]+) \r'), self.__MatchInputSettingGainLine, None)
            self.AddMatchString(re.compile(b'g_output_mute 0000 [\dA-F]{2} NC (\d),(0|1) \r'), self.__MatchOutputChannelSettingMute, None)
            self.AddMatchString(re.compile(b'g_output_channel_settings 0000 [\dA-F]{2} NC (\d),([^\r]+) \r'), self.__MatchOutputChannelSettingSource, None)
            self.AddMatchString(re.compile(b'GOCL 0000 [\dA-F]{2} NC (\d),(\d+) \r'), self.__MatchOutputLevel, None)
            self.AddMatchString(re.compile(b'g_output_level 0000 [\dA-F]{2} NC ([^\r]+) \r'), self.__MatchOutputLevelSettingLevel, None)
            self.AddMatchString(re.compile(b'GOCM 0000 [\dA-F]{2} NC (\d),([01]) \r'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'g_subinput_channel_settings 0000 [\dA-F]{2} NC ([^\r]+) \r'), self.__MatchSubInputSettingGain, None)

            self.AddMatchString(re.compile(b'NAK (\d+) \r'), self.__MatchError, None)

    def SetBusAssign(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '10': '9',
            'ST 1': '10',
            'ST 2': '11'
        }
        channel = qualifier['Channel']

        bus = int(qualifier['Bus Channel'])

        ValueStateValues = {
            'Off': '0',
            'On (Smart Mix Pre Assign)': '1',
            'On (Smart Mix Post Assign)': '2'
        }

        if channel in ChannelStates and 1 <= bus <= 12 and value in ValueStateValues:
            BusAssignCmdString = 'SBUS S 0000 00 NC {},{},{}, \r'.format(ChannelStates[channel], bus, ValueStateValues[value])
            self.__SetHelper('BusAssign', BusAssignCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBusAssign')

    def UpdateBusAssign(self, value, qualifier):

        self.UpdateBusLevel(value, qualifier)

    def SetBusLevel(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '10': '9',
            'ST 1': '10',
            'ST 2': '11',
            'Sub 1': '12',
            'Sub 2': '13',
            'Sub 3': '14',
            'Sub 4': '15',
            'Sub 5': '16',
            'Sub 6': '17',
            'Sub 7': '18',
            'Sub 8': '19'
            }

        if qualifier['Channel'] in ChannelStates and 1 <= int(qualifier['Bus Channel']) <= 12 and 0 <= value <= 411:
            BusLevelCmdString = 'SBUS S 0000 00 NC {},{},,{} \r'.format(ChannelStates[qualifier['Channel']], qualifier['Bus Channel'],
                                        value)
            self.__SetHelper('BusLevel', BusLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBusLevel')

    def UpdateBusLevel(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '10': '9',
            'ST 1': '10',
            'ST 2': '11',
            'Sub 1': '12',
            'Sub 2': '13',
            'Sub 3': '14',
            'Sub 4': '15',
            'Sub 5': '16',
            'Sub 6': '17',
            'Sub 7': '18',
            'Sub 8': '19'
            }

        if qualifier['Channel'] in ChannelStates and 1 <= int(qualifier['Bus Channel']) <= 12:
            BusLevelCmdString = 'GBUS O 0000 00 NC {},{} \r'.format(ChannelStates[qualifier['Channel']], qualifier['Bus Channel'])
            self.__UpdateHelper('BusLevel', BusLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBusLevel')

    def __MatchBusLevel(self, match, tag):

        ChannelStates = {
            '0': '1',
            '1': '2',
            '2': '3',
            '3': '4',
            '4': '5',
            '5': '6',
            '6': '7',
            '7': '8',
            '8': '9',
            '9': '10',
            '10': 'ST 1',
            '11': 'ST 2'
            }

        channel = ChannelStates[match.group(1).decode()]
        bus = match.group(2).decode()
        ValueStateValues = {
            '0': 'Off',
            '1': 'On (Smart Mix Pre Assign)',
            '2': 'On (Smart Mix Post Assign)'
        }
        self.WriteStatus('BusAssign', ValueStateValues[match.group(3).decode()], {'Channel': channel, 'Bus Channel': bus})
        value = int(match.group(4).decode())
        if 0 <= value <= 411:
            self.WriteStatus('BusLevel', value, {'Channel': channel, 'Bus Channel': bus})

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'g_firmware_version O 0000 00 NC \r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):


        value = match.group(1).decode().strip()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetInputChannelSource(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            '9':    '8',
            '10':   '9',
            'ST 1': '10',
            'ST 2': '11'
            }

        ValueStateValues = {
            'Mic':           '0',
            'Line +4dBu':    '1',
            'Line 0dBV':     '2',
            'Line -10dBV':   '3',
            'Line -20dBV':   '4',
            'USB':           '5',
            'Virtual Mic 1': '6',
            'Virtual Mic 2': '7',
            'Dante':         '9'
            }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            InputChannelSourceCmdString = 's_input_channel_settings S 0000 00 NC {},{},,,,,,,,,,,,,,,,,,,,,,,,,, \r'.format(
                                                    ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('InputChannelSource', InputChannelSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputChannelSource')

    def UpdateInputChannelSource(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            '9':    '8',
            '10':   '9',
            'ST 1': '10',
            'ST 2': '11'
            }

        if qualifier['Channel'] in ChannelStates:
            InputChannelSourceCmdString = 'g_input_channel_settings O 0000 00 NC {} \r'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('InputChannelSource', InputChannelSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputChannelSource')

    def __MatchInputChannelSource(self, match, tag):

        ChannelStates = {
            '0':    '1',
            '1':    '2',
            '2':    '3',
            '3':    '4',
            '4':    '5',
            '5':    '6',
            '6':    '7',
            '7':    '8',
            '8':    '9',
            '9':    '10',
            '10':   'ST 1',
            '11':   'ST 2'
        }

        ValueStateValues = {
            '0': 'Mic',
            '1': 'Line +4dBu',
            '2': 'Line 0dBV',
            '3': 'Line -10dBV',
            '4': 'Line -20dBV',
            '5': 'USB',
            '6': 'Virtual Mic 1',
            '7': 'Virtual Mic 2',
            '9': 'Dante'
            }

        res = match.group(1).decode().split(',')
        
        qualifier = {}
        qualifier['Channel'] = ChannelStates[res[0]]
        value = ValueStateValues[res[1]]
        self.WriteStatus('InputChannelSource', value, qualifier)

    def SetInputLevel(self, value, qualifier):

        ChannelStates = {
            '1':     '0',
            '2':     '1',
            '3':     '2',
            '4':     '3',
            '5':     '4',
            '6':     '5',
            '7':     '6',
            '8':     '7',
            '9':     '8',
            '10':    '9',
            'ST 1':  '10',
            'ST 2':  '11',
            'Sub 1': '12',
            'Sub 2': '13',
            'Sub 3': '14',
            'Sub 4': '15',
            'Sub 5': '16',
            'Sub 6': '17',
            'Sub 7': '18',
            'Sub 8': '19'
            }

        if qualifier['Channel'] in ChannelStates and 0 <= value <= 511:
            InputLevelCmdString = 'SICL S 0000 00 NC {},{} \r'.format(ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        ChannelStates = {
            '1':     '0',
            '2':     '1',
            '3':     '2',
            '4':     '3',
            '5':     '4',
            '6':     '5',
            '7':     '6',
            '8':     '7',
            '9':     '8',
            '10':    '9',
            'ST 1':  '10',
            'ST 2':  '11',
            'Sub 1': '12',
            'Sub 2': '13',
            'Sub 3': '14',
            'Sub 4': '15',
            'Sub 5': '16',
            'Sub 6': '17',
            'Sub 7': '18',
            'Sub 8': '19'
            }

        if qualifier['Channel'] in ChannelStates:
            InputLevelCmdString = 'GICL O 0000 00 NC {} \r'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLevel')

    def __MatchInputLevel(self, match, tag):

        ChannelStates = {
            '0':  '1',
            '1':  '2',
            '2':  '3',
            '3':  '4',
            '4':  '5',
            '5':  '6',
            '6':  '7',
            '7':  '8',
            '8':  '9',
            '9':  '10',
            '10': 'ST 1',
            '11': 'ST 2',
            '12': 'Sub 1',
            '13': 'Sub 2',
            '14': 'Sub 3',
            '15': 'Sub 4',
            '16': 'Sub 5',
            '17': 'Sub 6',
            '18': 'Sub 7',
            '19': 'Sub 8'
            }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        if 0 <= value <= 511:
            self.WriteStatus('InputLevel', value, qualifier)

    def SetInputMute(self, value, qualifier):

        ChannelStates = {
            '1':     '0',
            '2':     '1',
            '3':     '2',
            '4':     '3',
            '5':     '4',
            '6':     '5',
            '7':     '6',
            '8':     '7',
            '9':     '8',
            '10':    '9',
            'ST 1':  '10',
            'ST 2':  '11',
            'Sub 1': '12',
            'Sub 2': '13',
            'Sub 3': '14',
            'Sub 4': '15',
            'Sub 5': '16',
            'Sub 6': '17',
            'Sub 7': '18',
            'Sub 8': '19'
        }
        channel = qualifier['Channel']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if channel in ChannelStates and value in ValueStateValues:
            InputMuteCmdString = 'SICM S 0000 00 NC {},{} \r'.format(ChannelStates[channel], ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        ChannelStates = {
            '1':     '0',
            '2':     '1',
            '3':     '2',
            '4':     '3',
            '5':     '4',
            '6':     '5',
            '7':     '6',
            '8':     '7',
            '9':     '8',
            '10':    '9',
            'ST 1':  '10',
            'ST 2':  '11',
            'Sub 1': '12',
            'Sub 2': '13',
            'Sub 3': '14',
            'Sub 4': '15',
            'Sub 5': '16',
            'Sub 6': '17',
            'Sub 7': '18',
            'Sub 8': '19'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates:
            InputMuteCmdString = 'GICM O 0000 00 NC {} \r'.format(ChannelStates[channel])
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ChannelStates = {
            '0':    '1',
            '1':    '2',
            '2':    '3',
            '3':    '4',
            '4':    '5',
            '5':    '6',
            '6':    '7',
            '7':    '8',
            '8':    '9',
            '9':    '10',
            '10':   'ST 1',
            '11':   'ST 2',
            '12':   'Sub 1',
            '13':   'Sub 2',
            '14':   'Sub 3',
            '15':   'Sub 4',
            '16':   'Sub 5',
            '17':   'Sub 6',
            '18':   'Sub 7',
            '19':   'Sub 8'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetInputSettingBusLevel(self, value, qualifier):

        ChannelStates = {
            '1':        '0',
            '2':        '1',
            '3':        '2',
            '4':        '3',
            '5':        '4',
            '6':        '5',
            '7':        '6',
            '8':        '7',
            '9':        '8',
            '10':       '9',
            'ST 1':     '10',
            'ST 2':     '11',
            'Sub 1':    '12',
            'Sub 2':    '13',
            'Sub 3':    '14',
            'Sub 4':    '15',
            'Sub 5':    '16',
            'Sub 6':    '17',
            'Sub 7':    '18',
            'Sub 8':    '19'
            }

        temp_string = ',,,,,,,,,,,,,,,,,,,,,,,'
        if qualifier['Channel'] in ChannelStates and 1 <= int(qualifier['Bus Channel']) <= 12 and 0 <= value <= 411:
            list_r = temp_string.split(',')
            list_r[2*int(qualifier['Bus Channel'])-1] = str(value)
            val_string = ','.join(list_r)
            InputSettingBusLevelCmdString = 's_input_channel_bus_settings S 0000 00 NC {},{} \r'.format(ChannelStates[qualifier['Channel']],
                                                val_string)
            self.__SetHelper('InputSettingBusLevel', InputSettingBusLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSettingBusLevel')

    def UpdateInputSettingBusLevel(self, value, qualifier):

        ChannelStates = {
            '1':        '0',
            '2':        '1',
            '3':        '2',
            '4':        '3',
            '5':        '4',
            '6':        '5',
            '7':        '6',
            '8':        '7',
            '9':        '8',
            '10':       '9',
            'ST 1':     '10',
            'ST 2':     '11',
            'Sub 1':    '12',
            'Sub 2':    '13',
            'Sub 3':    '14',
            'Sub 4':    '15',
            'Sub 5':    '16',
            'Sub 6':    '17',
            'Sub 7':    '18',
            'Sub 8':    '19'
            }

        if qualifier['Channel'] in ChannelStates and 1 <= int(qualifier['Bus Channel']) <= 12:
            InputSettingBusLevelCmdString = 'g_input_channel_bus_settings O 0000 00 NC {} \r'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('InputSettingBusLevel', InputSettingBusLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSettingBusLevel')

    def __MatchInputSettingBusLevel(self, match, tag):

        ChannelStates = {
            '0':    '1',
            '1':    '2',
            '2':    '3',
            '3':    '4',
            '4':    '5',
            '5':    '6',
            '6':    '7',
            '7':    '8',
            '8':    '9',
            '9':    '10',
            '10':   'ST 1',
            '11':   'ST 2',
            '12':   'Sub 1',
            '13':   'Sub 2',
            '14':   'Sub 3',
            '15':   'Sub 4',
            '16':   'Sub 5',
            '17':   'Sub 6',
            '18':   'Sub 7',
            '19':   'Sub 8'
            }

        res = match.group(2).decode()
        for i in range(1, 13):
            qualifier = {}
            qualifier['Channel'] = ChannelStates[match.group(1).decode()]
            qualifier['Bus Channel'] = str(i)
            value = res.split(',')[2*i-1]
            if 0 <= int(value) <= 411:
                self.WriteStatus('InputSettingBusLevel', int(value), qualifier)

    def SetInputSettingGainLine(self, value, qualifier):

        ChannelStates = {
            '1':        '0',
            '2':        '1',
            '3':        '2',
            '4':        '3',
            '5':        '4',
            '6':        '5',
            '7':        '6',
            '8':        '7',
            '9':        '8',
            '10':       '9',
            'ST 1':     '10',
            'ST 2':     '11',
            'Sub 1':    '12',
            'Sub 2':    '13',
            'Sub 3':    '14',
            'Sub 4':    '15',
            'Sub 5':    '16',
            'Sub 6':    '17',
            'Sub 7':    '18',
            'Sub 8':    '19'
            }

        if qualifier['Channel'] in ChannelStates and -60 <= value <= -20:
            InputSettingGainLineCmdString = 's_input_gain_level S 0000 00 NC {},,{},,,,,,,, \r'.format(
                                                    ChannelStates[qualifier['Channel']], value + 60)
            self.__SetHelper('InputSettingGainLine', InputSettingGainLineCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSettingGainLine')

    def UpdateInputSettingGainLine(self, value, qualifier):

        ChannelStates = {
            '1':        '0',
            '2':        '1',
            '3':        '2',
            '4':        '3',
            '5':        '4',
            '6':        '5',
            '7':        '6',
            '8':        '7',
            '9':        '8',
            '10':       '9',
            'ST 1':     '10',
            'ST 2':     '11',
            'Sub 1':    '12',
            'Sub 2':    '13',
            'Sub 3':    '14',
            'Sub 4':    '15',
            'Sub 5':    '16',
            'Sub 6':    '17',
            'Sub 7':    '18',
            'Sub 8':    '19'
            }

        if qualifier['Channel'] in ChannelStates:
            InputSettingGainLineCmdString = 'g_input_gain_level O 0000 00 NC {} \r'.format(
                                                    ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('InputSettingGainLine', InputSettingGainLineCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSettingGainLine')

    def __MatchInputSettingGainLine(self, match, tag):

        ChannelStates = {
            '0':  '1',
            '1':  '2',
            '2':  '3',
            '3':  '4',
            '4':  '5',
            '5':  '6',
            '6':  '7',
            '7':  '8',
            '8':  '9',
            '9':  '10',
            '10': 'ST 1',
            '11': 'ST 2',
            '12': 'Sub 1',
            '13': 'Sub 2',
            '14': 'Sub 3',
            '15': 'Sub 4',
            '16': 'Sub 5',
            '17': 'Sub 6',
            '18': 'Sub 7',
            '19': 'Sub 8'
            }
            
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        res = match.group(1).decode().split(',')
        
        if res[0] in ChannelStates:
            channel_val = ChannelStates[res[0]]
            if 0 <= int(res[1]) <= 40:
                self.WriteStatus('InputSettingGainMic', int(res[1]) + 20, {'Channel': channel_val})
                
            if 0 <= int(res[2]) <= 40:
                self.WriteStatus('InputSettingGainLine', int(res[2]) - 60, {'Channel': channel_val})
                
            if 0 <= int(res[3]) <= 511:
                self.WriteStatus('InputSettingLevel', int(res[3]), {'Channel': channel_val})
                
            if res[4] in ValueStateValues:
                self.WriteStatus('InputSettingMaxVolumeEnable', ValueStateValues[res[4]], {'Channel': channel_val})
                
            if 0 <= int(res[5]) <= 511:
                self.WriteStatus('InputSettingMaxVolume', int(res[5]), {'Channel': channel_val})
                
            if res[6] in ValueStateValues:
                self.WriteStatus('InputSettingMute', ValueStateValues[res[6]], {'Channel': channel_val})
                
            if res[8] in ValueStateValues:
                self.WriteStatus('InputSettingMinVolumeEnable', ValueStateValues[res[8]], {'Channel': channel_val})
                
            if 0 <= int(res[9]) <= 511:
                self.WriteStatus('InputSettingMinVolume', int(res[9]), {'Channel': channel_val})
            
    def SetInputSettingGainMic(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            '9':    '8',
            '10':   '9',
            'ST 1': '10',
            'ST 2': '11'
            }

        if qualifier['Channel'] in ChannelStates and 20 <= value <= 60:
            InputSettingGainMicCmdString = 's_input_gain_level S 0000 00 NC {},{},,,,,, \r'.format(
                                                ChannelStates[qualifier['Channel']], value - 20)
            self.__SetHelper('InputSettingGainMic', InputSettingGainMicCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSettingGainMic')

    def UpdateInputSettingGainMic(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateInputSettingGainLine(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSettingGainMic')

    def SetInputSettingLevel(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            '9':    '8',
            '10':   '9',
            'ST 1': '10',
            'ST 2': '11'
            }

        if qualifier['Channel'] in ChannelStates and 0 <= value <= 511:
            InputSettingLevelCmdString = 's_input_gain_level S 0000 00 NC {},,,{},,,,,, \r'.format(
                                                    ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('InputSettingLevel', InputSettingLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSettingLevel')

    def UpdateInputSettingLevel(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateInputSettingGainLine(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSettingLevel')

    def SetInputSettingMaxVolume(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            '9':    '8',
            '10':   '9',
            'ST 1': '10',
            'ST 2': '11'
            }

        if qualifier['Channel'] in ChannelStates and 0 <= value <= 511:
            InputSettingMaxVolumeCmdString = 's_input_gain_level S 0000 00 NC {},,,,,{},,,, \r'.format(
                                                    ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('InputSettingMaxVolume', InputSettingMaxVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSettingMaxVolume')

    def UpdateInputSettingMaxVolume(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateInputSettingGainLine(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSettingMaxVolume')

    def SetInputSettingMaxVolumeEnable(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            '9':    '8',
            '10':   '9',
            'ST 1': '10',
            'ST 2': '11'
            }

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            InputSettingMaxVolumeEnableCmdString = 's_input_gain_level S 0000 00 NC {},,,,{},,,,, \r'.format(
                                                        ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('InputSettingMaxVolumeEnable', InputSettingMaxVolumeEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSettingMaxVolumeEnable')

    def UpdateInputSettingMaxVolumeEnable(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateInputSettingGainLine(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSettingMaxVolumeEnable')

    def SetInputSettingMinVolume(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            '9':    '8',
            '10':   '9',
            'ST 1': '10',
            'ST 2': '11'
            }

        if qualifier['Channel'] in ChannelStates and 0 <= value <= 511:
            InputSettingMinVolumeCmdString = 's_input_gain_level S 0000 00 NC {},,,,,,,,,{} \r'.format(
                                                    ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('InputSettingMinVolume', InputSettingMinVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSettingMinVolume')

    def UpdateInputSettingMinVolume(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateInputSettingGainLine(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSettingMinVolume')

    def SetInputSettingMinVolumeEnable(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            '9':    '8',
            '10':   '9',
            'ST 1': '10',
            'ST 2': '11'
            }

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            InputSettingMinVolumeEnableCmdString = 's_input_gain_level S 0000 00 NC {},,,,,,,,{}, \r'.format(
                                                ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('InputSettingMinVolumeEnable', InputSettingMinVolumeEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSettingMinVolumeEnable')

    def UpdateInputSettingMinVolumeEnable(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateInputSettingGainLine(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSettingMinVolumeEnable')

    def SetInputSettingMute(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            '9':    '8',
            '10':   '9',
            'ST 1': '10',
            'ST 2': '11'
            }

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            InputSettingMuteCmdString = 's_input_gain_level S 0000 00 NC {},,,,,,{},,, \r'.format(
                                                ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('InputSettingMute', InputSettingMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSettingMute')

    def UpdateInputSettingMute(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateInputSettingGainLine(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSettingMute')

    def SetOutputChannelSettingMute(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            'ST 1': '8',
            'ST 2': '9'
            }

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            OutputChannelSettingMuteCmdString = 's_output_mute S 0000 00 NC {},{} \r'.format(
                                                        ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('OutputChannelSettingMute', OutputChannelSettingMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputChannelSettingMute')

    def UpdateOutputChannelSettingMute(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            'ST 1': '8',
            'ST 2': '9'
            }

        if qualifier['Channel'] in ChannelStates:
            OutputChannelSettingMuteCmdString = 'g_output_mute O 0000 00 NC {} \r'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('OutputChannelSettingMute', OutputChannelSettingMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputChannelSettingMute')

    def __MatchOutputChannelSettingMute(self, match, tag):

        ChannelStates = {
            '0': '1',
            '1': '2',
            '2': '3',
            '3': '4',
            '4': '5',
            '5': '6',
            '6': '7',
            '7': '8',
            '8': 'ST 1',
            '9': 'ST 2'
            }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputChannelSettingMute', value, qualifier)

    def SetOutputChannelSettingSource(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7'
            }

        ValueStateValues = {
            'Off':        '0',
            'Bus 1':      '1',
            'Bus 2':      '2',
            'Bus 3':      '3',
            'Bus 4':      '4',
            'Bus 5':      '5',
            'Bus 6':      '6',
            'Bus 7':      '7',
            'Bus 8':      '8',
            'Bus 9':      '9',
            'Bus 10':     '10',
            'Bus 11':     '11',
            'Bus 12':     '12',
            'Direct Out': '13'
            }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            OutputChannelSettingSourceCmdString = 's_output_channel_settings S 0000 00 NC {},,,,,{}, \r'.format(
                                                        ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('OutputChannelSettingSource', OutputChannelSettingSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputChannelSettingSource')

    def UpdateOutputChannelSettingSource(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7'
            }

        if qualifier['Channel'] in ChannelStates:
            OutputChannelSettingSourceCmdString = 'g_output_channel_settings O 0000 00 NC {} \r'.format(
                                                        ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('OutputChannelSettingSource', OutputChannelSettingSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputChannelSettingSource')

    def __MatchOutputChannelSettingSource(self, match, tag):

        ChannelStates = {
            '0': '1',
            '1': '2',
            '2': '3',
            '3': '4',
            '4': '5',
            '5': '6',
            '6': '7',
            '7': '8'
            }

        ValueStateValues = {
            '0':  'Off',
            '1':  'Bus 1',
            '2':  'Bus 2',
            '3':  'Bus 3',
            '4':  'Bus 4',
            '5':  'Bus 5',
            '6':  'Bus 6',
            '7':  'Bus 7',
            '8':  'Bus 8',
            '9':  'Bus 9',
            '10': 'Bus 10',
            '11': 'Bus 11',
            '12': 'Bus 12',
            '13': 'Direct Out'
            }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode().split(',')[4]]
        self.WriteStatus('OutputChannelSettingSource', value, qualifier)

    def SetOutputLevel(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            'ST 1': '8',
            'ST 2': '9'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates and 0 <= value <= 511:
            OutputLevelCmdString = 'SOCL S 0000 00 NC {},{} \r'.format(ChannelStates[channel], value)
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            'ST 1': '8',
            'ST 2': '9'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates:
            OutputLevelCmdString = 'GOCL O 0000 00 NC {} \r'.format(ChannelStates[channel])
            self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):

        ChannelStates = {
            '0':    '1',
            '1':    '2',
            '2':    '3',
            '3':    '4',
            '4':    '5',
            '5':    '6',
            '6':    '7',
            '7':    '8',
            '8':    'ST 1',
            '9':    'ST 2'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        value = int(match.group(2).decode())
        if 0 <= value <= 511:
            self.WriteStatus('OutputLevel', value, qualifier)

    def SetOutputLevelSettingLevel(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            'ST 1': '8',
            'ST 2': '9'
            }

        if qualifier['Channel'] in ChannelStates and 0 <= value <= 511:
            OutputLevelSettingLevelCmdString = 's_output_level S 0000 00 NC {},{},,,, \r'.format(
                                                        ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('OutputLevelSettingLevel', OutputLevelSettingLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevelSettingLevel')

    def UpdateOutputLevelSettingLevel(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            'ST 1': '8',
            'ST 2': '9'
            }
            
        if qualifier['Channel'] in ChannelStates:
            OutputLevelSettingLevelCmdString = 'g_output_level O 0000 00 NC {} \r'.format(
                                                        ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('OutputLevelSettingLevel', OutputLevelSettingLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevelSettingLevel')

    def __MatchOutputLevelSettingLevel(self, match, tag):

        ChannelStates = {
            '0': '1',
            '1': '2',
            '2': '3',
            '3': '4',
            '4': '5',
            '5': '6',
            '6': '7',
            '7': '8',
            '8': 'ST 1',
            '9': 'ST 2'
            }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        res = match.group(1).decode().split(',')
        
        if res[0] in ChannelStates:
            channel_val = ChannelStates[res[0]]
            if 0 <= int(res[1]) <= 511:
                self.WriteStatus('OutputLevelSettingLevel', int(res[1]), {'Channel': channel_val})
                
            if res[2] in ValueStateValues:
                self.WriteStatus('OutputLevelSettingMaxVolumeEnable', ValueStateValues[res[2]], {'Channel': channel_val})
            
            if 0 <= int(res[3]) <= 511:
                self.WriteStatus('OutputLevelSettingMaxVolume', int(res[3]), {'Channel': channel_val})
            
            if res[4] in ValueStateValues:
                self.WriteStatus('OutputLevelSettingMinVolumeEnable', ValueStateValues[res[4]], {'Channel': channel_val})
            
            if 0 <= int(res[5]) <= 511:
                self.WriteStatus('OutputLevelSettingMinVolume', int(res[5]), {'Channel': channel_val})
        
    def SetOutputLevelSettingMaxVolume(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            'ST 1': '8',
            'ST 2': '9'
            }

        if qualifier['Channel'] in ChannelStates and 0 <= value <= 511:
            OutputLevelSettingMaxVolumeCmdString = 's_output_level S 0000 00 NC {},,,{},, \r'.format(
                                                        ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('OutputLevelSettingMaxVolume', OutputLevelSettingMaxVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevelSettingMaxVolume')

    def UpdateOutputLevelSettingMaxVolume(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateOutputLevelSettingLevel(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevelSettingMaxVolume')

    def SetOutputLevelSettingMaxVolumeEnable(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            'ST 1': '8',
            'ST 2': '9'
            }

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            OutputLevelSettingMaxVolumeEnableCmdString = 's_output_level S 0000 00 NC {},,{},,, \r'.format(
                                                        ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('OutputLevelSettingMaxVolumeEnable', OutputLevelSettingMaxVolumeEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevelSettingMaxVolumeEnable')

    def UpdateOutputLevelSettingMaxVolumeEnable(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateOutputLevelSettingLevel(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevelSettingMaxVolumeEnable')

    def SetOutputLevelSettingMinVolume(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            'ST 1': '8',
            'ST 2': '9'
            }

        if qualifier['Channel'] in ChannelStates and 0 <= value <= 511:
            OutputLevelSettingMinVolumeCmdString = 's_output_level S 0000 00 NC {},,,,,{} \r'.format(
                                                        ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('OutputLevelSettingMinVolume', OutputLevelSettingMinVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevelSettingMinVolume')

    def UpdateOutputLevelSettingMinVolume(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateOutputLevelSettingLevel(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevelSettingMinVolume')

    def SetOutputLevelSettingMinVolumeEnable(self, value, qualifier):

        ChannelStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            'ST 1': '8',
            'ST 2': '9'
            }

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            OutputLevelSettingMinVolumeEnableCmdString = 's_output_level S 0000 00 NC {},,,,{}, \r'.format(
                                                        ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('OutputLevelSettingMinVolumeEnable', OutputLevelSettingMinVolumeEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevelSettingMinVolumeEnable')

    def UpdateOutputLevelSettingMinVolumeEnable(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4', '5', '6', '7', '8', 'ST 1', 'ST 2')

        if qualifier['Channel'] in ChannelStates:
            self.UpdateOutputLevelSettingLevel(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevelSettingMinVolumeEnable')

    def SetOutputMute(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            'ST 1': '8',
            'ST 2': '9'
        }
        channel = qualifier['Channel']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if channel in ChannelStates and value in ValueStateValues:
            OutputMuteCmdString = 'SOCM S 0000 00 NC {},{} \r'.format(ChannelStates[channel], ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        ChannelStates = {
            '1':    '0',
            '2':    '1',
            '3':    '2',
            '4':    '3',
            '5':    '4',
            '6':    '5',
            '7':    '6',
            '8':    '7',
            'ST 1': '8',
            'ST 2': '9'
        }
        channel = qualifier['Channel']

        if channel in ChannelStates:
            OutputMuteCmdString = 'GOCM O 0000 00 NC {} \r'.format(ChannelStates[channel])
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ChannelStates = {
            '0':    '1',
            '1':    '2',
            '2':    '3',
            '3':    '4',
            '4':    '5',
            '5':    '6',
            '6':    '7',
            '7':    '8',
            '8':    'ST 1',
            '9':    'ST 2'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Channel': ChannelStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 8:
            PresetRecallCmdString = 'CALLP S 0000 00 NC {} \r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
            
    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 8:
            PresetSaveCmdString = 'REGIP S 0000 00 NC {} \r'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetSubInputSettingGain(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 8 and 20 <= value <= 60:
            SubInputSettingGainCmdString = 's_subinput_channel_settings S 0000 00 NC {},,{},,,,, \r'.format(
                                                int(qualifier['Channel']) - 1, value - 20)
            self.__SetHelper('SubInputSettingGain', SubInputSettingGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSubInputSettingGain')

    def UpdateSubInputSettingGain(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 8:
            SubInputSettingGainCmdString = 'g_subinput_channel_settings O 0000 00 NC {} \r'.format(int(qualifier['Channel']) - 1)
            self.__UpdateHelper('SubInputSettingGain', SubInputSettingGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSubInputSettingGain')

    def __MatchSubInputSettingGain(self, match, tag):

        res = match.group(1).decode().split(',')
        
        qualifier = {}
        qualifier['Channel'] = str(int(res[0]) + 1)
        value = int(res[2]) + 20
        if 20 <= value <= 60:
            self.WriteStatus('SubInputSettingGain', value, qualifier)

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
            1:  'Grammatical error',
            2:  'Invalid command',
            3:  'Divided transmission error',
            4:  'Parameter error',
            90: 'Busy',
            92: 'Busy (evacuation mode)',
            99: 'Other error'
        }

        error = int(match.group(1).decode())
        self.Error(['An error occurred: {}: {}.'.format(error, error_map.get(error, 'Unknown error'))])

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