from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, search
from extronlib.system import ProgramLog, Wait
from decimal import Decimal, ROUND_HALF_UP
import copy

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 4096
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AECEnable': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'AECGain': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'AECPhantomPower': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'AutoAnswer': {'Parameters': ['Instance Tag', 'Line'], 'Status': {}},
            'AutoMixerCombinerInputGroup': {'Parameters': ['Instance Tag', 'Input'], 'Status': {}},
            'AVBInputLevel': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'AVBInputMute': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'AVBOutputLevel': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'AVBOutputMute': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'Bluetooth': {'Parameters': ['Instance Tag'], 'Status': {}},
            'BluetoothConnectedDeviceName': {'Parameters': ['Instance Tag'], 'Status': {}},
            'BluetoothUSBConnectionStatus': {'Parameters': ['Instance Tag'], 'Status': {}},
            'BluetoothDeviceName': {'Parameters': ['Instance Tag'], 'Status': {}},
            'BluetoothDiscovery': {'Parameters': ['Instance Tag'], 'Status': {}},
            'BluetoothUSBStreamingStatus': {'Parameters': ['Instance Tag'], 'Status': {}},
            'ConnectionStatus': {'Status': {}},
            'CrosspointLevel': {'Parameters': ['Instance Tag', 'Input', 'Output'], 'Status': {}},
            'CrosspointState': {'Parameters': ['Instance Tag', 'Input', 'Output'], 'Status': {}},
            'DeviceFaultList': {'Status': {}},
            'DoNotDisturb': {'Parameters': ['Instance Tag', 'Line'], 'Status': {}},
            'DTMF': {'Parameters': ['Instance Tag', 'Line'], 'Status': {}},
            'FineLevelControl': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'GraphicEqualizerBandGain': {'Parameters': ['Instance Tag', 'Band'], 'Status': {}},
            'InputLevel': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'LastDialed': {'Parameters': ['Instance Tag', 'Line'], 'Status': {}},
            'LogicInputOutput': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'LogicMeter': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'LogicState': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'LevelControl': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'MuteControl': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'NewSpeedDialEntryNameCommand': {'Parameters': ['Instance Tag', 'Line', 'Entry'], 'Status': {}},
            'NewSpeedDialEntryNumberCommand': {'Parameters': ['Instance Tag', 'Line', 'Entry'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetRecallName': {'Parameters': ['Name'], 'Status': {}},
            'PresetSave': {'Status': {}},
            'PresetSaveName': {'Parameters': ['Name'], 'Status': {}},
            'RoomCombinerGroup': {'Parameters': ['Instance Tag', 'Room'], 'Status': {}},
            'RoomCombinerInputLevel': {'Parameters': ['Instance Tag', 'Room'], 'Status': {}},
            'RoomCombinerInputMute': {'Parameters': ['Instance Tag', 'Room'], 'Status': {}},
            'RoomCombinerOutputLevel': {'Parameters': ['Instance Tag', 'Room'], 'Status': {}},
            'RoomCombinerOutputMute': {'Parameters': ['Instance Tag', 'Room'], 'Status': {}},
            'RoomCombinerSourceLevel': {'Parameters': ['Instance Tag', 'Room'], 'Status': {}},
            'RoomCombinerSourceMute': {'Parameters': ['Instance Tag', 'Room'], 'Status': {}},
            'RoomCombinerSourceSelection': {'Parameters': ['Instance Tag', 'Room'], 'Status': {}},
            'RoomCombinerWall': {'Parameters': ['Instance Tag', 'Wall'], 'Status': {}},
            'RouterControl': {'Parameters': ['Instance Tag', 'Output'], 'Status': {}},
            'SignalPresentMeter': {'Parameters': ['Instance Tag', 'Channel', 'Meter Name'], 'Status': {}},
            'SourceSelectorOutputLevel': {'Parameters':['Instance Tag'], 'Status': {}},
            'SourceSelectorOutputMute': {'Parameters':['Instance Tag'], 'Status': {}},
            'SourceSelectorSourceSelection': {'Parameters': ['Instance Tag'], 'Status': {}},
            'SpeedDial': {'Parameters': ['Instance Tag', 'Line', 'Call Appearance'], 'Status': {}},
            'SpeedDialEntryName': {'Parameters': ['Instance Tag', 'Line', 'Entry'], 'Status': {}},
            'SpeedDialEntryNumber': {'Parameters': ['Instance Tag', 'Line', 'Entry'], 'Status': {}},
            'TICallerID': {'Parameters': ['Instance Tag'], 'Status': {}},
            'TICallStatus': {'Parameters': ['Instance Tag'], 'Status': {}},
            'TIHook': {'Parameters': ['Instance Tag', 'Line', 'Number'], 'Status': {}},
            'TILineInUse': {'Parameters': ['Instance Tag'], 'Status': {}},
            'TIReceiveLevel': {'Parameters': ['Instance Tag'], 'Status': {}},
            'TIReceiveMute': {'Parameters': ['Instance Tag'], 'Status': {}},
            'TITransmitLevel': {'Parameters': ['Instance Tag'], 'Status': {}},
            'TITransmitMute': {'Parameters': ['Instance Tag'], 'Status': {}},
            'VerboseMode': {'Status': {}},
            'VoIPCallerID': {'Parameters': ['Instance Tag', 'Line', 'Call Appearance'], 'Status': {}},
            'VoIPCallStatus': {'Parameters': ['Instance Tag', 'Line', 'Call Appearance'], 'Status': {}},
            'VoIPHook': {'Parameters': ['Instance Tag', 'Line', 'Call Appearance', 'Number'], 'Status': {}},
            'VoIPLineInUse': {'Parameters': ['Instance Tag', 'Line', 'Call Appearance'], 'Status': {}},
            'VoIPReceiveLevel': {'Parameters': ['Instance Tag', 'Line'], 'Status': {}},
            'VoIPReceiveMute': {'Parameters': ['Instance Tag', 'Line'], 'Status': {}},
            'VoIPTransmitLevel': {'Parameters': ['Instance Tag', 'Line'], 'Status': {}},
            'VoIPTransmitMute': {'Parameters': ['Instance Tag', 'Line'], 'Status': {}},
        }

        self.InitialStatusList = []
        self.MatchstringList = []
        self.SUBSCRIPTION_RESPONSE_TIME = 100
        self.VerboseDisabled = True
        if 'Serial' not in self.ConnectionType:
            self.deviceUsername = 'default'
            self.devicePassword = None

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\! \"publishToken\":\"([\S ]+?)\" \"value\":([\S ]+?)\r\n'), self.__MatchAllSubscribe, None)

            self.AddMatchString(compile(b'SESSION set verbose true\r\n\+OK\r\n'), self.__MatchVerboseMode, 'Set')
            self.AddMatchString(compile(b'SESSION get verbose\r\n\+OK \"value\":(true|false)\r\n'), self.__MatchVerboseMode, 'Update')

            self.AddMatchString(compile(b'DEVICE get version\r\n\+OK \"value\":\"([\d+.]+)\"\r\n'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(b'-(ERR .*?|CANNOT_DELIVER|GENERAL_FAILURE)\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'OK \"value\":\[{\"id\":(INDICATOR_NONE_IN_DEVICE|INDICATOR_MINOR_IN_DEVICE|INDICATOR_MAJOR_IN_DEVICE) \"name\":\"(No fault in device|Minor Fault in (System|Device)|Major Fault in (System|Device))\" \"faults\"'), self.__MatchDeviceFaultList, None)

    def __MatchError(self, match, tag):
        self.counter = 0
        errorMessage = match.group(1).decode().replace('ERR ', '')
        if errorMessage not in ['ALREADY_SUBSCRIBED', 'NOT_SUBSCRIBED']:
            self.Error([errorMessage])

    def __MatchVerboseMode(self, match, tag):
        self.VerboseDisabled = False

        if tag == 'Set':
            self.WriteStatus('VerboseMode', 'True')
        elif tag == 'Update':
            if match.group(1).decode() == 'true':
                self.WriteStatus('VerboseMode', 'True')
            else:
                self.WriteStatus('VerboseMode', 'False')

    def __MatchAllSubscribe(self, match, tag):

        StateValues = {
            'true' : ['On',  'True',  'Connected',    'Signal Present',    'In Use'],
            'false': ['Off', 'False', 'Disconnected', 'No Signal Present', 'Not in Use']
        }

        label = match.group(1).decode()
        data = [label[:label.index('_')],label[label.index('_')+1:]]
        paramsList = data[1].split('_')
        if data[0] in ['AECPhantomPower','LogicMeter','MuteControl']:
            stateIndex = 1 if data[0] == 'LogicMeter' else 0
            chnl = 1
            allValues = findall('false|true',match.group(2).decode())
            for value in allValues:
                self.WriteStatus(data[0], StateValues[value][stateIndex], {'Instance Tag': data[1], 'Channel': str(chnl)})
                chnl += 1

        elif data[0] in ['Bluetooth','BluetoothDiscovery','BluetoothUSBConnectionStatus','BluetoothUSBStreamingStatus']:
            stateIndex = 2 if data[0] == 'BluetoothUSBConnectionStatus' else 0
            value = StateValues[match.group(2).decode()][stateIndex]
            self.WriteStatus(data[0], value, {'Instance Tag': data[1]})

        elif data[0] == 'BluetoothConnectedDeviceName':
            if match.group(2):
                value = match.group(2).decode()
            else:
                value = ''
            self.WriteStatus('BluetoothConnectedDeviceName', value, {'Instance Tag': data[1]})

        elif data[0] == 'FineLevelControl':
            chnl = 1
            allValues = findall('(-?\d+\.\d+)', match.group(2).decode())
            for value in allValues:
                value = Decimal(float(value)).quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
                self.WriteStatus('FineLevelControl', value, {'Instance Tag': data[1], 'Channel': str(chnl)})
                chnl += 1

        elif data[0] == 'LevelControl':
            chnl = 1
            allValues = findall('(-?\d+)\.\d+', match.group(2).decode())
            for value in allValues:
                self.WriteStatus('LevelControl', int(value), {'Instance Tag': data[1], 'Channel': str(chnl)})
                chnl += 1

        elif data[0] == 'RoomCombinerOutputLevel':
            value = int(float(match.group(2).decode()))
            tag = '_'.join(paramsList[:len(paramsList)-1])
            room = paramsList[-1]
            self.WriteStatus('RoomCombinerOutputLevel', value, {'Instance Tag': tag, 'Room': room})

        elif data[0] == 'SignalPresentMeter':
            value = StateValues[match.group(2).decode()][3]
            tag = '_'.join(paramsList[:len(paramsList)-2])
            chnl = paramsList[-2]
            mtrName = paramsList[-1]
            self.WriteStatus('SignalPresentMeter', value, {'Instance Tag': tag, 'Channel': chnl, 'Meter Name': mtrName})

        elif data[0] == 'SourceSelectorOutputLevel':
            value = int(float(match.group(2).decode()))
            self.WriteStatus('SourceSelectorOutputLevel', value, {'Instance Tag' : data[1]})
        
        elif data[0] == 'SourceSelectorOutputMute':
            value = StateValues[match.group(2).decode()][0]
            self.WriteStatus('SourceSelectorOutputMute', value, {'Instance Tag' : data[1]})

        elif data[0] == 'SourceSelectorSourceSelection':
            value = match.group(2).decode()
            if value == '0':
                self.WriteStatus('SourceSelectorSourceSelection', 'No Source', {'Instance Tag': data[1]})
            elif 1 <= int(value) <= 32:
                self.WriteStatus('SourceSelectorSourceSelection', value, {'Instance Tag': data[1]})

        elif data[0] == 'TICallStatus':
            res = match.group(2).decode()

            stateValues = findall('\"state\":TI_CALL_STATE_(\w+) \"', res)
            for val in stateValues:
                value = val.replace('_', ' ').title()
                self.WriteStatus('TICallStatus', value, {'Instance Tag': data[1]})

            idValues = findall('"cid":"\x5C\x5C"(\d{8})\x5C\x5C"\x5C\x5C"(.*?)\x5C\x5C"\x5C\x5C"(.*?)\x5C\x5C""|"cid":""', res)
            for id_ in idValues:
                name = id_[2]
                number = id_[1]
                if number:
                    if name:
                        value = name + ' : ' + number
                    else:
                        value = number
                else:
                    value = ''
                self.WriteStatus('TICallerID', value, {'Instance Tag': data[1]})

        elif data[0] == 'TILineInUse':
            value = StateValues[match.group(2).decode()][4]
            self.WriteStatus('TILineInUse', value, {'Instance Tag': data[1]})

        elif data[0] == 'VoIPCallStatus':
            line = 1
            call = 1
            res = match.group(2).decode()

            stateValues = findall('\"state\":VOIP_CALL_STATE_(\w+) \"', res)
            for val in stateValues:
                value = val.replace('_', ' ').replace('XFER', 'Transfer').title()
                self.WriteStatus('VoIPCallStatus', value, {'Instance Tag': data[1], 'Line': str(line), 'Call Appearance': str(call)})
                if call >= 6:
                    call = 0
                    line += 1
                call += 1

            line = 1
            call = 1
            idValues = findall('"cid":"\x5C\x5C"(\d{8})\x5C\x5C"\x5C\x5C"(.*?)\x5C\x5C"\x5C\x5C"(.*?)\x5C\x5C""|"cid":""', res)
            for id_ in idValues:
                name = id_[2]
                number = id_[1]
                if number:
                    value = number
                    if name:
                        value = name + ' : ' + number
                else:
                    value = ''
                self.WriteStatus('VoIPCallerID', value, {'Instance Tag': data[1], 'Line': str(line), 'Call Appearance': str(call)})
                if call >= 6:
                    call = 0
                    line += 1
                call += 1

        elif data[0] == 'VoIPLineInUse':
            value = StateValues[match.group(2).decode()][4]
            tag = '_'.join(paramsList[:len(paramsList)-2])
            line = paramsList[-2]
            call = paramsList[-1]
            self.WriteStatus('VoIPLineInUse', value, {'Instance Tag': tag, 'Line': line, 'Call Appearance': call})

    def SetAECEnable(self, value, qualifier):

        state = {
            'On': 'true',
            'Off': 'false',
        }
        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 24 and value in state:
            cmdString = '{0} set aecEnable {1} {2}\n'.format(tag, chnl, state[value])
            self.__SetHelper('AECEnable', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAECEnable')

    def UpdateAECEnable(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('AECEnable',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 24:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get aecEnable (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchAECEnable, None)
            self.__UpdateHelper('AECEnable', '{0} get aecEnable {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAECEnable')

    def __MatchAECEnable(self, match, tag):

        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('AECEnable', value, qualifier)

    def SetAECGain(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 24 and 0 <= value <= 66:
            cmdString = '{0} set gain {1} {2}\n'.format(tag, chnl, value)
            self.__SetHelper('AECGain', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAECGain')

    def UpdateAECGain(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('AECGain',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 24:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get gain (\d+)\r\n\+OK \"value\":([-\d.]+)\r\n'.format(tag).encode()), self.__MatchAECGain, None)
            self.__UpdateHelper('AECGain', '{0} get gain {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAECGain')

    def __MatchAECGain(self, match, tag):

        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = int(float(match.group(3).decode()))
        self.WriteStatus('AECGain', value, qualifier)

    def SetAECPhantomPower(self, value, qualifier):

        state = {
            'On': 'true',
            'Off': 'false',
        }
        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 24 and value in state:
            cmdString = '{0} set phantomPower {1} {2}\n'.format(tag, chnl, state[value])
            self.__SetHelper('AECPhantomPower', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAECPhantomPower')

    def UpdateAECPhantomPower(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('AECPhantomPower',tag)
        self._UpdateSubscribeHelper('AECPhantomPower', 'phantomPowers', tag, label, qualifier)

    def SetAutoAnswer(self, value, qualifier):

        state = {
            'On': 'true',
            'Off': 'false',
        }
        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2', 'None'] and value in state:
            if line in ['1','2']:
                cmdString = '{0} set autoAnswer {1} {2}\n'.format(tag, line, state[value])
            else:
                cmdString = '{0} set autoAnswer {1}\n'.format(tag, state[value])

            self.__SetHelper('AutoAnswer', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoAnswer')

    def UpdateAutoAnswer(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        cmdTag = '{}_{}'.format('AutoAnswer',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1','2', 'None']:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get autoAnswer ?(\d+)?\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchAutoAnswer, None)

            if line in ['1','2']:
                self.__UpdateHelper('AutoAnswer', '{0} get autoAnswer {1}\n'.format(tag, line), value, qualifier)
            else:
                self.__UpdateHelper('AutoAnswer', '{0} get autoAnswer\n'.format(tag), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutoAnswer')

    def __MatchAutoAnswer(self, match, tag):

        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        if match.group(2):
            qualifier['Line'] = match.group(2).decode()
        else:
            qualifier['Line'] = 'None'
        value = state[match.group(3).decode()]
        self.WriteStatus('AutoAnswer', value, qualifier)

    def SetAutoMixerCombinerInputGroup(self, value, qualifier):

        ValueStateValues = {
            'None' : '0',
            'A' : '1',
            'B' : '2',
            'C' : '3',
            'D' : '4',
            'E' : '5',
            'F' : '6',
            'G' : '7',
            'H' : '8',
            'I' : '9',
            'J' : '10',
            'K' : '11',
            'L' : '12',
            'M' : '13',
            'N' : '14',
            'O' : '15',
            'P' : '16',
            'Q' : '17',
            'R' : '18',
            'S' : '19',
            'T' : '20',
            'U' : '21',
            'V' : '22',
            'W' : '23',
            'X' : '24',
            'Y' : '25',
            'Z' : '26',
            'a' : '27',
            'b' : '28',
            'c' : '29',
            'd' : '30',
            'e' : '31',
            'f' : '32'
        }

        tag = qualifier['Instance Tag']
        input_ = qualifier['Input']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(input_) <= 32 and value in ValueStateValues:
            cmdString = '{0} set inputGroup {1} {2}\n'.format(tag, input_, ValueStateValues[value])
            self.__SetHelper('AutoMixerCombinerInputGroup', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoMixerCombinerInputGroup')

    def UpdateAutoMixerCombinerInputGroup(self, value, qualifier):

        tag = qualifier['Instance Tag']
        input_ = qualifier['Input']
        cmdTag = '{}_{}'.format('AutoMixerCombinerInputGroup',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(input_) <= 32:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get inputGroup (\d+)\r\n\+OK \"value\":([-\d. ]+)\r\n'.format(tag).encode()), self.__MatchAutoMixerCombinerInputGroup, None)
            self.__UpdateHelper('AutoMixerCombinerInputGroup', '{0} get inputGroup {1}\n'.format(tag, input_), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutoMixerCombinerInputGroup')

    def __MatchAutoMixerCombinerInputGroup(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Input'] = match.group(2).decode()
        value = int(match.group(3).decode())
        if value == 0:
            value = 'None'
        elif 1 <= value <= 26:
            value = chr(value + 64)
        else:
            value = chr(value + 70)
        self.WriteStatus('AutoMixerCombinerInputGroup', value, qualifier)

    def SetAVBInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 60 and -100 <= value <= 12:
            cmdString = '{0} set level {1} {2}\n'.format(tag, chnl, value)
            self.__SetHelper('AVBInputLevel', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVBInputLevel')

    def UpdateAVBInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('AVBInputLevel', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 60:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get level (\d+)\r\n\+OK \"value\":([-\d.]+)\r\n'.format(tag).encode()), self.__MatchAVBInputLevel, None)
            self.__UpdateHelper('AVBInputLevel', '{0} get level {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAVBInputLevel')

    def __MatchAVBInputLevel(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = int(float(match.group(3).decode()))
        self.WriteStatus('AVBInputLevel', value, qualifier)

    def SetAVBInputMute(self, value, qualifier):

        state = {'On': 'true', 'Off': 'false'}
        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 60 and value in state:
            cmdString = '{0} set mute {1} {2}\n'.format(tag, chnl, state[value])
            self.__SetHelper('AVBInputMute', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVBInputMute')

    def UpdateAVBInputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('AVBInputMute', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 60:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get mute (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchAVBInputMute, None)
            self.__UpdateHelper('AVBInputMute', '{0} get mute {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAVBInputMute')

    def __MatchAVBInputMute(self, match, tag):
        state = {'true': 'On', 'false': 'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('AVBInputMute', value, qualifier)

    def SetAVBOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 60 and -100 <= value <= 0:
            cmdString = '{0} set level {1} {2}\n'.format(tag, chnl, value)
            self.__SetHelper('AVBOutputLevel', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVBOutputLevel')

    def UpdateAVBOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('AVBOutputLevel', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 60:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get level (\d+)\r\n\+OK \"value\":([-\d.]+)\r\n'.format(tag).encode()), self.__MatchAVBOutputLevel, None)
            self.__UpdateHelper('AVBOutputLevel', '{0} get level {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAVBOutputLevel')

    def __MatchAVBOutputLevel(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = int(float(match.group(3).decode()))
        self.WriteStatus('AVBOutputLevel', value, qualifier)

    def SetAVBOutputMute(self, value, qualifier):

        state = {'On': 'true', 'Off': 'false'}
        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 60 and value in state:
            cmdString = '{0} set mute {1} {2}\n'.format(tag, chnl, state[value])
            self.__SetHelper('AVBOutputMute', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVBOutputMute')

    def UpdateAVBOutputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('AVBOutputMute', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 60:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get mute (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchAVBOutputMute, None)
            self.__UpdateHelper('AVBOutputMute', '{0} get mute {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAVBOutputMute')

    def __MatchAVBOutputMute(self, match, tag):
        state = {'true': 'On', 'false': 'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('AVBOutputMute', value, qualifier)

    def SetBluetooth(self, value, qualifier):

        state = {'On': 'true', 'Off': 'false'}
        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if value in state:
            cmdString = '{0} set enable {1}\n'.format(tag, state[value])
            self.__SetHelper('Bluetooth', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBluetooth')

    def UpdateBluetooth(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('Bluetooth', tag)
        self._UpdateSubscribeHelper('Bluetooth', 'enable', tag, label, qualifier)

    def UpdateBluetoothConnectedDeviceName(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('BluetoothConnectedDeviceName', tag)
        self._UpdateSubscribeHelper('BluetoothConnectedDeviceName', 'connectedDeviceName', tag, label, qualifier)

    def UpdateBluetoothUSBConnectionStatus(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('BluetoothUSBConnectionStatus', tag)
        self._UpdateSubscribeHelper('BluetoothUSBConnectionStatus', 'connected', tag, label, qualifier)

    def UpdateBluetoothDeviceName(self, value, qualifier):

        tag = qualifier['Instance Tag']
        cmdTag = '{}_{}'.format('BluetoothDeviceName', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if cmdTag not in self.MatchstringList:
            self.MatchstringList.append(cmdTag)
            self.AddMatchString(compile('({0}) get deviceName\r\n\+OK \"value\":"([\S ]+)?"\r\n'.format(tag).encode()), self.__MatchBluetoothDeviceName, None)
        self.__UpdateHelper('BluetoothDeviceName', '{0} get deviceName\n'.format(tag), value, qualifier)

    def __MatchBluetoothDeviceName(self, match, tag):

        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        if match.group(2):
            value = match.group(2).decode()
        else:
            value = ''
        self.WriteStatus('BluetoothDeviceName', value, qualifier)

    def SetBluetoothDiscovery(self, value, qualifier):

        state = {'On': 'true', 'Off': 'false'}
        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"' + tag + '\"'
            
        if value in state:
            cmdString = '{0} set discoverable {1}\n'.format(tag, state[value])
            self.__SetHelper('BluetoothDiscovery', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBluetoothDiscovery')

    def UpdateBluetoothDiscovery(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('BluetoothDiscovery', tag)
        self._UpdateSubscribeHelper('BluetoothDiscovery', 'discoverable', tag, label, qualifier)

    def UpdateBluetoothUSBStreamingStatus(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('BluetoothUSBStreamingStatus', tag)
        self._UpdateSubscribeHelper('BluetoothUSBStreamingStatus', 'streaming', tag, label, qualifier)

    def SetCrosspointLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        Input = qualifier['Input']
        Output = qualifier['Output']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if  1 <= int(Input) <= 256 and 1 <= int(Output) <= 256 and -100 <= value <= 0:
            cmdString = '{0} set crosspointLevel {1} {2} {3}\n'.format(tag, Input, Output, value)
            self.__SetHelper('CrosspointLevel', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointLevel')

    def UpdateCrosspointLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        Input = qualifier['Input']
        Output = qualifier['Output']
        cmdTag = '{}_{}'.format('CrosspointLevel',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(Input) <= 256 and 1 <= int(Output) <= 256:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get crosspointLevel (\d+) (\d+)\r\n\+OK \"value\":([-\d.]+)\r\n'.format(tag).encode()), self.__MatchCrosspointLevel, None)
            self.__UpdateHelper('CrosspointLevel', '{0} get crosspointLevel {1} {2}\n'.format(tag, Input, Output), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCrosspointLevel')

    def __MatchCrosspointLevel(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Input'] = match.group(2).decode()
        qualifier['Output'] = match.group(3).decode()
        value = int(float(match.group(4).decode()))
        self.WriteStatus('CrosspointLevel', value, qualifier)

    def SetCrosspointState(self, value, qualifier):

        state = {
            'On': 'true',
            'Off': 'false',
        }

        tag = qualifier['Instance Tag']
        Input = qualifier['Input']
        Output = qualifier['Output']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(Input) <= 256 and 1 <= int(Output) <= 256 and value in state:
            cmdString = '{0} set crosspointLevelState {1} {2} {3}\n'.format(tag, Input, Output, state[value])
            self.__SetHelper('CrosspointState', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCrosspointState')

    def UpdateCrosspointState(self, value, qualifier):

        tag = qualifier['Instance Tag']
        Input = qualifier['Input']
        Output = qualifier['Output']
        cmdTag = '{}_{}'.format('CrosspointState',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(Input) <= 256 and 1 <= int(Output) <= 256:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get crosspointLevelState (\d+) (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchCrosspointState, None)
            self.__UpdateHelper('CrosspointState', '{0} get crosspointLevelState {1} {2}\n'.format(tag, Input, Output), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCrosspointState')

    def __MatchCrosspointState(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Input'] = match.group(2).decode()
        qualifier['Output'] = match.group(3).decode()
        value = state[match.group(4).decode()]
        self.WriteStatus('CrosspointState', value, qualifier)

    def UpdateDeviceFaultList(self, value, qualifier):

        cmdString = 'DEVICE get activeFaultList\n'
        self.__UpdateHelper('DeviceFaultList',cmdString, value,qualifier)

    def __MatchDeviceFaultList(self, match, tag):
        if match.group(2).decode().lower() == 'no fault in device':
            self.WriteStatus('DeviceFaultList', 'No Fault in Device')
        else:
            self.WriteStatus('DeviceFaultList', 'Errors in Fault List')

    def SetDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false',
        }
        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1','2'] and value in ValueStateValues:
            DoNotDisturbCmdString = '{0} set dndEnable {1} {2}\n'.format(tag, line, ValueStateValues[value])
            self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDoNotDisturb')

    def UpdateDoNotDisturb(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        cmdTag = '{}_{}'.format('DoNotDisturb',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2']:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get dndEnable (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchDoNotDisturb, None)
            self.__UpdateHelper('DoNotDisturb', '{0} get dndEnable {1}\n'.format(tag, line), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDoNotDisturb')

    def __MatchDoNotDisturb(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Line'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('DoNotDisturb', value, qualifier)

    def SetDTMF(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2', 'None'] and value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']:
            if line in ['1', '2']:
                cmdString = '{0} dtmf {1} {2}\n'.format(tag, line, value)
            else:
                cmdString = '{0} dtmf {1}\n'.format(tag, value)

            self.__SetHelper('DTMF', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetFineLevelControl(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 32 and -100.0 <= value <= 12.0:
            cmdString = '{0} set level {1} {2:.1f}\n'.format(tag, chnl, value)
            self.__SetHelper('FineLevelControl', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFineLevelControl')

    def UpdateFineLevelControl(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('FineLevelControl',tag)
        self._UpdateSubscribeHelper('FineLevelControl', 'levels', tag, label, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):

        self.__UpdateHelper('FirmwareVersion', 'DEVICE get version\n', value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):
        try:
            version = search('\+OK "value":"(.*)"\r\n', match.group(0).decode())
        except:
            self.Error(['FirmwareVersion: Invalid/unexpected response'])

        if version:
            self.WriteStatus('FirmwareVersion', version.group(1))

    def SetGraphicEqualizerBandGain(self, value, qualifier):

        tag = qualifier['Instance Tag']
        band = qualifier['Band']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(band) <= 31 and -30 <= value <= 15:
            cmdString = '{0} set gain {1} {2}\n'.format(tag, band, value)
            self.__SetHelper('GraphicEqualizerBandGain', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGraphicEqualizerBandGain')

    def UpdateGraphicEqualizerBandGain(self, value, qualifier):

        tag = qualifier['Instance Tag']
        band = qualifier['Band']
        cmdTag = '{}_{}'.format('GraphicEqualizerBandGain', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(band) <= 31:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get gain (\d+)\r\n\+OK \"value\":([-\d.]+)\r\n'.format(tag).encode()), self.__MatchGraphicEqualizerBandGain, None)
            self.__UpdateHelper('GraphicEqualizerBandGain', '{0} get gain {1}\n'.format(tag, band), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGraphicEqualizerBandGain')

    def __MatchGraphicEqualizerBandGain(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Band'] = match.group(2).decode()
        value = Decimal(float(match.group(3).decode())).quantize(Decimal('.1'),rounding=ROUND_HALF_UP)
        self.WriteStatus('GraphicEqualizerBandGain', value, qualifier)

    def SetInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 256 and -100 <= value <= 12:
            cmdString = '{0} set inputLevel {1} {2}\n'.format(tag, chnl, value)
            self.__SetHelper('InputLevel', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('InputLevel', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 256:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get inputLevel (\d+)\r\n\+OK \"value\":([-\d.]+)\r\n'.format(tag).encode()), self.__MatchInputLevel, None)
            self.__UpdateHelper('InputLevel', '{0} get inputLevel {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLevel')

    def __MatchInputLevel(self, match, tag):

        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = int(float(match.group(3).decode()))
        self.WriteStatus('InputLevel', value, qualifier)

    def SetInputMute(self, value, qualifier):

        state = {
            'On': 'true',
            'Off': 'false',
        }
        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 256 and value in state:
            cmdString = '{0} set inputMute {1} {2}\n'.format(tag, chnl, state[value])
            self.__SetHelper('InputMute', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('InputMute', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 256:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get inputMute (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchInputMute, None)
            self.__UpdateHelper('InputMute', '{0} get inputMute {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def UpdateLastDialed(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        cmdTag = '{}_{}'.format('LastDialed', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2', 'None']:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get lastNum ?(\d+)?\r\n\+OK \"value\":(\"\"|\"[\S ]+\")\r\n'.format(tag).encode()), self.__MatchLastDialed, None)
            if line in ['1','2']:
                self.__UpdateHelper('LastDialed', '{0} get lastNum {1}\n'.format(tag, line), value, qualifier)
            else:
                self.__UpdateHelper('LastDialed', '{0} get lastNum\n'.format(tag), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLastDialed')

    def __MatchLastDialed(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        if match.group(2):
            qualifier['Line'] = match.group(2).decode()
        else:
            qualifier['Line'] = 'None'
        value = match.group(3).decode().replace('"','')
        self.WriteStatus('LastDialed', value, qualifier)

    def SetLevelControl(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 32 and -100 <= value <= 12:
            cmdString = '{0} set level {1} {2}\n'.format(tag, chnl, value)
            self.__SetHelper('LevelControl', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLevelControl')

    def UpdateLevelControl(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('LevelControl',tag)
        self._UpdateSubscribeHelper('LevelControl', 'levels', tag, label, qualifier)

    def SetLogicInputOutput(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 16 and value in ['True', 'False']:
            cmdString = '{0} set invert {1} {2}\n'.format(tag, chnl, value.lower())
            self.__SetHelper('LogicInputOutput', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogicInputOutput')

    def UpdateLogicInputOutput(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('LogicInputOutput', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 16:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append('LogicInputOutput')
                self.AddMatchString(compile('({0}) get invert (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchLogicInputOutput, None)
            self.__UpdateHelper('LogicInputOutput', '{0} get invert {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogicInputOutput')

    def __MatchLogicInputOutput(self, match, tag):
        state = {'true':'True','false':'False'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('LogicInputOutput', value, qualifier)

    def UpdateLogicMeter(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('LogicMeter',tag)
        self._UpdateSubscribeHelper('LogicMeter', 'states', tag, label, qualifier)

    def SetLogicState(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 32 and value in ['True', 'False']:
            cmdString = '{0} set state {1} {2}\n'.format(tag, chnl, value.lower())
            self.__SetHelper('LogicState', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogicState')

    def UpdateLogicState(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('LogicState', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 32:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get state (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchLogicState, None)
            self.__UpdateHelper('LogicState', '{0} get state {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogicState')

    def __MatchLogicState(self, match, tag):
        state = {'true':'True','false':'False'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('LogicState', value, qualifier)

    def SetMuteControl(self, value, qualifier):

        state = {
            'On': 'true',
            'Off': 'false',
        }
        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 32 and value in state:
            cmdString = '{0} set mute {1} {2}\n'.format(tag, chnl, state[value])
            self.__SetHelper('MuteControl', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMuteControl')

    def UpdateMuteControl(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('MuteControl',tag)
        self._UpdateSubscribeHelper('MuteControl', 'mutes', tag, label, qualifier)

    def SetNewSpeedDialEntryNameCommand(self, value, qualifier):

        name = value
        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        entry = qualifier['Entry']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2'] and 1 <= int(entry) <= 16:
            name = name.replace('"', '\\"')
            NewSpeedDialEntryNameCommandCmdString = '"{0}" set speedDialLabel {1} {2} "{3}"\n'.format(tag, line, entry, name)
            self.__SetHelper('NewSpeedDialEntryNameCommand', NewSpeedDialEntryNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNewSpeedDialEntryNameCommand')

    def SetNewSpeedDialEntryNumberCommand(self, value, qualifier):

        number = value
        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        entry = qualifier['Entry']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2'] and 1 <= int(entry) <= 16:
            number = number.replace('"', '\\"')
            NewSpeedDialEntryNumberCommandCmdString = '"{0}" set speedDialNum {1} {2} "{3}"\n'.format(tag, line, entry, number)
            self.__SetHelper('NewSpeedDialEntryNumberCommand', NewSpeedDialEntryNumberCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNewSpeedDialEntryNumberCommand')

    def SetOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 256 and -100 <= value <= 12:
            cmdString = '{0} set outputLevel {1} {2}\n'.format(tag, chnl, value)
            self.__SetHelper('OutputLevel', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('OutputLevel', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 256:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get outputLevel (\d+)\r\n\+OK \"value\":([-\d.]+)\r\n'.format(tag).encode()), self.__MatchOutputLevel, None)
            self.__UpdateHelper('OutputLevel', '{0} get outputLevel {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = int(float(match.group(3).decode()))
        self.WriteStatus('OutputLevel', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        state = {
            'On': 'true',
            'Off': 'false',
        }
        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 256 and value in state:
            cmdString = '{0} set outputMute {1} {2}\n'.format(tag, chnl, state[value])
            self.__SetHelper('OutputMute', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        cmdTag = '{}_{}'.format('OutputMute', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(chnl) <= 256:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get outputMute (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchOutputMute, None)
            self.__UpdateHelper('OutputMute', '{0} get outputMute {1}\n'.format(tag, chnl), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Channel'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def UpdateSpeedDialEntryName(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        entry = qualifier['Entry']
        cmdTag = '{}_{}'.format('SpeedDialEntryName',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2'] and 1 <= int(entry) <= 16:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get speedDialLabel (\d+) (\d+)\r\n\+OK \"value\":(\"\"|\"[\+\-\d\w. ]+\")\r\n'.format(tag).encode()), self.__MatchSpeedDialEntryName, None)
            SpeedDialEntryNameCmdString = '{0} get speedDialLabel {1} {2}\n'.format(tag, line, entry)
            self.__UpdateHelper('SpeedDialEntryName', SpeedDialEntryNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSpeedDialEntryName')

    def __MatchSpeedDialEntryName(self, match, tag):

        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Line'] = match.group(2).decode()
        qualifier['Entry'] = match.group(3).decode()
        value = match.group(4).decode().replace('"','')
        self.WriteStatus('SpeedDialEntryName', value, qualifier)

    def UpdateSpeedDialEntryNumber(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        entry = qualifier['Entry']
        cmdTag = '{}_{}'.format('SpeedDialEntryNumber',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2'] and 1 <= int(entry) <= 16:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get speedDialNum (\d+) (\d+)\r\n\+OK \"value\":(\"\"|\"[\+\-\d\w. ]+\")\r\n'.format(tag).encode()), self.__MatchSpeedDialEntryNumber, None)
            SpeedDialEntryNumberCmdString = '{0} get speedDialNum {1} {2}\n'.format(tag, line, entry)
            self.__UpdateHelper('SpeedDialEntryNumber', SpeedDialEntryNumberCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSpeedDialEntryNumber')

    def __MatchSpeedDialEntryNumber(self, match, tag):

        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Line'] = match.group(2).decode()
        qualifier['Entry'] = match.group(3).decode()
        value = match.group(4).decode().replace('"','')
        self.WriteStatus('SpeedDialEntryNumber', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            cmdString = 'DEVICE recallPreset {0}\n'.format(int(value) + 1000)
            self.__SetHelper('PresetRecall', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetRecallName(self, value, qualifier):

        name = qualifier['Name']
        if name:
            PresetRecallNameCmdString = 'DEVICE recallPresetByName {0}\n'.format(name)
            self.__SetHelper('PresetRecallName', PresetRecallNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecallName')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            PresetSaveCmdString = 'DEVICE savePreset {0}\n'.format(int(value) + 1000)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetPresetSaveName(self, value, qualifier):

        name = qualifier['Name']
        if name:
            PresetSaveNameCmdString = 'DEVICE savePresetByName {0}\n'.format(name)
            self.__SetHelper('PresetSaveName', PresetSaveNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSaveName')

    def SetRoomCombinerGroup(self, value, qualifier):

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32 and 0 <= int(value) <= 16:
            cmdString = '{0} set group {1} {2}\n'.format(tag, room, value)
            self.__SetHelper('RoomCombinerGroup', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomCombinerGroup')

    def UpdateRoomCombinerGroup(self, value, qualifier):

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        cmdTag = '{}_{}'.format('RoomCombinerGroup', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get group (\d+)\r\n\+OK \"value\":(\d+)\r\n'.format(tag).encode()), self.__MatchRoomCombinerGroup, None)
            self.__UpdateHelper('RoomCombinerGroup', '{0} get group {1}\n'.format(tag, room), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRoomCombinerGroup')

    def __MatchRoomCombinerGroup(self, match, tag):

        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Room'] = match.group(2).decode()
        value = match.group(3).decode()
        self.WriteStatus('RoomCombinerGroup', value, qualifier)

    def SetRoomCombinerInputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 12
        }

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(room) <= 32:
            RoomCombinerInputLevelCmdString = '{0} set levelIn {1} {2}\n'.format(tag, room, value)
            self.__SetHelper('RoomCombinerInputLevel', RoomCombinerInputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomCombinerInputLevel')

    def UpdateRoomCombinerInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        cmdTag = '{}_{}'.format('RoomCombinerInputLevel',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get levelIn (\d+)\r\n\+OK \"value\":([-\d.]+)\r\n'.format(tag).encode()), self.__MatchRoomCombinerInputLevel, None)
            RoomCombinerInputLevelCmdString = '{0} get levelIn {1}\n'.format(tag, room)
            self.__UpdateHelper('RoomCombinerInputLevel', RoomCombinerInputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRoomCombinerInputLevel')

    def __MatchRoomCombinerInputLevel(self, match, tag):

        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Room'] = match.group(2).decode()
        value = int(float(match.group(3).decode()))
        self.WriteStatus('RoomCombinerInputLevel', value, qualifier)

    def SetRoomCombinerInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32 and value in ValueStateValues:
            RoomCombinerInputMuteCmdString = '{0} set muteIn {1} {2}\n'.format(tag, room, ValueStateValues[value])
            self.__SetHelper('RoomCombinerInputMute', RoomCombinerInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomCombinerInputMute')

    def UpdateRoomCombinerInputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        cmdTag = '{}_{}'.format('RoomCombinerInputMute', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get muteIn (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchRoomCombinerInputMute, None)
            RoomCombinerInputMuteCmdString = '{0} get muteIn {1}\n'.format(tag, room)
            self.__UpdateHelper('RoomCombinerInputMute', RoomCombinerInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRoomCombinerInputMute')

    def __MatchRoomCombinerInputMute(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Room'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('RoomCombinerInputMute', value, qualifier)

    def SetRoomCombinerOutputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 12
        }

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(room) <= 32:
            RoomCombinerOutputLevelCmdString = '{0} set levelOut {1} {2}\n'.format(tag, room, value)
            self.__SetHelper('RoomCombinerOutputLevel', RoomCombinerOutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomCombinerOutputLevel')

    def UpdateRoomCombinerOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        label = '{0}_{1}_{2}'.format('RoomCombinerOutputLevel', tag, room)

        if 1 <= int(room) <= 32:
            self._UpdateSubscribeHelper('RoomCombinerOutputLevel', 'levelOut {0}'.format(room), tag, label, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRoomCombinerOutputLevel')

    def SetRoomCombinerOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32 and value in ValueStateValues:
            RoomCombinerOutputMuteCmdString = '{0} set muteOut {1} {2}\n'.format(tag, room, ValueStateValues[value])
            self.__SetHelper('RoomCombinerOutputMute', RoomCombinerOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomCombinerOutputMute')

    def UpdateRoomCombinerOutputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        cmdTag = '{}_{}'.format('RoomCombinerOutputMute', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get muteOut (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchRoomCombinerOutputMute, None)
            RoomCombinerOutputMuteCmdString = '{0} get muteOut {1}\n'.format(tag, room)
            self.__UpdateHelper('RoomCombinerOutputMute', RoomCombinerOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRoomCombinerOutputMute')

    def __MatchRoomCombinerOutputMute(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Room'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('RoomCombinerOutputMute', value, qualifier)

    def SetRoomCombinerSourceLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 12
        }

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(room) <= 32:
            RoomCombinerSourceLevelCmdString = '{0} set levelSource {1} {2}\n'.format(tag, room, value)
            self.__SetHelper('RoomCombinerSourceLevel', RoomCombinerSourceLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomCombinerSourceLevel')

    def UpdateRoomCombinerSourceLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        cmdTag = '{}_{}'.format('RoomCombinerSourceLevel', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get levelSource (\d+)\r\n\+OK \"value\":([-\d.]+)\r\n'.format(tag).encode()), self.__MatchRoomCombinerSourceLevel, None)
            RoomCombinerSourceLevelCmdString = '{0} get levelSource {1}\n'.format(tag, room)
            self.__UpdateHelper('RoomCombinerSourceLevel', RoomCombinerSourceLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRoomCombinerSourceLevel')

    def __MatchRoomCombinerSourceLevel(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Room'] = match.group(2).decode()
        value = int(float(match.group(3).decode()))
        self.WriteStatus('RoomCombinerSourceLevel', value, qualifier)

    def SetRoomCombinerSourceMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        room = qualifier['Room']
        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32 and value in ValueStateValues:
            RoomCombinerSourceMuteCmdString = '{0} set muteSource {1} {2}\n'.format(tag, room, ValueStateValues[value])
            self.__SetHelper('RoomCombinerSourceMute', RoomCombinerSourceMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomCombinerSourceMute')

    def UpdateRoomCombinerSourceMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        cmdTag = '{}_{}'.format('RoomCombinerSourceMute', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get muteSource (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchRoomCombinerSourceMute, None)
            RoomCombinerSourceMuteCmdString = '{0} get muteSource {1}\n'.format(tag, room)
            self.__UpdateHelper('RoomCombinerSourceMute', RoomCombinerSourceMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRoomCombinerSourceMute')

    def __MatchRoomCombinerSourceMute(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Room'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('RoomCombinerSourceMute', value, qualifier)

    def SetRoomCombinerSourceSelection(self, value, qualifier):

        ValueStateValues = {
            'No Source': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        room = qualifier['Room']
        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32 and value in ValueStateValues:
            RoomCombinerSourceSelectionCmdString = '{0} set sourceSelection {1} {2}\n'.format(tag, room, ValueStateValues[value])
            self.__SetHelper('RoomCombinerSourceSelection', RoomCombinerSourceSelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomCombinerSourceSelection')

    def UpdateRoomCombinerSourceSelection(self, value, qualifier):

        tag = qualifier['Instance Tag']
        room = qualifier['Room']
        cmdTag = '{}_{}'.format('RoomCombinerSourceSelection', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(room) <= 32:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get sourceSelection (\d+)\r\n\+OK \"value\":([\d]+)\r\n'.format(tag).encode()), self.__MatchRoomCombinerSourceSelection, None)
            RoomCombinerSourceSelectionCmdString = '{0} get sourceSelection {1}\n'.format(tag, room)
            self.__UpdateHelper('RoomCombinerSourceSelection', RoomCombinerSourceSelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRoomCombinerSourceSelection')

    def __MatchRoomCombinerSourceSelection(self, match, tag):
        state = {'0': 'No Source','1': '1','2': '2','3': '3','4': '4'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Room'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('RoomCombinerSourceSelection', value, qualifier)

    def SetRoomCombinerWall(self, value, qualifier):

        state = {
            'Close': 'true',
            'Open': 'false',
        }

        tag = qualifier['Instance Tag']
        wall = qualifier['Wall']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(wall) <= 46 and value in state:
            cmdString = '{0} set wallState {1} {2}\n'.format(tag, wall, state[value])
            self.__SetHelper('RoomCombinerWall', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomCombinerWall')

    def UpdateRoomCombinerWall(self, value, qualifier):

        tag = qualifier['Instance Tag']
        wall = qualifier['Wall']
        cmdTag = '{}_{}'.format('RoomCombinerWall', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(wall) <= 46:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get wallState (\d+)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchRoomCombinerWall, None)
            self.__UpdateHelper('RoomCombinerWall', '{0} get wallState {1}\n'.format(tag, wall), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRoomCombinerWall')

    def __MatchRoomCombinerWall(self, match, tag):
        state = {'true': 'Close','false': 'Open',}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Wall'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('RoomCombinerWall', value, qualifier)

    def SetRouterControl(self, value, qualifier):

        tag = qualifier['Instance Tag']
        Output = qualifier['Output']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(Output) <= 256 and 0 <= int(value) <= 256:
            cmdString = '{0} set input {1} {2}\n'.format(tag, Output, value)
            self.__SetHelper('RouterControl', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRouterControl')

    def UpdateRouterControl(self, value, qualifier):

        tag = qualifier['Instance Tag']
        Output = qualifier['Output']
        cmdTag = '{}_{}'.format('RouterControl', tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if 1 <= int(Output) <= 256:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get input (\d+)\r\n\+OK \"value\":([\d]+)\r\n'.format(tag).encode()), self.__MatchRouterControl, None)
            self.__UpdateHelper('RouterControl', '{0} get input {1}\n'.format(tag, Output), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRouterControl')

    def __MatchRouterControl(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Output'] = match.group(2).decode()
        value = match.group(3).decode()
        self.WriteStatus('RouterControl', value, qualifier)

    def UpdateSignalPresentMeter(self, value, qualifier):

        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        mtrName = qualifier['Meter Name']
        label = '{0}_{1}_{2}_{3}'.format('SignalPresentMeter', tag, chnl, mtrName)

        if 1 <= int(chnl) <= 32:
            self._UpdateSubscribeHelper('SignalPresentMeter', 'present {0}'.format(chnl), tag, label, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSignalPresentMeter')

    def SetSourceSelectorOutputLevel(self, value, qualifier):

        ValueConstraints = {'Min' : -100,'Max' : 12}
        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"'+tag+'\"'

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SourceSelectorOutputLevelCmdString = '{0} set outputLevel {1}\n'.format(tag, value)
            self.__SetHelper('SourceSelectorOutputLevel', SourceSelectorOutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSourceSelectorOutputLevel')

    def UpdateSourceSelectorOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('SourceSelectorOutputLevel', tag)
        self.UpdateSubscribeHelper('SourceSelectorOutputLevel', 'outputLevel', tag, label, qualifier)

    def SetSourceSelectorOutputMute(self, value, qualifier):

        ValueStateValues = {'On' : 'true', 'Off' : 'false'}
        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"'+tag+'\"'

        if value in ValueStateValues:
            SourceSelectorOutputMuteCmdString = '{0} set outputMute {1}\n'.format(tag, ValueStateValues[value])
            self.__SetHelper('SourceSelectorOutputMute', SourceSelectorOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSourceSelectorOutputMute')

    def UpdateSourceSelectorOutputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('SourceSelectorOutputMute', tag)
        if label not in self.MatchstringList:
            self.MatchstringList.append(label)
            self.AddMatchString(compile('\! "publishToken":"{0}" "value":(false|true)\r\n'.format(label).encode()), self.__MatchSourceSelectorOutputMute, tag)
        self.UpdateSubscribeHelper('SourceSelectorOutputMute', 'outputMute', tag, label, qualifier)

    def __MatchSourceSelectorOutputMute(self, match, tag):
        state = {'true':'On','false':'Off'}
        value = state[match.group(1).decode()]
        self.WriteStatus('SourceSelectorOutputMute', value, {'Instance Tag':tag})

    def SetSourceSelectorSourceSelection(self, value, qualifier):

        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if value == 'No Source' or 1 <= int(value) <= 32:
            if value == 'No Source':
                source = '0'
            else:
                source = value
            cmdString = '{0} set sourceSelection {1}\n'.format(tag, source)
            self.__SetHelper('SourceSelectorSourceSelection', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSourceSelectorSourceSelection')

    def UpdateSourceSelectorSourceSelection(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('SourceSelectorSourceSelection',tag)
        self._UpdateSubscribeHelper('SourceSelectorSourceSelection', 'sourceSelection', tag, label, qualifier)

    def SetSpeedDial(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        call = qualifier['Call Appearance']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2'] and 1 <= int(call) <= 6 and 1 <= int(value) <= 16:
            cmdString = '{0} speedDial {1} {2} {3}\n'.format(tag, line, call, value)
            self.__SetHelper('SpeedDial', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeedDial')

    def UpdateTICallerID(self, value, qualifier):

        self.UpdateTICallStatus(value, qualifier)

    def UpdateTICallStatus(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('TICallStatus',tag)
        self._UpdateSubscribeHelper('TICallStatus', 'callState', tag, label, qualifier)

    def SetTIHook(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        if ' ' in tag:
            tag = '\"'+tag+'\"'

        if line in ['1', '2', 'None']:
            if line in ['1', '2']:
                line = ' '+line
                call = ' 1'
            else:
                line = ''
                call = ''

            cmdString = ''
            if value in ['Redial', 'End', 'Flash', 'Answer']:
                cmdString = '{0} {1}{2}{3}\n'.format(tag, value.lower(), line, call)
            elif value in ['Off', 'On']:
                if line and call:
                    cmdString = '{0} {1}Hook{2}{3}\n'.format(tag, value.lower(), line, call)
                else:
                    cmdString = '{0} set hookState {1}HOOK\n'.format(tag, value.upper())
            elif value == 'Dial':
                number = qualifier['Number']
                if number:
                    cmdString = '{0} dial{1}{2} {3}\n'.format(tag, line, call, number)

            if cmdString:
                self.__SetHelper('TIHook', cmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetTIHook')
        else:
            self.Discard('Invalid Command for SetTIHook')

    def UpdateTILineInUse(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('TILineInUse',tag)
        self._UpdateSubscribeHelper('TILineInUse', 'lineInUse', tag, label, qualifier)

    def SetTIReceiveLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if -100 <= value <= 12:
            cmdString = '{0} set level {1}\n'.format(tag, value)
            self.__SetHelper('TIReceiveLevel', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTIReceiveLevel')

    def UpdateTIReceiveLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        cmdTag = '{}_{}'.format('TIReceiveLevel',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if cmdTag not in self.MatchstringList:
            self.MatchstringList.append(cmdTag)
            self.AddMatchString(compile('({0}) get level\r\n\+OK \"value\":([-\d\.]+)\r\n'.format(tag).encode()), self.__MatchTIReceiveLevel, None)
        self.__UpdateHelper('TIReceiveLevel', '{0} get level\n'.format(tag), value, qualifier)

    def __MatchTIReceiveLevel(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        value = int(float(match.group(2).decode()))
        self.WriteStatus('TIReceiveLevel', value, qualifier)

    def SetTIReceiveMute(self, value, qualifier):

        state = {
            'On': 'true',
            'Off': 'false',
        }
        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if value in state:
            cmdString = '{0} set mute {1}\n'.format(tag, state[value])
            self.__SetHelper('TIReceiveMute', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTIReceiveMute')

    def UpdateTIReceiveMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        cmdTag = '{}_{}'.format('TIReceiveMute',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if cmdTag not in self.MatchstringList:
            self.MatchstringList.append(cmdTag)
            self.AddMatchString(compile('({0}) get mute\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchTIReceiveMute, None)
        self.__UpdateHelper('TIReceiveMute', '{0} get mute\n'.format(tag), value, qualifier)

    def __MatchTIReceiveMute(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        value = state[match.group(2).decode()]
        self.WriteStatus('TIReceiveMute', value, qualifier)

    def SetTITransmitLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if -100 <= value <= 0:
            cmdString = '{0} set level {1}\n'.format(tag, value)
            self.__SetHelper('TITransmitLevel', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTITransmitLevel')

    def UpdateTITransmitLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        cmdTag = '{}_{}'.format('TITransmitLevel',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if cmdTag not in self.MatchstringList:
            self.MatchstringList.append(cmdTag)
            self.AddMatchString(compile('({0}) get level\r\n\+OK \"value\":([-\d\.]+)\r\n'.format(tag).encode()), self.__MatchTITransmitLevel, None)
        self.__UpdateHelper('TITransmitLevel', '{0} get level\n'.format(tag), value, qualifier)

    def __MatchTITransmitLevel(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        value = int(float(match.group(2).decode()))
        self.WriteStatus('TITransmitLevel', value, qualifier)

    def SetTITransmitMute(self, value, qualifier):

        state = {
            'On': 'true',
            'Off': 'false',
        }
        tag = qualifier['Instance Tag']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if value in state:
            cmdString = '{0} set mute {1}\n'.format(tag, state[value])
            self.__SetHelper('TITransmitMute', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTITransmitMute')

    def UpdateTITransmitMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        cmdTag = '{}_{}'.format('TITransmitMute',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if cmdTag not in self.MatchstringList:
            self.MatchstringList.append(cmdTag)
            self.AddMatchString(compile('({0}) get mute\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchTITransmitMute, None)
        self.__UpdateHelper('TITransmitMute', '{0} get mute\n'.format(tag), value, qualifier)

    def __MatchTITransmitMute(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        value = state[match.group(2).decode()]
        self.WriteStatus('TITransmitMute', value, qualifier)

    def UpdateVerboseMode(self, value, qualifier):

        self.__UpdateHelper('VerboseMode', 'SESSION get verbose\n', value, qualifier)

    def UpdateVoIPCallerID(self, value, qualifier):

        self.UpdateVoIPCallStatus(value, qualifier)

    def UpdateVoIPCallStatus(self, value, qualifier):

        tag = qualifier['Instance Tag']
        label = '{0}_{1}'.format('VoIPCallStatus',tag)
        self._UpdateSubscribeHelper('VoIPCallStatus', 'callState', tag, label, qualifier)

    def SetVoIPHook(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        call = qualifier['Call Appearance']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2'] and 1 <= int(call) <= 6:
            cmdString = ''
            if value in ['Redial', 'End', 'Flash', 'Send', 'Answer', 'Resume', 'Hold', 'Transfer']:
                cmdString = '{0} {1} {2} {3}\n'.format(tag, value.lower(), line, call)
            elif value in ['Off', 'On']:
                cmdString = '{0} {1}Hook {2} {3}\n'.format(tag, value.lower(), line, call)
            elif value == 'Dial':
                number = qualifier['Number']
                if number:
                    cmdString = '{0} dial {1} {2} {3}\n'.format(tag, line, call, number)
            elif value == 'Conference':
                cmdString = '{0} lconf {1} {2}\n'.format(tag, line, call)
            elif value == 'Leave Conference':
                cmdString = '{0} leaveConf {1} {2}\n'.format(tag, line, call)
            if cmdString:
                self.__SetHelper('VoIPHook', cmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVoIPHook')
        else:
            self.Discard('Invalid Command for SetVoIPHook')

    def UpdateVoIPLineInUse(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        call = qualifier['Call Appearance']
        label = '{0}_{1}_{2}_{3}'.format('VoIPLineInUse', tag, line, call)

        if line in ['1', '2'] and 1 <= int(call) <= 6:
            self._UpdateSubscribeHelper('VoIPLineInUse', 'lineInUse {0} {1}'.format(line, call), tag, label, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVoIPLineInUse')

    def SetVoIPReceiveLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2'] and -100 <= value <= 12:
            cmdString = '{0} set level {1} {2}\n'.format(tag, line, value)
            self.__SetHelper('VoIPReceiveLevel', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoIPReceiveLevel')

    def UpdateVoIPReceiveLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        cmdTag = '{}_{}'.format('VoIPReceiveLevel',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2']:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get level (\d)\r\n\+OK \"value\":([-\d\.]+)\r\n'.format(tag).encode()), self.__MatchVoIPReceiveLevel, None)
            self.__UpdateHelper('VoIPReceiveLevel', '{0} get level {1}\n'.format(tag, line), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVoIPReceiveLevel')

    def __MatchVoIPReceiveLevel(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Line'] = match.group(2).decode()
        value = int(float(match.group(3).decode()))
        self.WriteStatus('VoIPReceiveLevel', value, qualifier)

    def SetVoIPReceiveMute(self, value, qualifier):

        state = {
            'On': 'true',
            'Off': 'false',
        }
        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2'] and value in state:
            cmdString = '{0} set mute {1} {2}\n'.format(tag, line, state[value])
            self.__SetHelper('VoIPReceiveMute', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoIPReceiveMute')

    def UpdateVoIPReceiveMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        cmdTag = '{}_{}'.format('VoIPReceiveMute',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2']:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get mute (\d)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchVoIPReceiveMute, None)
            self.__UpdateHelper('VoIPReceiveMute', '{0} get mute {1}\n'.format(tag, line), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVoIPReceiveMute')

    def __MatchVoIPReceiveMute(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Line'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('VoIPReceiveMute', value, qualifier)

    def SetVoIPTransmitLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2'] and -100 <= value <= 0:
            cmdString = '{0} set level {1} {2}\n'.format(tag, line, value)
            self.__SetHelper('VoIPTransmitLevel', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoIPTransmitLevel')

    def UpdateVoIPTransmitLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        cmdTag = '{}_{}'.format('VoIPTransmitLevel',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2']:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get level (\d)\r\n\+OK \"value\":([-\d\.]+)\r\n'.format(tag).encode()), self.__MatchVoIPTransmitLevel, None)
            self.__UpdateHelper('VoIPTransmitLevel', '{0} get level {1}\n'.format(tag, line), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVoIPTransmitLevel')

    def __MatchVoIPTransmitLevel(self, match, tag):
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Line'] = match.group(2).decode()
        value = int(float(match.group(3).decode()))
        self.WriteStatus('VoIPTransmitLevel', value, qualifier)

    def SetVoIPTransmitMute(self, value, qualifier):

        state = {'On': 'true','Off': 'false',}
        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2'] and value in state:
            cmdString = '{0} set mute {1} {2}\n'.format(tag, line, state[value])
            self.__SetHelper('VoIPTransmitMute', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoIPTransmitMute')

    def UpdateVoIPTransmitMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        line = qualifier['Line']
        cmdTag = '{}_{}'.format('VoIPTransmitMute',tag)
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if line in ['1', '2']:
            if cmdTag not in self.MatchstringList:
                self.MatchstringList.append(cmdTag)
                self.AddMatchString(compile('({0}) get mute (\d)\r\n\+OK \"value\":(true|false)\r\n'.format(tag).encode()), self.__MatchVoIPTransmitMute, None)
            self.__UpdateHelper('VoIPTransmitMute', '{0} get mute {1}\n'.format(tag, line), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVoIPTransmitMute')

    def __MatchVoIPTransmitMute(self, match, tag):
        state = {'true':'On','false':'Off'}
        qualifier = {}
        qualifier['Instance Tag'] = match.group(1).decode()
        qualifier['Line'] = match.group(2).decode()
        value = state[match.group(3).decode()]
        self.WriteStatus('VoIPTransmitMute', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.VerboseDisabled and self.Unidirectional == 'False':
            @Wait(1)
            def SendVerbose():
                if self.VerboseDisabled:
                    self.Send('SESSION set verbose true\n')
                self.Send(commandstring)
        else:
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

            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    if self.VerboseDisabled:
                        self.Send('SESSION set verbose true\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def _UpdateSubscribeHelper(self, command, commandstring, tag, label, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    if self.VerboseDisabled:
                        self.Send('SESSION set verbose true\n')
                    if label not in self.InitialStatusList:
                        self.InitialStatusList.append(label)

                        unsubscribe = '"{0}" unsubscribe {1} "{2}"\n'.format(tag, commandstring, label)
                        self.Send(unsubscribe)

                    subscribe = '"{0}" subscribe {1} "{2}" {3}\n'.format(tag, commandstring, label, self.SUBSCRIPTION_RESPONSE_TIME)
                    self.Send(subscribe)
            else:
                if label not in self.InitialStatusList:
                    self.InitialStatusList.append(label)

                    unsubscribe = '"{0}" unsubscribe {1} "{2}"\n'.format(tag, commandstring, label)
                    self.Send(unsubscribe)

                subscribe = '"{0}" subscribe {1} "{2}" {3}\n'.format(tag, commandstring, label, self.SUBSCRIPTION_RESPONSE_TIME)
                self.Send(subscribe)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.InitialStatusList.clear()
        self.VerboseDisabled = True

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')

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
        if not self.connectionFlag and command != 'ConnectionStatus': 
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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        # check incoming data if it matched any expected data from device module
        tempList = copy.copy(self.__matchStringDict)
        for regexString, CurrentMatch in tempList.items():
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

class SerialClass(SerialInterface, DeviceClass):
    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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
