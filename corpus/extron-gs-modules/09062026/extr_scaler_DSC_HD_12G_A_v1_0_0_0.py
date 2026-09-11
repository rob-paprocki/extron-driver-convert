# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
            'AspectRatio': { 'Status': {}},
            'AudioFormat': { 'Status': {}},
            'AudioMute': {'Parameters':['Output'], 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Firmware': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FilmModeDetection': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'GlobalAudioMute': { 'Status': {}},
            'InputGain': { 'Status': {}},
            'InputPresetRecall': { 'Status': {}},
            'InputPresetSave': { 'Status': {}},
            'InputSignalStatus': { 'Status': {}},
            'Logo': { 'Status': {}},
            'LogoAssignment': {'Parameters':['Logo'], 'Status': {}},
            'LogoAvailability': {'Parameters':['Logo'], 'Status': {}},
            'LogoKeySetting': {'Parameters':['Logo'], 'Status': {}},
            'MACAddress': { 'Status': {}},
            'ModelName': { 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'PartNumber': { 'Status': {}},
            'PowerSaveMode': { 'Status': {}},
            'SerialNumber': { 'Status': {}},
            'ScreenSaverStatus': { 'Status': {}},
            'Temperature': { 'Status': {}},
            'TestPattern': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.EchoDisabled = True
        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Aspr1\*([1-2])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'AfmtI1\*([0-3])\r\n'), self.__MatchAudioFormat, None)
            self.AddMatchString(re.compile(b'Amt([0-1]) ([0-1])\r\n'), self.__MatchAudioMute, "Query")
            self.AddMatchString(re.compile(b'Amt([0-1])\r\n'), self.__MatchAudioMute, "Global")
            self.AddMatchString(re.compile(b'Amt([1-2])\*([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Exe([0-1])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Bld(\d.\d{2}.\d{4})\r\n'), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(b'Film1\*([0-1])\r\n'), self.__MatchFilmModeDetection, None)
            self.AddMatchString(re.compile(b'Frz1\*([0-1])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'Aud([+-]\d+)\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'In00 ([0-1])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'LogoE(?:1\*)?(\d{1,3})\r\n'), self.__MatchLogo, None)
            self.AddMatchString(re.compile(b'LogoA(\d{3}),(.*?)\r\n'), self.__MatchLogoAssignment, None)
            self.AddMatchString(re.compile(b'LogoQ00\*([01]+[*01]+)\r\n'), self.__MatchLogoAvailability, None)
            self.AddMatchString(re.compile(b'Lkef(\d{3})\*([0-4])\r\n'), self.__MatchLogoKeySetting, None)
            self.AddMatchString(re.compile(b'Iph ([0-9A-Z-]{17})\r\n'), self.__MatchMACAddress, None)
            self.AddMatchString(re.compile(b'Inf01\*(\w.+)\r\n'), self.__MatchModelName, None)
            self.AddMatchString(re.compile(b'Rate1\*(\d+)\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'Pno(\w.+)\r\n'), self.__MatchPartNumber, None)
            self.AddMatchString(re.compile(b'Psav([0-1])\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(re.compile(b'SsavS1\*([0-9])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(re.compile(b'Inf19\*(\w+)\r\n'), self.__MatchSerialNumber, None)
            self.AddMatchString(re.compile(b'28Stat (\d{1,3}\.\d{1})C\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'Test1\*([0-6])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vmt([0-2]) ([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vol([-+]\d+)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'E(\d{2})\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None) # Echo Mode for SSH

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()        
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill': '1',
            'Follow': '2'
            }

        if value in ValueStateValues:
            AspectRatioCmdString = 'w1*{}ASPR\r'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'w1ASPR\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '1': 'Fill',
            '2': 'Follow'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioFormat(self, value, qualifier):

        ValueStateValues = {
            'None': '0',
            'Analog': '1',
            'LPCM-2Ch': '2',
            'Multi-Ch': '3'
            }

        if value in ValueStateValues:
            AudioFormatCmdString = 'wI1*{}AFMT\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioFormat', AudioFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFormat')

    def UpdateAudioFormat(self, value, qualifier):

        AudioFormatCmdString = 'wI1AFMT\r'
        self.__UpdateHelper('AudioFormat', AudioFormatCmdString, value, qualifier)

    def __MatchAudioFormat(self, match, tag):

        ValueStateValues = {
            '0': 'None',
            '1': 'Analog',
            '2': 'LPCM-2Ch',
            '3': 'Multi-Ch'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioFormat', value, None)

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            'Analog': '1',
            'Digital': '2'
            }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if qualifier['Output'] in OutputStates and value in ValueStateValues:
            AudioMuteCmdString = '{}*{}Z'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        OutputStates = {
            'Analog': '1',
            'Digital': '2'
            }

        if qualifier['Output'] in OutputStates:
            AudioMuteCmdString = 'Z'
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        OutputStates = {
            '1': 'Analog',
            '2': 'Digital'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        if tag == 'Query':
            out1 = ValueStateValues[match.group(1).decode()]
            out2 = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', out1, {'Output': 'Analog'})
            self.WriteStatus('AudioMute', out2, {'Output': 'Digital'})
        elif tag == 'Global':
            value = ValueStateValues[match.group(1).decode()]
            self.WriteStatus('AudioMute', value, {'Output': 'Analog'})
            self.WriteStatus('AudioMute', value, {'Output': 'Digital'})
        else:
            output = OutputStates[match.group(1).decode()]
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, {'Output': output})

    def SetAutoImage(self, value, qualifier):

        ValueStateValues = {
            'Execute' : '1*0A', 
            'Execute and Fill' : '1*1A',
            'Execute and Follow' : '1*2A'
        }

        if value in ValueStateValues:
            AutoImageCmdString = '{0}'.format(ValueStateValues[value])
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')
  
    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{}X'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFilmModeDetection(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            FilmModeDetectionCmdString = 'w1*{}FILM\r'.format(ValueStateValues[value])
            self.__SetHelper('FilmModeDetection', FilmModeDetectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFilmModeDetection')

    def UpdateFilmModeDetection(self, value, qualifier):

        FilmModeDetectionCmdString = 'w1FILM\r'
        self.__UpdateHelper('FilmModeDetection', FilmModeDetectionCmdString, value, qualifier)

    def __MatchFilmModeDetection(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FilmModeDetection', value, None)

    def UpdateFirmware(self, value, qualifier):

        FirmwareCmdString = '*q'
        self.__UpdateHelper('Firmware', FirmwareCmdString, value, qualifier)
        

    def __MatchFirmware(self, match, tag):

        self.WriteStatus('Firmware', match.group(1).decode(), None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            FreezeCmdString = '1*{}F'.format(ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '1F'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetGlobalAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            GlobalAudioMuteCmdString = '{}Z'.format(ValueStateValues[value])
            self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalAudioMute')

    def SetInputGain(self, value, qualifier):

        if -18 <= value <= 24:
            InputGainCmdString = '{}G'.format(value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        InputGainCmdString = 'G'
        self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)

    def __MatchInputGain(self, match, tag):

        value = int(match.group(1).decode())
        if -18 <= value <= 24:
            self.WriteStatus('InputGain', value, None)

    def SetInputPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            InputPresetRecallCmdString = '2*{}.'.format(value)
            self.__SetHelper('InputPresetRecall', InputPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')

    def SetInputPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            InputPresetSaveCmdString = '2*{},'.format(value)
            self.__SetHelper('InputPresetSave', InputPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InputSignalStatus', value, None)

    def SetLogo(self, value, qualifier):

        ValueStateValues = {
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
            '16': '16',
            'Screen Saver': '101',
            'HDCP': '201',
            'Off': '0'
            }

        if value in ValueStateValues:
            LogoCmdString = 'wE1*{}LOGO\r'.format(ValueStateValues[value])
            self.__SetHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogo')

    def UpdateLogo(self, value, qualifier):

        LogoCmdString = 'wE1LOGO\r'
        self.__UpdateHelper('Logo', LogoCmdString, value, qualifier)

    def __MatchLogo(self, match, tag):

        ValueStateValues = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '5' : '5',
            '6' : '6',
            '7' : '7',
            '8' : '8',
            '9' : '9',
            '10' : '10',
            '11' : '11',
            '12' : '12',
            '13' : '13',
            '14' : '14',
            '15' : '15',
            '16' : '16',
            '101' : 'Screen Saver',
            '201' : 'HDCP',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Logo', value, None)

    def SetLogoAssignment(self, value, qualifier):

        LogoStates = {
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
            '16': '16',
            'Screen Saver': '101',
            'HDCP': '201'
            }

        if qualifier['Logo'] in LogoStates:
            LogoAssignmentCmdString = 'wA{},{}LOGO\r'.format(LogoStates[qualifier['Logo']], value)
            self.__SetHelper('LogoAssignment', LogoAssignmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogoAssignment')

    def UpdateLogoAssignment(self, value, qualifier):

        LogoStates = {
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
            '16': '16',
            'Screen Saver': '101',
            'HDCP': '201'
            }

        if qualifier['Logo'] in LogoStates:
            LogoAssignmentCmdString = 'wA{}LOGO\r'.format(qualifier['Logo'])
            self.__UpdateHelper('LogoAssignment', LogoAssignmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogoAssignment')

    def __MatchLogoAssignment(self, match, tag):

        LogoStates = {
            1 : '1',
            2 : '2',
            3 : '3',
            4 : '4',
            5 : '5',
            6 : '6',
            7 : '7',
            8 : '8',
            9 : '9',
            10 : '10',
            11 : '11',
            12 : '12',
            13 : '13',
            14 : '14',
            15 : '15',
            16 : '16',
            101 : 'Screen Saver',
            201 : 'HDCP'
        }

        qualifier = {'Logo': LogoStates[int(match.group(1).decode())]}
        value = match.group(2).decode()
        self.WriteStatus('LogoAssignment', value, qualifier)

    def UpdateLogoAvailability(self, value, qualifier):

        LogoAvailabilityCmdString = 'wQLOGO\r'
        self.__UpdateHelper('LogoAvailability', LogoAvailabilityCmdString, value, qualifier)
    
    def __MatchLogoAvailability(self, match, tag):

        ValueStateValues = {
            '1' : 'Saved',
            '0' : 'Empty'
        }
        results = match.group(1).decode().split('*')
        logo = 1
        for i in results[0]:
            value = ValueStateValues[i]
            self.WriteStatus('LogoAvailability', value, {'Logo':str(logo)})
            logo += 1
        self.WriteStatus('LogoAvailability', ValueStateValues[results[1]], {'Logo':'Screen Saver'})
        self.WriteStatus('LogoAvailability', ValueStateValues[results[2]], {'Logo':'HDCP'})

    def SetLogoKeySetting(self, value, qualifier):

        LogoStates = {
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
            '16': '16',
            'Screen Saver': '101',
            'HDCP': '201'
            }

        ValueStateValues = {
            'Disabled': '0',
            'Transparency': '1',
            'RGB Key': '2',
            'Level Key': '3',
            'Alpha Key': '4'
            }

        if qualifier['Logo'] in LogoStates and value in ValueStateValues:
            LogoKeySettingCmdString = 'w{}*{}LKEF\r'.format(LogoStates[qualifier['Logo']], ValueStateValues[value])
            self.__SetHelper('LogoKeySetting', LogoKeySettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogoKeySetting')

    def UpdateLogoKeySetting(self, value, qualifier):

        LogoStates = {
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
            '16': '16',
            'Screen Saver': '101',
            'HDCP': '201'
            }

        if qualifier['Logo'] in LogoStates:
            LogoKeySettingCmdString = 'w{}LKEF\r'.format(LogoStates[qualifier['Logo']])
            self.__UpdateHelper('LogoKeySetting', LogoKeySettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogoKeySetting')

    def __MatchLogoKeySetting(self, match, tag):

        LogoStates = {
            1 : '1',
            2 : '2',
            3 : '3',
            4 : '4',
            5 : '5',
            6 : '6',
            7 : '7',
            8 : '8',
            9 : '9',
            10 : '10',
            11 : '11',
            12 : '12',
            13 : '13',
            14 : '14',
            15 : '15',
            16 : '16',
            101 : 'Screen Saver',
            201 : 'HDCP'
        }

        ValueStateValues = {
            '0' : 'Disabled',
            '1' : 'Transparency',
            '2' : 'RGB Key',
            '3' : 'Level Key',
            '4' : 'Alpha Key'
        }

        qualifier = {'Logo': LogoStates[int(match.group(1).decode())]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LogoKeySetting', value, qualifier)

    def UpdateMACAddress(self, value, qualifier):

        MACAddressCmdString = 'wCH\r'
        self.__UpdateHelper('MACAddress', MACAddressCmdString, value, qualifier)
        

    def __MatchMACAddress(self, match, tag):
        
        self.WriteStatus('MACAddress', match.group(1).decode(), None)

    def UpdateModelName(self, value, qualifier):

        ModelNameCmdString = '1i'
        self.__UpdateHelper('ModelName', ModelNameCmdString, value, qualifier)
        

    def __MatchModelName(self, match, tag):
        
        self.WriteStatus('ModelName', match.group(1).decode(), None)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '720p (25Hz)': '29',
            '720p (29.97Hz)': '30',
            '720p (30Hz)': '31',
            '720p (50Hz)': '32',
            '720p (59.94Hz)': '33',
            '720p (60Hz)': '34',
            '1080i (50Hz)': '35`',
            '1080i (59.94Hz)': '36',
            '1080i (60Hz)': '37',
            '1080p (23.98Hz)': '38',
            '1080p (24Hz)': '39',
            '1080p (25Hz)': '40',
            '1080p (29.97Hz)': '41',
            '1080p (30Hz)': '42',
            '1080p (50Hz)': '43',
            '1080p (59.94Hz)': '44',
            '1080p (60Hz)': '45',
            '2048x1080 (23.98Hz)': '46',
            '2048x1080 (24Hz)': '47',
            '2048x1080 (25Hz)': '48',
            '2048x1080 (29.97Hz)': '49',
            '2048x1080 (30Hz)': '50',
            '2048x1080 (50Hz)': '51',
            '2048x1080 (59.94Hz)': '52',
            '2048x1080 (60Hz)': '53',
            '3480x2160 (23.98Hz)': '59',
            '3480x2160 (24Hz)': '60',
            '3480x2160 (25Hz)': '61',
            '3480x2160 (29.97Hz)': '62',
            '3480x2160 (30Hz)': '63',
            '3480x2160 (50Hz)': '64',
            '3480x2160 (59.94Hz)': '65',
            '3480x2160 (60Hz)': '66',
            '4096x2160 (23.98Hz)': '69',
            '4096x2160 (24Hz)': '70',
            '4096x2160 (25Hz)': '71',
            '4096x2160 (29.97Hz)': '72',
            '4096x2160 (30Hz)': '73',
            '4096x2160 (50Hz)': '74',
            '4096x2160 (59.94Hz)': '75',
            '4096x2160 (60Hz)': '76',
            'Custom Rate 1': '201',
            'Custom Rate 2': '202',
            'Custom Rate 3': '203'
            }

        if value in ValueStateValues:
            OutputResolutionCmdString = 'w1*{}RATE\r'.format(ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = 'w1RATE\r'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            '29': '720p (25Hz)',
            '30': '720p (29.97Hz)',
            '31': '720p (30Hz)',
            '32': '720p (50Hz)',
            '33': '720p (59.94Hz)',
            '34': '720p (60Hz)',
            '35': '1080i (50Hz)',
            '36': '1080i (59.94Hz)',
            '37': '1080i (60Hz)',
            '38': '1080p (23.98Hz)',
            '39': '1080p (24Hz)',
            '40': '1080p (25Hz)',
            '41': '1080p (29.97Hz)',
            '42': '1080p (30Hz)',
            '43': '1080p (50Hz)',
            '44': '1080p (59.94Hz)',
            '45': '1080p (60Hz)',
            '46': '2048x1080 (23.98Hz)',
            '47': '2048x1080 (24Hz)',
            '48': '2048x1080 (25Hz)',
            '49': '2048x1080 (29.97Hz)',
            '50': '2048x1080 (30Hz)',
            '51': '2048x1080 (50Hz)',
            '52': '2048x1080 (59.94Hz)',
            '53': '2048x1080 (60Hz)',
            '59': '3480x2160 (23.98Hz)',
            '60': '3480x2160 (24Hz)',
            '61': '3480x2160 (25Hz)',
            '62': '3480x2160 (29.97Hz)',
            '63': '3480x2160 (30Hz)',
            '64': '3480x2160 (50Hz)',
            '65': '3480x2160 (59.94Hz)',
            '66': '3480x2160 (60Hz)',
            '69': '4096x2160 (23.98Hz)',
            '70': '4096x2160 (24Hz)',
            '71': '4096x2160 (25Hz)',
            '72': '4096x2160 (29.97Hz)',
            '73': '4096x2160 (30Hz)',
            '74': '4096x2160 (50Hz)',
            '75': '4096x2160 (59.94Hz)',
            '76': '4096x2160 (60Hz)',
            '201': 'Custom Rate 1',
            '202': 'Custom Rate 2',
            '203': 'Custom Rate 3',
            }

        value = ValueStateValues[str(int(match.group(1).decode()))]
        self.WriteStatus('OutputResolution', value, None)

    def UpdatePartNumber(self, value, qualifier):

        PartNumberCmdString = 'n'
        self.__UpdateHelper('PartNumber', PartNumberCmdString, value, qualifier) 

    def __MatchPartNumber(self, match, tag):

        self.WriteStatus('PartNumber', match.group(1).decode(), None)

    def SetPowerSaveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            PowerSaveModeCmdString = 'w{}PSAV\r'.format(ValueStateValues[value])
            self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerSaveMode')

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = 'wPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def UpdateScreenSaverStatus(self, value, qualifier):

        ScreenSaverStatusCmdString = 'wS1SSAV\r'
        self.__UpdateHelper('ScreenSaverStatus', ScreenSaverStatusCmdString, value, qualifier)

    def __MatchScreenSaverStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Active Input Detected; Timer not running',
            '2': 'No Active Input; Timer expired; Output sync disabled',
            '1': 'No Active Input; Timer running; Output sync enabled'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenSaverStatus', value, None)

    def UpdateSerialNumber(self, value, qualifier):

        SerialNumberCmdString = '19i'
        self.__UpdateHelper('SerialNumber', SerialNumberCmdString, value, qualifier) 

    def __MatchSerialNumber(self, match, tag):
        
        self.WriteStatus('SerialNumber', match.group(1).decode(), None)

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'w28STAT\r'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = float(match.group(1).decode())
        self.WriteStatus('Temperature', value, None)

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Crop': '1',
            'Alternating Pixels': '2',
            'Crosshatch': '3',
            'Color Bars': '4',
            '32-level split Grayscale': '5',
            'Audio Test': '6'
            }

        if value in ValueStateValues:
            TestPatternCmdString = 'w1*{}TEST\r'.format(ValueStateValues[value])
            self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = 'w1TEST\r'
        self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def __MatchTestPattern(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Crop',
            '2': 'Alternating Pixels',
            '3': 'Crosshatch',
            '4': 'Color Bars',
            '5': '32-level split Grayscale',
            '6': 'Audio Test'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'On with Sync': '2',
            'Off': '0'
            }

        if value in ValueStateValues:
            VideoMuteCmdString = '{}B'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '2': 'On with Sync',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if -100 <= value <= 0:
            VolumeCmdString = '{}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if -100 <= value <= 0:
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n') 
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '01' : 'Invalid input number',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter',
            '14' : 'Invalid command for this configuration',
            '17' : 'Invalid command for signal type',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '28' : 'Bad filename or file not found',
            '33' : 'Bad file type or size'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error(['Error occurred: {}'.format(DEVICE_ERROR_CODES[value])])
        else:
            self.Error(['Unrecognized error code: '+ match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
