from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait


class DeviceClass:

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {
            'VSX-30': self.pion_27_2382_v30,
            'VSX-31': self.pion_27_2382_v31,
            'VSX-1120': self.pion_27_2382_1120or32,
            'VSX-32': self.pion_27_2382_1120or32,
            'VSX-33': self.pion_27_2382_v33,
            'SC-35': self.pion_27_2382_SC35,
            'SC-37': self.pion_27_2382_SC37,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AdapterPortOperation': {'Status': {}},
            'AmpPower': {'Status': {}},
            'ChannelLevel': {'Parameters': ['Channel'], 'Status': {}},
            'HDMIAudio': {'Status': {}},
            'HomeMediaGalleryOperation': {'Status': {}},
            'Input': {'Status': {}},
            'iPodOperation': {'Status': {}},
            'Keyboard': {'Status': {}},
            'MCACCMemoryRecall': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'PanelKeyLock': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteKeyLock': {'Status': {}},
            'SiriusChannel': {'Status': {}},
            'SiriusOperation': {'Status': {}},
            'TunerFrequencyStatus': {'Status': {}},
            'TunerFrequencyStep': {'Status': {}},
            'TunerBandToggle': {'Status': {}},
            'TunerClassToggle': {'Status': {}},
            'TunerPreset': {'Status': {}},
            'TunerPresetStatus': {'Status': {}},
            'Volume': {'Status': {}},
            'XMChannel': {'Status': {}},
            'XMOperation': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Mute': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Volume': {'Status': {}},
            'Zone3Input': {'Status': {}},
            'Zone3Power': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'SPK([0-3])\r\n'), self.__MatchAmpPower, None)
            self.AddMatchString(re.compile(b'CLV(R__|L__|C__|SL_|SR_|SBL|SBR|SW_|LH_|RH_|LW_|RW_)(\d{2})\r\n'), self.__MatchChannelLevel, None)
            self.AddMatchString(re.compile(b'HA(0|1)\r\n'), self.__MatchHDMIAudio, None)
            self.AddMatchString(re.compile(b'FN(\d{2})\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'MC([1-6])\r\n'), self.__MatchMCACCMemoryRecall, None)
            self.AddMatchString(re.compile(b'(Z2)?MUT(0|1)\r\n'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'PKL([0-2])\r\n'), self.__MatchPanelKeyLock, None)
            self.AddMatchString(re.compile(b'PWR(0|1)\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'RKL(0|1)\r\n'), self.__MatchRemoteKeyLock, None)
            self.AddMatchString(re.compile(b'SIR(\d{3})\r\n'), self.__MatchSiriusChannel, None)
            self.AddMatchString(re.compile(b'FR(F|A)(\d{5})\r\n'), self.__MatchTunerFrequencyStatus, None)
            self.AddMatchString(re.compile(b'PR([A-G]0[1-9])\r\n'), self.__MatchTunerPresetStatus, None)
            self.AddMatchString(re.compile(b'VOL(\d{3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'XM(\d{3})\r\n'), self.__MatchXMChannel, None)
            self.AddMatchString(re.compile(b'Z2F(\d{2})\r\n'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'Z3F(\d{2})\r\n'), self.__MatchZone3Input, None)
            self.AddMatchString(re.compile(b'APR(0|1)\r\n'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'BPR(0|1)\r\n'), self.__MatchZone3Power, None)
            self.AddMatchString(re.compile(b'ZV([0-8][0-9])\r\n'), self.__MatchZone2Volume, None)
            self.AddMatchString(re.compile(b'(E04|E06|B00)\r\n'), self.__MatchError, None)

    def SetAdapterPortOperation(self, value, qualifier):
        ValueStateValues = {
            'Play': '10',
            'Pause': '11',
            'Stop': '12',
            'Previous': '13',
            'Next': '14',
            'Rev': '15',
            'Fwd': '16',
        }

        AdapterPortOperationCmdString = '{0}BT\r'.format(ValueStateValues[value])
        self.__SetHelper('AdapterPortOperation', AdapterPortOperationCmdString, value, qualifier)

    def SetAmpPower(self, value, qualifier):
        ValueStateValues = {
            'Speaker Off': '0',
            'Speaker A On': '1',
            'Speaker B On': '2',
            'Speaker A+B On': '3',
        }

        AmpPowerCmdString = '{0}SPK\r'.format(ValueStateValues[value])
        self.__SetHelper('AmpPower', AmpPowerCmdString, value, qualifier)

    def UpdateAmpPower(self, value, qualifier):
        AmpPowerCmdString = '?SPK\r'
        self.__UpdateHelper('AmpPower', AmpPowerCmdString, value, qualifier)

    def __MatchAmpPower(self, match, tag):
        ValueStateValues = {
            '0': 'Speaker Off',
            '1': 'Speaker A On',
            '2': 'Speaker B On',
            '3': 'Speaker A+B On',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AmpPower', value, None)

    def SetChannelLevel(self, value, qualifier):
        ChannelStates = {
            'Front Left': 'L__',
            'Front Right': 'R__',
            'Center': 'C__',
            'Surround Left': 'SL_',
            'Surround Right': 'SR_',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR',
            'Subwoofer': 'SW_',
            'Front Height Left': 'LH_',
            'Front Height Right': 'RH_',
            'Front Wide Left': 'LW_',
            'Front Wide Right': 'RW_'
        }

        ValueConstraints = {
            'Min': -12,
            'Max': 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            tempValue = int((12.5 + value) * 2) + 25
            ChannelLevelCmdString = '{0}{1}CLV\r'.format(ChannelStates[qualifier['Channel']], tempValue)
            self.__SetHelper('ChannelLevel', ChannelLevelCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetChannelLevel')

    def UpdateChannelLevel(self, value, qualifier):
        ChannelStates = {
            'Front Left': 'L__',
            'Front Right': 'R__',
            'Center': 'C__',
            'Surround Left': 'SL_',
            'Surround Right': 'SR_',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR',
            'Subwoofer': 'SW_',
            'Front Height Left': 'LH_',
            'Front Height Right': 'RH_',
            'Front Wide Left': 'LW_',
            'Front Wide Right': 'RW_'
        }

        ChannelLevelCmdString = '?{0}CLV\r'.format(ChannelStates[qualifier['Channel']])
        self.__UpdateHelper('ChannelLevel', ChannelLevelCmdString, value, qualifier)

    def __MatchChannelLevel(self, match, tag):
        ChannelStates = {
            'L__': 'Front Left',
            'R__': 'Front Right',
            'C__': 'Center',
            'SL_': 'Surround Left',
            'SR_': 'Surround Right',
            'SBL': 'Surround Back Left',
            'SBR': 'Surround Back Right',
            'SW_': 'Subwoofer',
            'LH_': 'Front Height Left',
            'RH_': 'Front Height Right',
            'LW_': 'Front Wide Left',
            'RW_': 'Front Wide Right'
        }

        qualifier = {'Channel': ChannelStates[match.group(1).decode()]}
        value = int(match.group(2).decode())
        value = ((value - 25) / 2) - 12.5
        self.WriteStatus('ChannelLevel', value, qualifier)

    def SetHDMIAudio(self, value, qualifier):
        ValueStateValues = {
            'AMP': '0',
            'Through': '1',
        }

        HDMIAudioCmdString = '{0}HA\r'.format(ValueStateValues[value])
        self.__SetHelper('HDMIAudio', HDMIAudioCmdString, value, qualifier)

    def UpdateHDMIAudio(self, value, qualifier):
        HDMIAudioCmdString = '?HA\r'
        self.__UpdateHelper('HDMIAudio', HDMIAudioCmdString, value, qualifier)

    def __MatchHDMIAudio(self, match, tag):
        ValueStateValues = {
            '0': 'AMP',
            '1': 'Through',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDMIAudio', value, None)

    def SetHomeMediaGalleryOperation(self, value, qualifier):
        ValueStateValues = {
            '0': '00',
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            'Play': '10',
            'Pause': '11',
            'Previous': '12',
            'Next': '13',
            'Display': '18',
            'Stop': '20',
            'Up': '26',
            'Down': '27',
            'Right': '28',
            'Left': '29',
            'Enter': '30',
            'Return': '31',
            'Program': '32',
            'Clear': '33',
            'Repeat': '34',
            'Random': '35',
            'Menu': '36',
            'Edit': '37',
            'Class': '38'
        }

        HomeMediaGalleryOperationCmdString = '{0}NW\r'.format(ValueStateValues[value])
        self.__SetHelper('HomeMediaGalleryOperation', HomeMediaGalleryOperationCmdString, value, qualifier)

    def SetInput(self, value, qualifier):
        InputCmdString = '{0}FN\r'.format(self.InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        InputCmdString = '?F\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        value = self.MatchInputValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetiPodOperation(self, value, qualifier):
        ValueStateValues = {
            'Play': '00',
            'Pause': '01',
            'Stop': '02',
            'Previous': '03',
            'Next': '04',
            'Rev': '05',
            'Fwd': '06',
            'Repeat': '07',
            'Shuffle': '08',
            'Display': '09',
            'iPod Control': '10',
            'Up': '13',
            'Down': '14',
            'Right': '15',
            'Left': '16',
            'Enter': '17',
            'Return': '18',
            'Top Menu': '19'
        }

        iPodOperationCmdString = '{0}IP\r'.format(ValueStateValues[value])
        self.__SetHelper('iPodOperation', iPodOperationCmdString, value, qualifier)

    def SetKeyboard(self, value, qualifier):
        ValueStateValues = {
            'Space': 'FG20\r',
            '!': 'FG21\r',
            '"': 'FG22\r',
            '#': 'FG23\r',
            '$': 'FG24\r',
            '%': 'FG25\r',
            '&': 'FG26\r',
            '\'': 'FG27\r',
            '(': 'FG28\r',
            ')': 'FG29\r',
            '*': 'FG2A\r',
            '+': 'FG2B\r',
            ',': 'FG2C\r',
            '-': 'FG2D\r',
            '.': 'FG2E\r',
            '/': 'FG2F\r',
            '0': 'FG30\r',
            '1': 'FG31\r',
            '2': 'FG32\r',
            '3': 'FG33\r',
            '4': 'FG34\r',
            '5': 'FG35\r',
            '6': 'FG36\r',
            '7': 'FG37\r',
            '8': 'FG38\r',
            '9': 'FG39\r',
            ':': 'FG3A\r',
            ';': 'FG3B\r',
            '<': 'FG3C\r',
            '=': 'FG3D\r',
            '>': 'FG3E\r',
            '?': 'FG3F\r',
            '@': 'FG40\r',
            'A': 'FG41\r',
            'B': 'FG42\r',
            'C': 'FG43\r',
            'D': 'FG44r',
            'E': 'FG45\r',
            'F': 'FG46\r',
            'G': 'FG47\r',
            'H': 'FG48\r',
            'I': 'FG49\r',
            'J': 'FG4A\r',
            'K': 'FG4B\r',
            'L': 'FG4C\r',
            'M': 'FG4D\r',
            'N': 'FG4E\r',
            'O': 'FG4F\r',
            'P': 'FG50\r',
            'Q': 'FG51\r',
            'R': 'FG52\r',
            'S': 'FG53\r',
            'T': 'FG54\r',
            'U': 'FG55\r',
            'V': 'FG56\r',
            'W': 'FG57\r',
            'X': 'FG58\r',
            'Y': 'FG59\r',
            'Z': 'FG5A\r',
            '[': 'FG5B\r',
            '\\': 'FG5C\r',
            ']': 'FG5D\r',
            '^': 'FG5E\r',
            '_': 'FG5F\r',
            '`': 'FG60\r',
            'a': 'FG61\r',
            'b': 'FG62\r',
            'c': 'FG63\r',
            'd': 'FG64\r',
            'e': 'FG65\r',
            'f': 'FG66\r',
            'g': 'FG67\r',
            'h': 'FG68\r',
            'i': 'FG69\r',
            'j': 'FG6A\r',
            'k': 'FG6B\r',
            'l': 'FG6C\r',
            'm': 'FG6D\r',
            'n': 'FG6E\r',
            'o': 'FG6F\r',
            'p': 'FG70\r',
            'q': 'FG71\r',
            'r': 'FG72\r',
            's': 'FG73\r',
            't': 'FG74\r',
            'u': 'FG75\r',
            'v': 'FG76\r',
            'w': 'FG77\r',
            'x': 'FG78\r',
            'y': 'FG79\r',
            'z': 'FG7A\r',
            '{': 'FG7B\r',
            '|': 'FG7C\r',
            '}': 'FG7D\r',
            '~': 'FG7E\r',
            'Tab': 'FGTB\r',
            'Delete': 'FGDL\r',
            'Back Space': 'FGBS\r'
        }

        KeyboardCmdString = ValueStateValues[value]
        self.__SetHelper('Keyboard', KeyboardCmdString, value, qualifier)

    def SetMCACCMemoryRecall(self, value, qualifier):
        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }
        MCACCMemoryRecallCmdString = '{0}MS\r'.format(ValueStateValues[value])
        self.__SetHelper('MCACCMemoryRecall', MCACCMemoryRecallCmdString, value, qualifier, 3)

    def UpdateMCACCMemoryRecall(self, value, qualifier):
        MCACCMemoryRecallCmdString = '?MC\r'
        self.__UpdateHelper('MCACCMemoryRecall', MCACCMemoryRecallCmdString, value, qualifier)

    def __MatchMCACCMemoryRecall(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('MCACCMemoryRecall', value, None)

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Up': 'CUP\r',
            'Down': 'CDN\r',
            'Right': 'CRI\r',
            'Left': 'CLE\r',
            'Enter': 'CEN\r',
            'Return': 'CRT\r',
            'Audio Parameter': 'APA\r',
            'Video Parameter': 'VPA\r',
            'Home Menu': 'HM\r',
            'Key On/Off': 'KOF\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 3)

    def SetMute(self, value, qualifier):
        ValueStateValues = {
            'On': 'MO\r',
            'Off': 'MF\r'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):
        MuteCmdString = '?M\r'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):
        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }
        if match.group(1):
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Zone2Mute', value, None)
        else:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Mute', value, None)

    def SetPanelKeyLock(self, value, qualifier):
        ValueStateValues = {
            'Panel Key & Volume Lock Off': '0',
            'Panel Key Lock On': '1',
            'Panel Key & Volume Lock On': '2'
        }

        PanelKeyLockCmdString = '{0}PKL\r'.format(ValueStateValues[value])
        self.__SetHelper('PanelKeyLock', PanelKeyLockCmdString, value, qualifier)

    def UpdatePanelKeyLock(self, value, qualifier):
        PanelKeyLockCmdString = '?PKL\r'
        self.__UpdateHelper('PanelKeyLock', PanelKeyLockCmdString, value, qualifier)

    def __MatchPanelKeyLock(self, match, tag):
        ValueStateValues = {
            '0': 'Panel Key & Volume Lock Off',
            '1': 'Panel Key Lock On',
            '2': 'Panel Key & Volume Lock On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PanelKeyLock', value, None)

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On': 'PO\r',
            'Off': 'PF\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 5)

    def UpdatePower(self, value, qualifier):
        PowerCmdString = '?P\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetRemoteKeyLock(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        RemoteKeyLockCmdString = '{0}RML\r'.format(ValueStateValues[value])
        self.__SetHelper('RemoteKeyLock', RemoteKeyLockCmdString, value, qualifier)

    def UpdateRemoteKeyLock(self, value, qualifier):
        RemoteKeyLockCmdString = '?RML\r'
        self.__UpdateHelper('RemoteKeyLock', RemoteKeyLockCmdString, value, qualifier)

    def __MatchRemoteKeyLock(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RemoteKeyLock', value, None)

    def UpdateSiriusChannel(self, value, qualifier):
        SiriusChannelCmdString = '?SIR\r'
        self.__UpdateHelper('SiriusChannel', SiriusChannelCmdString, value, qualifier)

    def __MatchSiriusChannel(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('SiriusChannel', value, None)

    def SetSiriusOperation(self, value, qualifier):
        ValueStateValues = {
            '0': '00',
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            'Ch + / Cursor Down': '10',
            'Ch - / Cursor Up': '11',
            'Preset Station + / Cursor Right': '12',
            'Preset Station - / Cursor Left': '13',
            'Display': '14',
            'Preset': '15',
            'Class': '16',
            'Direct Access (CH)': '17',
            'Memory (EDIT)': '18',
            'Menu': '19',
            'Enter': '21',
            'Return': '22',
            'Category': '23'
        }

        SiriusOperationCmdString = '{0}SI\r'.format(ValueStateValues[value])
        self.__SetHelper('SiriusOperation', SiriusOperationCmdString, value, qualifier)

    def UpdateTunerFrequencyStatus(self, value, qualifier):
        TunerFrequencyStatusCmdString = '?FR\r'
        self.__UpdateHelper('TunerFrequencyStatus', TunerFrequencyStatusCmdString, value, qualifier)

    def __MatchTunerFrequencyStatus(self, match, tag):
        band = match.group(1).decode()
        frequency = match.group(2).decode()

        if band == 'F':
            frequency = str(float(frequency[:-2] + '.' + frequency[-2:]))
        else:
            frequency = str(int(frequency))

        value = band + 'M ' + frequency
        self.WriteStatus('TunerFrequencyStatus', value, None)

    def SetTunerFrequencyStep(self, value, qualifier):
        ValueStateValues = {
            'Increase': 'TFI\r',
            'Decrease': 'TFD\r'
        }

        TunerFStepCmdString = ValueStateValues[value]
        self.__SetHelper('TunerFrequencyStep', TunerFStepCmdString, value, qualifier)

    def SetTunerBandToggle(self, value, qualifier):
        TunerBandToggleCmdString = 'TB\r'
        self.__SetHelper('TunerBandToggle', TunerBandToggleCmdString, value, qualifier)

    def SetTunerClassToggle(self, value, qualifier):
        TunerClassToggleCmdString = 'TC\r'
        self.__SetHelper('TunerClassToggle', TunerClassToggleCmdString, value, qualifier)

    def SetTunerPreset(self, value, qualifier):
        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9'
        }

        TunerPresetCmdString = '{0}TP\r'.format(ValueStateValues[value])
        self.__SetHelper('TunerPreset', TunerPresetCmdString, value, qualifier)

    def UpdateTunerPresetStatus(self, value, qualifier):
        TunerPresetStatusCmdString = '?PR\r'
        self.__UpdateHelper('TunerPresetStatus', TunerPresetStatusCmdString, value, qualifier)

    def __MatchTunerPresetStatus(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('TunerPresetStatus', value, None)

    def SetVolume(self, value, qualifier):
        ValueConstraints = {
            'Min': -80,
            'Max': 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            tempValue = int((80.5 + value) * 2)
            VolumeCmdString = '{0:03}VL\r'.format(tempValue)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = '?V\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        tempValue = int(match.group(1).decode())
        if tempValue == 0:
            value = -80;
        else:
            value = (tempValue / 2 - 80.5)
        self.WriteStatus('Volume', value, None)

    def UpdateXMChannel(self, value, qualifier):
        XMChannelCmdString = '?XM\r'
        self.__UpdateHelper('XMChannel', XMChannelCmdString, value, qualifier)

    def __MatchXMChannel(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('XMChannel', value, None)

    def SetXMOperation(self, value, qualifier):
        ValueStateValues = {
            '0': '00',
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            'Ch + / Cursor Down': '10',
            'Ch - / Cursor Up': '11',
            'Preset Station + / Cursor Right': '12',
            'Preset Station - / Cursor Left': '13',
            'Display': '14',
            'Preset': '15',
            'Class': '16',
            'Direct Access (CH)': '17',
            'Memory (EDIT)': '18',
            'Menu': '19',
            'Enter': '21',
            'Return': '22',
            'Category': '23'
        }

        XMOperationCmdString = '{0}XM\r'.format(ValueStateValues[value])
        self.__SetHelper('XMOperation', XMOperationCmdString, value, qualifier)

    def SetZone3Input(self, value, qualifier):
        Zone3InputCmdString = '{0}ZT\r'.format(self.Zone3InputStateValues[value])
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier, 3)

    def UpdateZone3Input(self, value, qualifier):
        Zone3InputCmdString = '?ZT\r'
        self.__UpdateHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def __MatchZone3Input(self, match, tag):
        value = self.MatchZone3InputValues[match.group(1).decode()]
        self.WriteStatus('Zone3Input', value, None)

    def SetZone2Input(self, value, qualifier):
        Zone2InputCmdString = '{0}ZS\r'.format(self.Zone2InputStateValues[value])
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier, 3)

    def UpdateZone2Input(self, value, qualifier):
        Zone2InputCmdString = '?ZS\r'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):
        value = self.MatchZone2InputValues[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Mute(self, value, qualifier):
        ValueStateValues = {
            'On': 'Z2MO\r',
            'Off': 'Z2MF\r'
        }

        Zone2MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def UpdateZone2Mute(self, value, qualifier):
        Zone2MuteCmdString = '?Z2M\r'
        self.__UpdateHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def __MatchZone2Mute(self, match, tag):
        pass

    def SetZone3Power(self, value, qualifier):
        ValueStateValues = {
            'On': 'BPO\r',
            'Off': 'BPF\r'
        }

        Zone3PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier, 5)

    def UpdateZone3Power(self, value, qualifier):

        Zone3PowerCmdString = '?BP\r'
        self.__UpdateHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def __MatchZone3Power(self, match, tag):
        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone3Power', value, None)

    def SetZone2Power(self, value, qualifier):
        ValueStateValues = {
            'On': 'APO\r',
            'Off': 'APF\r'
        }

        Zone2PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier, 5)

    def UpdateZone2Power(self, value, qualifier):
        Zone2PowerCmdString = '?AP\r'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):
        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Volume(self, value, qualifier):
        ValueConstraints = {
            'Min': -80,
            'Max': 0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            tempValue = value + 81
            Zone2VolumeCmdString = '{0}ZV\r'.format(tempValue)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):
        Zone2VolumeCmdString = '?ZV\r'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):
        value = int(match.group(1).decode())
        if value == 0:
            value = 0
        else:
            value -= 81
        self.WriteStatus('Zone2Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        errors = {
            'E04': 'COMMAND ERROR',
            'E06': 'PARAMETER ERROR',
            'B00': 'BUSY'
        }
        value = errors[match.group(1).decode()]
        print(value)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pion_27_2382_SC35(self):
    
        self.InputStateValues = {
            'DVD' : '04', 
            'BD' : '25', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'HDMI 1' : '19', 
            'HDMI 2' : '20', 
            'HDMI 3' : '21', 
            'HDMI 4' : '22', 
            'HDMI 5 (Front)' : '23', 
            'Home Media Gallery' : '26', 
            'IPod/USB' : '17', 
            'XM Radio' : '18', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
            'Phono' : '00', 
            'Multi Channel In' : '12'
        }

        self.MatchInputValues = {
            '04' : 'DVD', 
            '25' : 'BD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '19' : 'HDMI 1', 
            '20' : 'HDMI 2', 
            '21' : 'HDMI 3', 
            '22' : 'HDMI 4', 
            '23' : 'HDMI 5 (Front)', 
            '26' : 'Home Media Gallery', 
            '17' : 'IPod/USB', 
            '18' : 'XM Radio', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
            '00' : 'Phono', 
            '12' : 'Multi Channel In'
        }

        self.Zone2InputStateValues = {
            'DVD' : '04', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'Home Media Gallery' : '26', 
            'IPod/USB' : '17', 
            'XM Radio' : '18', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
        }
        self.MatchZone2InputValues = {
            '04' : 'DVD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '26' : 'Home Media Gallery', 
            '17' : 'IPod/USB', 
            '18' : 'XM Radio', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
        }

        self.Zone3InputStateValues = {
            'DVD' : '04', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33'
        }

        self.MatchZone3InputValues = {
            '04' : 'DVD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port' 
        }

    def pion_27_2382_SC37(self):
    
        self.InputStateValues = {
            'DVD' : '04', 
            'BD' : '25', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'HDMI 1' : '19', 
            'HDMI 2' : '20', 
            'HDMI 3' : '21', 
            'HDMI 4' : '22', 
            'HDMI 5 (Front)' : '23', 
            'Home Media Gallery' : '26', 
            'IPod/USB' : '17', 
            'XM Radio' : '18', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
            'Phono' : '00', 
            'Multi Channel In' : '12'
        }

        self.MatchInputValues = {
            '04' : 'DVD', 
            '25' : 'BD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '19' : 'HDMI 1', 
            '20' : 'HDMI 2', 
            '21' : 'HDMI 3', 
            '22' : 'HDMI 4', 
            '23' : 'HDMI 5 (Front)', 
            '26' : 'Home Media Gallery', 
            '17' : 'IPod/USB', 
            '18' : 'XM Radio', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
            '00' : 'Phono', 
            '12' : 'Multi Channel In'
        }

        self.Zone2InputStateValues = {
            'DVD' : '04', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'Home Media Gallery' : '26', 
            'IPod/USB' : '17', 
            'XM Radio' : '18', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
        }
        self.MatchZone2InputValues = {
            '04' : 'DVD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '26' : 'Home Media Gallery', 
            '17' : 'IPod/USB', 
            '18' : 'XM Radio', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
        }

        self.Zone3InputStateValues = {
            'DVD' : '04', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'Home Media Gallery' : '26', 
            'IPod/USB' : '17', 
            'XM Radio' : '18', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
        }
        self.MatchZone3Input2Values = {
            '04' : 'DVD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '26' : 'Home Media Gallery', 
            '17' : 'IPod/USB', 
            '18' : 'XM Radio', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
        }

    def pion_27_2382_1120or32(self):

        self.InputStateValues = {
            'DVD' : '04', 
            'BD' : '25', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'HDMI 1' : '19', 
            'HDMI 2' : '20', 
            'HDMI 3' : '21', 
            'HDMI 4' : '22', 
            'HDMI 5 (Front)' : '23', 
            'Home Media Gallery' : '26', 
            'IPod/USB' : '17', 
            'XM Radio' : '18', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
        }

        self.MatchInputValues = {
            '04' : 'DVD', 
            '25' : 'BD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '19' : 'HDMI 1', 
            '20' : 'HDMI 2', 
            '21' : 'HDMI 3', 
            '22' : 'HDMI 4', 
            '23' : 'HDMI 5 (Front)', 
            '26' : 'Home Media Gallery', 
            '17' : 'IPod/USB', 
            '18' : 'XM Radio', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
        }

        self.Zone2InputStateValues = {
            'DVD' : '04', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10',  
            'Home Media Gallery' : '26', 
            'IPod/USB' : '17', 
            'XM Radio' : '18', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
        }

        self.MatchZone2InputValues = {
            '04' : 'DVD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '26' : 'Home Media Gallery', 
            '17' : 'IPod/USB', 
            '18' : 'XM Radio', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
        }

    def pion_27_2382_v30(self):

        self.InputStateValues = {
            'DVD' : '04', 
            'BD' : '25', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video 1' : '10', 
            'Video 2' : '14', 
            'HDMI 1' : '20', 
            'HDMI 2' : '21', 
            'HDMI 3' : '22', 
            'Home Media Gallery' : '26', 
            'iPod/USB' : '17', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
        }

        self.MatchInputValues = {
            '04' : 'DVD', 
            '25' : 'BD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video 1', 
            '14' : 'Video 2', 
            '20' : 'HDMI 1', 
            '21' : 'HDMI 2', 
            '22' : 'HDMI 3', 
            '26' : 'Home Media Gallery', 
            '17' : 'iPod/USB', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
        }

        self.Zone2InputStateValues = {
            'DVD' : '04', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video 1' : '10', 
            'Video 2' : '14', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
        }

        self.MatchZone2InputValues = {
            '04' : 'DVD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video 1',
            '14' : 'Video 2',
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
        }

    def pion_27_2382_v31(self):

        self.InputStateValues = {
            'DVD' : '04', 
            'BD' : '25', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Home Media Gallery' : '26', 
            'iPod/USB' : '17', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
            'HDMI 1' : '19', 
            'HDMI 2' : '20', 
            'HDMI 3' : '21', 
            'HDMI 4' : '22', 
            'HDMI 5' : '23', 
            'Video' : '10'
        }

        self.MatchInputValues = {
            '04' : 'DVD', 
            '25' : 'BD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '26' : 'Home Media Gallery', 
            '17' : 'iPod/USB', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
            '19' : 'HDMI 1', 
            '20' : 'HDMI 2', 
            '21' : 'HDMI 3', 
            '22' : 'HDMI 4', 
            '23' : 'HDMI 5', 
            '10' : 'Video'
        }

        self.Zone2InputStateValues = {
            'DVD' : '04', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'Home Media Gallery' : '26', 
            'IPod/USB' : '17', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
        }

        self.MatchZone2InputValues = {
            '04' : 'DVD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '26' : 'Home Media Gallery', 
            '17' : 'IPod/USB', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
        }

    def pion_27_2382_v33(self):
    
        self.InputStateValues = {
            'DVD' : '04', 
            'BD' : '25', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'HDMI 1' : '19', 
            'HDMI 2' : '20', 
            'HDMI 3' : '21', 
            'HDMI 4' : '22', 
            'HDMI 5 (Front)' : '23', 
            'Home Media Gallery' : '26', 
            'IPod/USB' : '17', 
            'XM Radio' : '18', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
        }

        self.MatchInputValues = {
            '04' : 'DVD', 
            '25' : 'BD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '19' : 'HDMI 1', 
            '20' : 'HDMI 2', 
            '21' : 'HDMI 3', 
            '22' : 'HDMI 4', 
            '23' : 'HDMI 5 (Front)', 
            '26' : 'Home Media Gallery', 
            '17' : 'IPod/USB', 
            '18' : 'XM Radio', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
        }

        self.Zone2InputStateValues = {
            'DVD' : '04', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'Home Media Gallery' : '26', 
            'IPod/USB' : '17', 
            'XM Radio' : '18', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
        }

        self.MatchZone2InputValues = {
            '04' : 'DVD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '26' : 'Home Media Gallery', 
            '17' : 'IPod/USB', 
            '18' : 'XM Radio', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
        }

        self.Zone3InputStateValues = {
            'DVD' : '04', 
            'TV/SAT' : '05', 
            'DVR/BDR' : '15', 
            'Video' : '10', 
            'CD' : '01', 
            'CD-R/Tape' : '03', 
            'Tuner' : '02', 
            'Adapter Port' : '33', 
            'Sirius' : '27', 
        }

        self.MatchZone3InputValues = {
            '04' : 'DVD', 
            '05' : 'TV/SAT', 
            '15' : 'DVR/BDR', 
            '10' : 'Video', 
            '01' : 'CD', 
            '03' : 'CD-R/Tape', 
            '02' : 'Tuner', 
            '33' : 'Adapter Port', 
            '27' : 'Sirius', 
        }

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}

    # Check incoming unsolicited data to see if it matched with device expectancy. 
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True      

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')
        
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
        if self.connectionFlag == False:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
