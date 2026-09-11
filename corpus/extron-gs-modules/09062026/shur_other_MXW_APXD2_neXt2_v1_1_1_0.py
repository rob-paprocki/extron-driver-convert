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
            'AudioGain': {'Parameters':['Channel'], 'Status': {}},
            'AutomixerOutMute': { 'Status': {}},
            'BodypackInputSource': {'Parameters':['Channel'], 'Status': {}},
            'BodypackInternalMicrophoneGain': {'Parameters':['Channel'], 'Status': {}},
            'DeviceID': { 'Status': {}},
            'DeviceModel': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'InputChannelGain': {'Parameters':['Channel'], 'Status': {}},
            'MicrophoneButtonStatus': {'Parameters':['Channel'], 'Status': {}},
            'OutputChannelGain': {'Parameters':['Channel'], 'Status': {}},
            'OutputChannelMute': {'Parameters':['Channel'], 'Status': {}},
            'SerialNumber': { 'Status': {}},
            'SystemOperationMode': { 'Status': {}},
            'TransmitterAvailable': {'Parameters':['Channel','Type'], 'Status': {}},
            'TransmitterBatteryCharge': {'Parameters':['Channel'], 'Status': {}},
            'TransmitterBatteryHealth': {'Parameters':['Channel'], 'Status': {}},
            'TransmitterBatteryRunTime': {'Parameters':['Channel'], 'Status': {}},
            'TransmitterBatteryTimetoFull': {'Parameters':['Channel'], 'Status': {}},
            'TransmitterDeviceID': {'Parameters':['Channel','Type'], 'Status': {}},
            'TransmitterModel': {'Parameters':['Channel','Type'], 'Status': {}},
            'TransmitterStatus': {'Parameters':['Channel','Type'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP (\d{1,2}) AUDIO_GAIN (\d{3}) >'), self.__MatchAudioGain, None)
            self.AddMatchString(re.compile(b'< REP AUTOMIX_OUT_MUTE (MUTED|ACTIVE) >'), self.__MatchAutomixerOutMute, None)
            self.AddMatchString(re.compile(b'< REP ([12]) BP_MIC_SELECT (INT|EXT|AUTO|ERR|UNKNOWN) >'), self.__MatchBodypackInputSource, None)
            self.AddMatchString(re.compile(b'< REP ([12]) INT_AUDIO_GAIN (\d{1,3}) >'), self.__MatchBodypackInternalMicrophoneGain, None)
            self.AddMatchString(re.compile(b'< REP DEVICE_ID {(.*)} >'), self.__MatchDeviceID, None)
            self.AddMatchString(re.compile(b'< REP DEVICE_MODEL {(.*)} >'), self.__MatchDeviceModel, None)
            self.AddMatchString(re.compile(b'< REP FW_VER {(.*)} >'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'< REP (\d{1,2}) INPUT_CH_GAIN (\d{1,4}) >'), self.__MatchInputChannelGain, None)
            self.AddMatchString(re.compile(b'< REP ([12]) BUTTON_STS (ON|OFF) >'), self.__MatchMicrophoneButtonStatus, None)
            self.AddMatchString(re.compile(b'< REP (\d{1,2}) OUTPUT_CH_GAIN (\d{1,4}) >'), self.__MatchOutputChannelGain, None)
            self.AddMatchString(re.compile(b'< REP (\d{1,2}) OUTPUT_CH_MUTE (MUTED|ACTIVE) >'), self.__MatchOutputChannelMute, None)
            self.AddMatchString(re.compile(b'< REP SERIAL_NUM {(.*)} >'), self.__MatchSerialNumber, None)
            self.AddMatchString(re.compile(b'< REP SYSTEM_OPERATION_MODE (PRESENTATION|CONFERENCE|DIRECT|CUSTOM) >'), self.__MatchSystemOperationMode, None)
            self.AddMatchString(re.compile(b'< REP (BAY|CH) ([12]) TX_AVAILABLE (YES|NO) >'), self.__MatchTransmitterAvailable, None)
            self.AddMatchString(re.compile(b'< REP ([12]) BATT_CHARGE (\d{1,3}) >'), self.__MatchTransmitterBatteryCharge, None)
            self.AddMatchString(re.compile(b'< REP ([12]) BATT_HEALTH (\d{1,3}) >'), self.__MatchTransmitterBatteryHealth, None)
            self.AddMatchString(re.compile(b'< REP ([1,2]) BATT_RUN_TIME (\d{1,5}) >'), self.__MatchTransmitterBatteryRunTime, None)
            self.AddMatchString(re.compile(b'< REP ([1,2]) BATT_TIME_TO_FULL (\d{1,5}) >'), self.__MatchTransmitterBatteryTimetoFull, None)
            self.AddMatchString(re.compile(b'< REP (BAY|CH) ([12]) TX_DEVICE_ID {?(.*?)}? >'), self.__MatchTransmitterDeviceID, None)
            self.AddMatchString(re.compile(b'< REP (BAY|CH) ([12]) TX_MODEL {?(MXW[1268]X|UNKNOWN)}? >'), self.__MatchTransmitterModel, None)
            self.AddMatchString(re.compile(b'< REP (BAY|CH) ([12]) TX_STATUS (ACTIVE|MUTED|ON_CHARGER|UNKNOWN) >'), self.__MatchTransmitterStatus, None)
            self.AddMatchString(re.compile(b'< REP ERR >'), self.__MatchError, None)

    def SetAudioGain(self, value, qualifier):

        ChannelStates = {
            'Dante 1': '1',
            'Dante 2': '2',
            'Dante 3': '3',
            'Dante 4': '4',
            'Dante 5': '5',
            'Dante 6': '6',
            'Dante 7': '7',
            'Dante 8': '8',
            'Dante 9': '9',
            'Dante 10': '10',
            'Dante 11': '11',
            'Dante 12': '12',
            'Dante 13': '13',
            'Dante 14': '14',
            'Dante 15': '15',
            'Dante 16': '16',
            'Dante 17': '17',
            'Dante 18': '18',
            'Dante 19': '19',
            'Mic 1': '21',
            'Mic 2': '22',
            'Analog': '41',
            'USB': '51'
        }

        if qualifier['Channel'] in ChannelStates and -25 <= value <= 15:
            gain = value + 25
            AudioGainCmdString = '< SET {0} AUDIO_GAIN {1} >'.format(ChannelStates[qualifier['Channel']], str(gain).zfill(3))
            self.__SetHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):

        ChannelStates = {
            'Dante 1': '1',
            'Dante 2': '2',
            'Dante 3': '3',
            'Dante 4': '4',
            'Dante 5': '5',
            'Dante 6': '6',
            'Dante 7': '7',
            'Dante 8': '8',
            'Dante 9': '9',
            'Dante 10': '10',
            'Dante 11': '11',
            'Dante 12': '12',
            'Dante 13': '13',
            'Dante 14': '14',
            'Dante 15': '15',
            'Dante 16': '16',
            'Dante 17': '17',
            'Dante 18': '18',
            'Dante 19': '19',
            'Mic 1': '21',
            'Mic 2': '22',
            'Analog': '41',
            'USB': '51'
        }

        if qualifier['Channel'] in ChannelStates:
            AudioGainCmdString = '< GET {0} AUDIO_GAIN >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGain')

    def __MatchAudioGain(self, match, tag):

        ChannelStates = {
            '1': 'Dante 1',
            '2': 'Dante 2',
            '3': 'Dante 3',
            '4': 'Dante 4',
            '5': 'Dante 5',
            '6': 'Dante 6',
            '7': 'Dante 7',
            '8': 'Dante 8',
            '9': 'Dante 9',
            '10': 'Dante 10',
            '11': 'Dante 11',
            '12': 'Dante 12',
            '13': 'Dante 13',
            '14': 'Dante 14',
            '15': 'Dante 15',
            '16': 'Dante 16',
            '17': 'Dante 17',
            '18': 'Dante 18',
            '19': 'Dante 19',
            '21': 'Mic 1',
            '22': 'Mic 2',
            '41': 'Analog',
            '51': 'USB'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = int(match.group(2)) - 25
        if -25 <= value <= 15:
            self.WriteStatus('AudioGain', value, qualifier)

    def SetAutomixerOutMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'MUTED',
            'Off' : 'ACTIVE'
        }

        if value in ValueStateValues:
            AutomixerOutMuteCmdString = '< SET AUTOMIX_OUT_MUTE {} >'.format(ValueStateValues[value])
            self.__SetHelper('AutomixerOutMute', AutomixerOutMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomixerOutMute')

    def UpdateAutomixerOutMute(self, value, qualifier):

        AutomixerOutMuteCmdString = '< GET AUTOMIX_OUT_MUTE >'
        self.__UpdateHelper('AutomixerOutMute', AutomixerOutMuteCmdString, value, qualifier)

    def __MatchAutomixerOutMute(self, match, tag):

        ValueStateValues = {
            'MUTED'  : 'On',
            'ACTIVE' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutomixerOutMute', value, None)

    def UpdateBodypackInputSource(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 2:
            BodypackInputSourceCmdString = '< GET {0} BP_MIC_SELECT >'.format(qualifier['Channel'])
            self.__UpdateHelper('BodypackInputSource', BodypackInputSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBodypackInputSource')

    def __MatchBodypackInputSource(self, match, tag):

        ValueStateValues = {
            'INT'   : 'Internal',
            'EXT'   : 'External',
            'AUTO'  : 'Auto',
            'ERR'   : 'Error',
            'UNKNOWN': 'Unknown'
        }

        qualifier = {'Channel' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('BodypackInputSource', value, qualifier)

    def SetBodypackInternalMicrophoneGain(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 2 and -25 <= value <= 35:
            gain = value + 25
            BodypackInternalMicrophoneGainCmdString = '< SET {0} INT_AUDIO_GAIN {1} >'.format(qualifier['Channel'], str(gain).zfill(3))
            self.__SetHelper('BodypackInternalMicrophoneGain', BodypackInternalMicrophoneGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBodypackInternalMicrophoneGain')

    def UpdateBodypackInternalMicrophoneGain(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 2:
            BodypackInternalMicrophoneGainCmdString = '< GET {0} INT_AUDIO_GAIN >'.format(qualifier['Channel'])
            self.__UpdateHelper('BodypackInternalMicrophoneGain', BodypackInternalMicrophoneGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBodypackInternalMicrophoneGain')

    def __MatchBodypackInternalMicrophoneGain(self, match, tag):

        qualifier = {'Channel' : match.group(1).decode()}
        value = int(match.group(2).decode()) - 25
        if -25 <= value <= 35:
            self.WriteStatus('BodypackInternalMicrophoneGain', value, qualifier)

    def UpdateDeviceID(self, value, qualifier):

        DeviceIDCmdString = '< GET DEVICE_ID >'
        self.__UpdateHelper('DeviceID', DeviceIDCmdString, value, qualifier)

    def __MatchDeviceID(self, match, tag):

        value = match.group(1).decode().strip()
        self.WriteStatus('DeviceID', value, None)

    def UpdateDeviceModel(self, value, qualifier):

        DeviceModelCmdString = '< GET DEVICE_MODEL >'
        self.__UpdateHelper('DeviceModel', DeviceModelCmdString, value, qualifier)

    def __MatchDeviceModel(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceModel', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '< GET FW_VER >'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        if '*' in value:
            value = 'FAILED'
        self.WriteStatus('FirmwareVersion', value, None)

    def SetInputChannelGain(self, value, qualifier):

        ChannelStates = {
            'Dante 1'   : '1',
            'Dante 2'   : '2',
            'Dante 3'   : '3',
            'Dante 4'   : '4',
            'Dante 5'   : '5',
            'Dante 6'   : '6',
            'Dante 7'   : '7',
            'Dante 8'   : '8',
            'Dante 9'   : '9',
            'Dante 10'  : '10',
            'Dante 11'  : '11',
            'Dante 12'  : '12',
            'Dante 13'  : '13',
            'Dante 14'  : '14',
            'Dante 15'  : '15',
            'Dante 16'  : '16',
            'Dante 17'  : '17',
            'Dante 18'  : '18',
            'Dante 19'  : '19',
            'Mic 1'     : '21',
            'Mic 2'     : '22',
            'Analog'    : '41',
            'USB'       : '51'
        }

        if qualifier['Channel'] in ChannelStates and -110.0 <= value <= 30.0:
            gain = int(value * 10 + 1100)
            InputChannelGainCmdString = '< SET {0} INPUT_CH_GAIN {1} >'.format(ChannelStates[qualifier['Channel']], gain)
            self.__SetHelper('InputChannelGain', InputChannelGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputChannelGain')

    def UpdateInputChannelGain(self, value, qualifier):

        ChannelStates = {
            'Dante 1'   : '1',
            'Dante 2'   : '2',
            'Dante 3'   : '3',
            'Dante 4'   : '4',
            'Dante 5'   : '5',
            'Dante 6'   : '6',
            'Dante 7'   : '7',
            'Dante 8'   : '8',
            'Dante 9'   : '9',
            'Dante 10'  : '10',
            'Dante 11'  : '11',
            'Dante 12'  : '12',
            'Dante 13'  : '13',
            'Dante 14'  : '14',
            'Dante 15'  : '15',
            'Dante 16'  : '16',
            'Dante 17'  : '17',
            'Dante 18'  : '18',
            'Dante 19'  : '19',
            'Mic 1'     : '21',
            'Mic 2'     : '22',
            'Analog'    : '41',
            'USB'       : '51'
        }

        if qualifier['Channel'] in ChannelStates:
            InputChannelGainCmdString = '< GET {} INPUT_CH_GAIN >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('InputChannelGain', InputChannelGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputChannelGain')

    def __MatchInputChannelGain(self, match, tag):

        ChannelStates = {
            '1'  : 'Dante 1',
            '2'  : 'Dante 2',
            '3'  : 'Dante 3',
            '4'  : 'Dante 4',
            '5'  : 'Dante 5',
            '6'  : 'Dante 6',
            '7'  : 'Dante 7',
            '8'  : 'Dante 8',
            '9'  : 'Dante 9',
            '10' : 'Dante 10',
            '11' : 'Dante 11',
            '12' : 'Dante 12',
            '13' : 'Dante 13',
            '14' : 'Dante 14',
            '15' : 'Dante 15',
            '16' : 'Dante 16',
            '17' : 'Dante 17',
            '18' : 'Dante 18',
            '19' : 'Dante 19',
            '21' : 'Mic 1',
            '22' : 'Mic 2',
            '41' : 'Analog',
            '51' : 'USB'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = (int(match.group(2)) - 1100) / 10
        if -110.0 <= value <= 30.0:
            self.WriteStatus('InputChannelGain', value, qualifier)

    def UpdateMicrophoneButtonStatus(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 2:
            MicrophoneButtonStatusCmdString = '< GET {0} BUTTON_STS >'.format(qualifier['Channel'])
            self.__UpdateHelper('MicrophoneButtonStatus', MicrophoneButtonStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicrophoneButtonStatus')

    def __MatchMicrophoneButtonStatus(self, match, tag):

        qualifier = {'Channel' : match.group(1).decode()}
        value = match.group(2).decode().title()
        self.WriteStatus('MicrophoneButtonStatus', value, qualifier)

    def SetOutputChannelGain(self, value, qualifier):

        ChannelStates = {
            'Dante 1'       : '1',
            'Dante 2'       : '2',
            'Dante 3'       : '3',
            'Dante 4'       : '4',
            'Analog 1'      : '41',
            'Analog 2'      : '42',
            'USB'           : '51',
            'Back Channel'  : '61'
        }

        if qualifier['Channel'] in ChannelStates and -110.0 <= value <= 30.0:
            gain = int(value * 10 + 1100)
            OutputChannelGainCmdString = '< SET {0} OUTPUT_CH_GAIN {1} >'.format(ChannelStates[qualifier['Channel']], gain)
            self.__SetHelper('OutputChannelGain', OutputChannelGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputChannelGain')

    def UpdateOutputChannelGain(self, value, qualifier):

        ChannelStates = {
            'Dante 1'       : '1',
            'Dante 2'       : '2',
            'Dante 3'       : '3',
            'Dante 4'       : '4',
            'Analog 1'      : '41',
            'Analog 2'      : '42',
            'USB'           : '51',
            'Back Channel'  : '61'
        }

        if qualifier['Channel'] in ChannelStates:
            OutputChannelGainCmdString = '< GET {0} OUTPUT_CH_GAIN >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('OutputChannelGain', OutputChannelGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputChannelGain')

    def __MatchOutputChannelGain(self, match, tag):

        ChannelStates = {
            '1'  : 'Dante 1',
            '2'  : 'Dante 2',
            '3'  : 'Dante 3',
            '4'  : 'Dante 4',
            '41' : 'Analog 1',
            '42' : 'Analog 2',
            '51' : 'USB',
            '61' : 'Back Channel'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = (int(match.group(2)) - 1100) / 10
        if -110.0 <= value <= 30.0:
            self.WriteStatus('OutputChannelGain', value, qualifier)

    def SetOutputChannelMute(self, value, qualifier):

        ChannelStates = {
            'Dante 1'       : '1',
            'Dante 2'       : '2',
            'Dante 3'       : '3',
            'Dante 4'       : '4',
            'Analog 1'      : '41',
            'Analog 2'      : '42',
            'USB'           : '51',
            'Back Channel'  : '61'
        }

        ValueStateValues = {
            'On'  : 'MUTED',
            'Off' : 'ACTIVE'
        }

        if qualifier['Channel'] in ChannelStates and value in ValueStateValues:
            OutputChannelMuteCmdString = '< SET {0} OUTPUT_CH_MUTE {1} >'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('OutputChannelMute', OutputChannelMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputChannelMute')

    def UpdateOutputChannelMute(self, value, qualifier):

        ChannelStates = {
            'Dante 1'       : '1',
            'Dante 2'       : '2',
            'Dante 3'       : '3',
            'Dante 4'       : '4',
            'Analog 1'      : '41',
            'Analog 2'      : '42',
            'USB'           : '51',
            'Back Channel'  : '61'
        }

        if qualifier['Channel'] in ChannelStates:
            OutputChannelMuteCmdString = '< GET {0} OUTPUT_CH_MUTE >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('OutputChannelMute', OutputChannelMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputChannelMute')

    def __MatchOutputChannelMute(self, match, tag):

        ChannelStates = {
            '1'  : 'Dante 1',
            '2'  : 'Dante 2',
            '3'  : 'Dante 3',
            '4'  : 'Dante 4',
            '41' : 'Analog 1',
            '42' : 'Analog 2',
            '51' : 'USB',
            '61' : 'Back Channel'
        }

        ValueStateValues = {
            'MUTED'  : 'On',
            'ACTIVE' : 'Off'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputChannelMute', value, qualifier)

    def UpdateSerialNumber(self, value, qualifier):

        SerialNumberCmdString = '< GET SERIAL_NUM >'
        self.__UpdateHelper('SerialNumber', SerialNumberCmdString, value, qualifier)

    def __MatchSerialNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SerialNumber', value, None)

    def SetSystemOperationMode(self, value, qualifier):

        ValueStateValues = ['Presentation', 'Conference', 'Direct', 'Custom']

        if value in ValueStateValues:
            SystemOperationModeCmdString = '< SET SYSTEM_OPERATION_MODE {} >'.format(value.upper())
            self.__SetHelper('SystemOperationMode', SystemOperationModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSystemOperationMode')

    def UpdateSystemOperationMode(self, value, qualifier):

        SystemOperationModeCmdString = '< GET SYSTEM_OPERATION_MODE >'
        self.__UpdateHelper('SystemOperationMode', SystemOperationModeCmdString, value, qualifier)

    def __MatchSystemOperationMode(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('SystemOperationMode', value, None)

    def UpdateTransmitterAvailable(self, value, qualifier):

        TypeStates = {
            'Docking Bay' : 'BAY',
            'Channel' : 'CH'
        }

        if 1 <= int(qualifier['Channel']) <= 2 and qualifier['Type'] in TypeStates:
            TransmitterAvailableCmdString = '< GET {0} {1} TX_AVAILABLE >'.format(TypeStates[qualifier['Type']], qualifier['Channel'])
            self.__UpdateHelper('TransmitterAvailable', TransmitterAvailableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterAvailable')

    def __MatchTransmitterAvailable(self, match, tag):

        TypeStates = {
            'BAY' : 'Docking Bay',
            'CH' : 'Channel'
        }
        
        qualifier = {
            'Channel' : match.group(2).decode(),
            'Type' : TypeStates[match.group(1).decode()]
        }
        
        value = match.group(3).decode().title()
        self.WriteStatus('TransmitterAvailable', value, qualifier)

    def UpdateTransmitterBatteryCharge(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 2:
            TransmitterBatteryChargeCmdString = '< GET {0} BATT_CHARGE >'.format(qualifier['Channel'])
            self.__UpdateHelper('TransmitterBatteryCharge', TransmitterBatteryChargeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterBatteryCharge')

    def __MatchTransmitterBatteryCharge(self, match, tag):

        qualifier = {'Channel' : match.group(1).decode()}
        value = int(match.group(2).decode())
        if 0 <= value <= 100:
            self.WriteStatus('TransmitterBatteryCharge', value, qualifier)

    def UpdateTransmitterBatteryHealth(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 2:
            TransmitterBatteryHealthCmdString = '< GET {0} BATT_HEALTH >'.format(qualifier['Channel'])
            self.__UpdateHelper('TransmitterBatteryHealth', TransmitterBatteryHealthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterBatteryHealth')

    def __MatchTransmitterBatteryHealth(self, match, tag):

        qualifier = {'Channel' : match.group(1).decode()}
        value = int(match.group(2).decode())
        if 0 <= value <= 100:
            self.WriteStatus('TransmitterBatteryHealth', value, qualifier)

    def UpdateTransmitterBatteryRunTime(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 2:
            TransmitterBatteryRunTimeCmdString = '< GET {0} BATT_RUN_TIME >'.format(qualifier['Channel'])
            self.__UpdateHelper('TransmitterBatteryRunTime', TransmitterBatteryRunTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterBatteryRunTime')

    def __MatchTransmitterBatteryRunTime(self, match, tag):

        qualifier = {'Channel' : match.group(1).decode()}
        value = int(match.group(2).decode())
        if 0 <= value <= 65535:
            self.WriteStatus('TransmitterBatteryRunTime', value, qualifier)

    def UpdateTransmitterBatteryTimetoFull(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 2:
            TransmitterBatteryTimetoFullCmdString = '< GET {0} BATT_TIME_TO_FULL >'.format(qualifier['Channel'])
            self.__UpdateHelper('TransmitterBatteryTimetoFull', TransmitterBatteryTimetoFullCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterBatteryTimetoFull')

    def __MatchTransmitterBatteryTimetoFull(self, match, tag):

        qualifier = {'Channel' : match.group(1).decode()}
        value = int(match.group(2).decode())
        if 0 <= value <= 65535:
            self.WriteStatus('TransmitterBatteryTimetoFull', value, qualifier)

    def UpdateTransmitterDeviceID(self, value, qualifier):

        TypeStates = {
            'Docking Bay' : 'BAY',
            'Channel'     : 'CH'
        }

        if qualifier['Channel'] in ['1', '2'] and qualifier['Type'] in TypeStates:
            TransmitterDeviceIDCmdString = '< GET {} 0 TX_DEVICE_ID >'.format(TypeStates[qualifier['Type']])
            self.__UpdateHelper('TransmitterDeviceID', TransmitterDeviceIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterDeviceID')

    def __MatchTransmitterDeviceID(self, match, tag):

        TypeStates = {
            'BAY' : 'Docking Bay',
            'CH'  : 'Channel'
        }

        qualifier = {
            'Channel' : match.group(2).decode(),
            'Type' : TypeStates[match.group(1).decode()]
        }

        value = match.group(3).decode().strip()
        value = 'Unknown' if value == 'UNKNOWN' else value
        self.WriteStatus('TransmitterDeviceID', value, qualifier)

    def UpdateTransmitterModel(self, value, qualifier):

        TypeStates = {
            'Docking Bay' : 'BAY',
            'Channel'     : 'CH'
        }

        if qualifier['Channel'] in ['1', '2'] and qualifier['Type'] in TypeStates:
            TransmitterModelCmdString = '< GET {} 0 TX_MODEL >'.format(TypeStates[qualifier['Type']])
            self.__UpdateHelper('TransmitterModel', TransmitterModelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterModel')

    def __MatchTransmitterModel(self, match, tag):

        TypeStates = {
            'BAY' : 'Docking Bay',
            'CH'  : 'Channel'
        }

        ValueStateValues = {
            'MXW1X'   : 'MXW1X',
            'MXW2X'   : 'MXW2X',
            'MXW6X'   : 'MXW6X',
            'MXW8X'   : 'MXW8X',
            'UNKNOWN' : 'Unknown'
        }

        qualifier = {
            'Channel' : match.group(2).decode(),
            'Type' : TypeStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('TransmitterModel', value, qualifier)

    def UpdateTransmitterStatus(self, value, qualifier):

        TypeStates = {
            'Docking Bay' : 'BAY',
            'Channel'     : 'CH'
        }

        if qualifier['Channel'] in ['1', '2'] and qualifier['Type'] in TypeStates:
            TransmitterStatusCmdString = '< GET {} 0 TX_STATUS >'.format(TypeStates[qualifier['Type']])
            self.__UpdateHelper('TransmitterStatus', TransmitterStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterStatus')

    def __MatchTransmitterStatus(self, match, tag):

        TypeStates = {
            'BAY' : 'Docking Bay',
            'CH'  : 'Channel'
        }

        ValueStateValues = {
            'ACTIVE'     : 'Active',
            'MUTED'      : 'Muted',
            'ON_CHARGER' : 'On Charger',
            'UNKNOWN'    : 'Unknown'
        }

        qualifier = {
            'Channel' : match.group(2).decode(),
            'Type' : TypeStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('TransmitterStatus', value, qualifier)

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

        self.Error(['An error has occured.'])

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