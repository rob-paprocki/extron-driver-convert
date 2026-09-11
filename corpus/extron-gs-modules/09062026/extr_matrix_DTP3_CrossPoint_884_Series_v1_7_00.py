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
            'AmplifierAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'AmplifierMute': {'Parameters': ['Output'], 'Status': {}},
            'AmplifierOutputMode': { 'Status': {}},
            'AmplifierPostmixerTrim': {'Parameters': ['Output'], 'Status': {}},
            'AnalogAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'AnalogMute': {'Parameters': ['Output'], 'Status': {}},
            'AnalogPostmixerTrim': {'Parameters': ['Output'], 'Status': {}},
            'AspectRatio': {'Parameters': ['Input'], 'Status': {}},
            'ATAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'ATMute': {'Parameters': ['Output'], 'Status': {}},
            'ATPostmixerTrim': {'Parameters': ['Output'], 'Status': {}},
            'AutoImage': {'Parameters': ['Output'], 'Status': {}},
            'AutomixerGateMonitor': {'Parameters': ['Input'], 'Status': {}},
            'AutomixerGateStatus': {'Parameters': ['Input'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FanSpeed': {'Parameters': ['Fan'], 'Status': {}},
            'FlexAnalogInputGain': {'Parameters': ['Input'], 'Status': {}},
            'FlexDigitalInputGain': {'Parameters': ['Input'], 'Status': {}},
            'FlexInputMute': {'Parameters': ['Input'], 'Status': {}},
            'FlexInputSignalLevelMonitor': {'Parameters': ['Input'], 'Status': {}},
            'FlexInputSignalLevelStatus': {'Parameters': ['Input'], 'Status': {}},
            'FlexInputSignalLevelValue': {'Parameters': ['Input'], 'Status': {}},
            'FlexPremixerGain': {'Parameters': ['Input'], 'Status': {}},
            'FlexPremixerMute': {'Parameters': ['Input'], 'Status': {}},
            'Freeze': {'Parameters': ['Output'], 'Status': {}},
            'GlobalVideoMute': { 'Status': {}},
            'GroupMixpoint': {'Parameters': ['Group'], 'Status': {}},
            'GroupMute': {'Parameters': ['Group'], 'Status': {}},
            'GroupOutputAttenuation': {'Parameters': ['Group'], 'Status': {}},
            'GroupPostmixerTrim': {'Parameters': ['Group'], 'Status': {}},
            'GroupPrematrixTrim': {'Parameters': ['Group'], 'Status': {}},
            'GroupPremixerGain': {'Parameters': ['Group'], 'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'HDMIDTPAttenuation': {'Parameters': ['Output', 'L/R'], 'Status': {}},
            'HDMIDTPMute': {'Parameters': ['Output', 'L/R'], 'Status': {}},
            'HDMIDTPPostmixerTrim': {'Parameters': ['Output', 'L/R'], 'Status': {}},
            'InputAudioSwitchMode': {'Parameters': ['Input'], 'Status': {}},
            'InputConnectorType': {'Parameters': ['Input'], 'Status': {}},
            'InputGain': {'Parameters': ['Input', 'Format', 'L/R'], 'Status': {}},
            'InputMute': {'Parameters': ['Input', 'L/R'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'Logo': {'Parameters': ['Output'], 'Status': {}},
            'MatrixIONameCommand': {'Parameters': ['Type', 'Name', 'Number'], 'Status': {}},
            'MatrixIONameStatus': {'Parameters': ['Type', 'Number'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'MixpointGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MixpointMute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputAudioSelect': {'Parameters': ['Output'], 'Status': {}},
            'OutputResolution': {'Parameters': ['Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatusName': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PhantomPower': {'Parameters': ['Input'], 'Status': {}},
            'PostMatrixGain': {'Parameters': ['Output', 'L/R'], 'Status': {}},
            'PostMatrixMute': {'Parameters': ['Output', 'L/R'], 'Status': {}},
            'PowerSaveMode': { 'Status': {}},
            'PowerSupplyVoltage': { 'Status': {}},
            'PrematrixTrim': {'Parameters': ['Input', 'L/R'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'RefreshMatrix': { 'Status': {}},
            'RefreshMatrixIONames': { 'Status': {}},
            'ScalerPresetRecall': {'Parameters': ['Output'], 'Status': {}},
            'Temperature': {'Parameters': ['Scale'], 'Status': {}},
            'USBCallStatus': { 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}}
        }
        
        self.EchoDisabled = True
        self.VerboseDisabled = True

        self.GroupFunction = {}
        
        self.InputSize = 12
        self.OutputSize = 12
        self.OutputSizeWAudio = 14
        
        self.DTPConstraints = {
            'Min': 1,
            'Max': 12,
            }
        
        self.ScaledOutputConstraints = {
            'Min': 1,
            'Max': 12,
            }
        
        self.EDIDStates	= {
            '1'  : 'Output 1', 
            '2'  : 'Output 2', 
            '3'  : 'Output 3', 
            '4'  : 'Output 4', 
            '5'  : 'Output 5A', 
            '6'  : 'Output 5B', 
            '7'  : 'Output 6A', 
            '8'  : 'Output 6B', 
            '9'  : 'Output 7', 
            '10' : 'Output 8', 
            '11' : '1024x768 @ 50Hz', 
            '12' : '1024x768 @ 60Hz', 
            '13' : '1280x720 @ 50Hz', 
            '14' : '1280x720 @ 60Hz', 
            '15' : '1280x768 @ 50Hz', 
            '16' : '1280x768 @ 60Hz', 
            '17' : '1280x800 @ 50Hz', 
            '18' : '1280x800 @ 60Hz', 
            '19' : '1280x1024 @ 50Hz', 
            '20' : '1280x1024 @ 60Hz', 
            '21' : '1360x768 @ 50Hz', 
            '22' : '1360x768 @ 60Hz', 
            '23' : '1366x768 @ 50Hz', 
            '24' : '1366x768 @ 60Hz', 
            '25' : '1400x1050 @ 50Hz', 
            '26' : '1400x1050 @ 60Hz', 
            '27' : '1440x900 @ 50Hz', 
            '28' : '1440x900 @ 60Hz', 
            '29' : '1600x900 @ 50Hz', 
            '30' : '1600x900 @ 60Hz', 
            '31' : '1600x1200 @ 50Hz', 
            '32' : '1600x1200 @ 60Hz', 
            '33' : '1680x1050 @ 50Hz', 
            '34' : '1680x1050 @ 60Hz', 
            '35' : '1920x1080 @ 50Hz', 
            '36' : '1920x1080 @ 60Hz', 
            '37' : '1920x1200 @ 50Hz', 
            '38' : '1920x1200 @ 60Hz', 
            '39' : '2048x1080 @ 50Hz', 
            '40' : '2048x1080 @ 60Hz', 
            '41' : '480p 2_Ch Audio @ 60Hz', 
            '42' : '576p 2_Ch Audio @ 50Hz', 
            '43' : '720p 2_Ch Audio @ 50Hz', 
            '44' : '720p 2_Ch Audio @ 60Hz', 
            '45' : '720p Multi_Ch Audio @ 50Hz', 
            '46' : '720p Multi_Ch Audio @ 60Hz', 
            '47' : '1080i 2_Ch Audio @ 50Hz', 
            '48' : '1080i 2_Ch Audio @ 60Hz', 
            '49' : '1080i Multi_Ch Audio @ 50Hz', 
            '50' : '1080i Multi_Ch Audio @ 60Hz', 
            '51' : '1080p 2_Ch Audio @ 50Hz', 
            '52' : '1080p 2_Ch Audio @ 60Hz', 
            '53' : '1080p Multi_Ch Audio @ 50Hz', 
            '54' : '1080p Multi_Ch Audio @ 60Hz', 
            '55' : '3840x2160 2_Ch Audio @ 30Hz', 
            '56' : '3840x2160 Multi_Ch Audio @ 30Hz', 
            '57' : 'User Assigned 1', 
            '58' : 'User Assigned 2', 
            '59' : 'User Assigned 3', 
            '60' : 'User Assigned 4', 
            '61' : 'User Assigned 5', 
            '62' : 'User Assigned 6', 
            '63' : 'User Assigned 7', 
            '64' : 'User Assigned 8', 
            '65' : 'User Assigned 9', 
            '66' : 'User Assigned 10'
        }

        self.MixPointInputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'Output 7 Left'  : '12',
            'Output 7 Right' : '13',
            'Output 8 Left'  : '14',
            'Output 8 Right' : '15',
            'Output 9 Left'  : '16',
            'Output 9 Right' : '17',
            'Output 10 Left'  : '18',
            'Output 10 Right' : '19',
            'Output 11 Left'  : '20',
            'Output 11 Right' : '21',
            'Output 12 Left'  : '22',
            'Output 12 Right' : '23',
            'Output 13 Left'  : '24',
            'Output 13 Right' : '25',
            'Output 14 Left'  : '26',
            'Output 14 Right' : '27',
            'Flex 1': '28',
            'Flex 2': '29',
            'Flex 3': '30',
            'Flex 4': '31',
            'Flex 5': '32',
            'Flex 6': '33',
            'Flex 7': '34',
            'Flex 8': '35',
            'Flex 9': '36',
            'Flex 10': '37',
            'Flex 11': '38',
            'Flex 12': '39',
            'Flex 13': '40',
            'Flex 14': '41',
            'Flex 15': '42',
            'Flex 16': '43',
            'Flex 17': '44',
            'Flex 18': '45',
            'Flex 19': '46',
            'Flex 20': '47',
            'Flex 21': '48',
            'Flex 22': '49',
            'Flex 23': '50',
            'Flex 24': '51',
            'Flex 25': '52',
            'Flex 26': '53',
            'Flex 27': '54',
            'Flex 28': '55',
            'Flex 29': '56',
            'Flex 30': '57',
            'Flex 31': '58',
            'Flex 32': '59',
            'Flex 33': '60',
            'Flex 34': '61',
            'Flex 35': '62',
            'Flex 36': '63',
            'Flex 37': '64',
            'Flex 38': '65',
            'Flex 39': '66',
            'Flex 40': '67',
            'Flex 41': '68',
            'Flex 42': '69',
            'Flex 43': '70',
            'Flex 44': '71',
            'Flex 45': '72',
            'Flex 46': '73',
            'Flex 47': '74',
            'Flex 48': '75'
        }

        self.MixPointOutputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'Output 7 Left'  : '12',
            'Output 7 Right' : '13',
            'Output 8 Left'  : '14',
            'Output 8 Right' : '15',
            'Output 9 Left'  : '16',
            'Output 9 Right' : '17',
            'Output 10 Left'  : '18',
            'Output 10 Right' : '19',
            'Output 11 Left'  : '20',
            'Output 11 Right' : '21',
            'Output 12 Left'  : '22',
            'Output 12 Right' : '23',
            'Line Out 1' : '24',
            'Line Out 2' : '25',
            'Amp Out 1' : '26',
            'Amp Out 2' : '27',
            'USB 1 Left': '28',
            'USB 1 Right': '29',
            'USB 2 Left': '30',
            'USB 2 Right': '31',
            'USB 3 Left': '32',
            'USB 3 Right': '33',
            'AT & Exp 1': '36',
            'AT & Exp 2': '37',
            'AT & Exp 3': '38',
            'AT & Exp 4': '39',
            'AT & Exp 5': '40',
            'AT & Exp 6': '41',
            'AT & Exp 7': '42',
            'AT & Exp 8': '43',
            'AT & Exp 9': '44',
            'AT & Exp 10': '45',
            'AT & Exp 11': '46',
            'AT & Exp 12': '47',
            'AT & Exp 13': '48',
            'AT & Exp 14': '49',
            'AT & Exp 15': '50',
            'AT & Exp 16': '51',
            'AT 17': '52',
            'AT 18': '53',
            'AT 19': '54',
            'AT 20': '55',
            'AT 21': '56',
            'AT 22': '57',
            'AT 23': '58',
            'AT 24': '59',
            'AT 25': '60',
            'AT 26': '61',
            'AT 27': '62',
            'AT 28': '63',
            'AT 29': '64',
            'AT 30': '65',
            'AT 31': '66',
            'AT 32': '67',
            'V. Send A': '68',
            'V. Send B': '69',
            'V. Send C': '70',
            'V. Send D': '71',
            'V. Send E': '72',
            'V. Send F': '73',
            'V. Send G': '74',
            'V. Send H': '75',
            'V. Send I': '76',
            'V. Send J': '77',
            'V. Send K': '78',
            'V. Send L': '79',
            'V. Send M': '80',
            'V. Send N': '81',
            'V. Send O': '82',
            'V. Send P': '83',
        }
        
        self.MixPointInputsStatus = {
            '00': 'Output 1 Left',
            '01': 'Output 1 Right',
            '02': 'Output 2 Left',
            '03': 'Output 2 Right',
            '04': 'Output 3 Left',
            '05': 'Output 3 Right',
            '06': 'Output 4 Left',
            '07': 'Output 4 Right',
            '08': 'Output 5 Left',
            '09': 'Output 5 Right',
            '10': 'Output 6 Left',
            '11': 'Output 6 Right',
            '12': 'Output 7 Left',  
            '13': 'Output 7 Right', 
            '14': 'Output 8 Left',  
            '15': 'Output 8 Right', 
            '16': 'Output 9 Left',  
            '17': 'Output 9 Right', 
            '18': 'Output 10 Left',
            '19': 'Output 10 Right',
            '20': 'Output 11 Left' ,
            '21': 'Output 11 Right',
            '22': 'Output 12 Left' ,
            '23': 'Output 12 Right',
            '24': 'Output 13 Left' ,
            '25': 'Output 13 Right',
            '26': 'Output 14 Left' ,
            '27': 'Output 14 Right',
            '28': 'Flex 1', 
            '29': 'Flex 2', 
            '30': 'Flex 3', 
            '31': 'Flex 4', 
            '32': 'Flex 5', 
            '33': 'Flex 6', 
            '34': 'Flex 7', 
            '35': 'Flex 8', 
            '36': 'Flex 9', 
            '37': 'Flex 10',
            '38': 'Flex 11',
            '39': 'Flex 12',
            '40': 'Flex 13',
            '41': 'Flex 14',
            '42': 'Flex 15',
            '43': 'Flex 16',
            '44': 'Flex 17',
            '45': 'Flex 18',
            '46': 'Flex 19',
            '47': 'Flex 20',
            '48': 'Flex 21',
            '49': 'Flex 22',
            '50': 'Flex 23',
            '51': 'Flex 24',
            '52': 'Flex 25',
            '53': 'Flex 26',
            '54': 'Flex 27',
            '55': 'Flex 28',
            '56': 'Flex 29',
            '57': 'Flex 30',
            '58': 'Flex 31',
            '59': 'Flex 32',
            '60': 'Flex 33',
            '61': 'Flex 34',
            '62': 'Flex 35',
            '63': 'Flex 36',
            '64': 'Flex 37',
            '65': 'Flex 38',
            '66': 'Flex 39',
            '67': 'Flex 40',
            '68': 'Flex 41',
            '69': 'Flex 42',
            '70': 'Flex 43',
            '71': 'Flex 44',
            '72': 'Flex 45',
            '73': 'Flex 46',
            '74': 'Flex 47',
            '75': 'Flex 48'
        }

        self.MixPointOutputsStatus = {
            '00': 'Output 1 Left', 
            '01': 'Output 1 Right',
            '02': 'Output 2 Left', 
            '03': 'Output 2 Right',
            '04': 'Output 3 Left', 
            '05': 'Output 3 Right',
            '06': 'Output 4 Left', 
            '07': 'Output 4 Right',
            '08': 'Output 5 Left', 
            '09': 'Output 5 Right',
            '10': 'Output 6 Left', 
            '11': 'Output 6 Right',
            '12': 'Output 7 Left',
            '13': 'Output 7 Right',
            '14': 'Output 8 Left',
            '15': 'Output 8 Right',
            '16': 'Output 9 Left',
            '17': 'Output 9 Right',
            '18': 'Output 10 Left',
            '19': 'Output 10 Right',
            '20': 'Output 11 Left',
            '21': 'Output 11 Right',
            '22': 'Output 12 Left',
            '23': 'Output 12 Right',
            '24': 'Line Out 1',
            '25': 'Line Out 2',
            '26': 'Amp Out 1',
            '27': 'Amp Out 2',
            '28': 'USB 1 Left',
            '29': 'USB 1 Right',
            '30': 'USB 2 Left',
            '31': 'USB 2 Right',
            '32': 'USB 3 Left',
            '33': 'USB 3 Right',
            '36': 'AT & Exp 1',
            '37': 'AT & Exp 2',
            '38': 'AT & Exp 3',
            '39': 'AT & Exp 4',
            '40': 'AT & Exp 5',
            '41': 'AT & Exp 6',
            '42': 'AT & Exp 7',
            '43': 'AT & Exp 8',
            '44': 'AT & Exp 9',
            '45': 'AT & Exp 10',
            '46': 'AT & Exp 11',
            '47': 'AT & Exp 12',
            '48': 'AT & Exp 13',
            '49': 'AT & Exp 14',
            '50': 'AT & Exp 15',
            '51': 'AT & Exp 16',
            '52': 'AT 17',
            '53': 'AT 18',
            '54': 'AT 19',
            '55': 'AT 20',
            '56': 'AT 21',
            '57': 'AT 22',
            '58': 'AT 23',
            '59': 'AT 24',
            '60': 'AT 25',
            '61': 'AT 26',
            '62': 'AT 27',
            '63': 'AT 28',
            '64': 'AT 29',
            '65': 'AT 30',
            '66': 'AT 31',
            '67': 'AT 32',
            '68': 'V. Send A',
            '69': 'V. Send B',
            '70': 'V. Send C',
            '71': 'V. Send D',
            '72': 'V. Send E',
            '73': 'V. Send F',
            '74': 'V. Send G',
            '75': 'V. Send H',
            '76': 'V. Send I',
            '77': 'V. Send J',
            '78': 'V. Send K',
            '79': 'V. Send L',
            '80': 'V. Send M',
            '81': 'V. Send N',
            '82': 'V. Send O',
            '83': 'V. Send P',
        }
        
        self.OutputStates = {
            '1A'  : '1A', 
            '1B'  : '1B', 
            '2A'  : '2A', 
            '2B'  : '2B', 
            '3A' : '3A',
            '3B' : '3B',
            '4A' : '4A',
            '4B' : '4B', 
            '5A' : '5A',
            '5B' : '5B', 
            '6A' : '6A',
            '6B' : '6B', 
            '7'  : '7', 
            '8'  : '8',
            '9'  : '9', 
            '10'  : '10',
            '11'  : '11', 
            '12'  : '12'
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Ds[gG]600(26|27)\*([-]\d{1,4}|0)\r\n'), self.__MatchAmplifierAttenuation, None)
            self.AddMatchString(re.compile(b'Ds[mM]600(26|27)\*(0|1)\r\n'), self.__MatchAmplifierMute, None)
            self.AddMatchString(re.compile(b'Spkr([1-4])\r\n'), self.__MatchAmplifierOutputMode, None)
            self.AddMatchString(re.compile(b'Ds[gG]6012([67])\*([0-9 -]{1,4})\r\n'), self.__MatchAmplifierPostmixerTrim, None)
            self.AddMatchString(re.compile(b'Ds[gG]6002([4-5])\*([-]\d{1,4}|0)\r\n'), self.__MatchAnalogAttenuation, None)
            self.AddMatchString(re.compile(b'Ds[mM]6002([4-5])\*(0|1)\r\n'), self.__MatchAnalogMute, None)
            self.AddMatchString(re.compile(b'Ds[gG]6012([45])\*([0-9 -]{1,4})\r\n'), self.__MatchAnalogPostmixerTrim, None)
            self.AddMatchString(re.compile(b'Aspr(\d{1,2})\*(1|2)\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'Ds[gG]600([3-6][0-9])\*([-]\d{1,4}|0)\r\n'), self.__MatchATAttenuation, None)
            self.AddMatchString(re.compile(b'Ds[mM]600([3-6][0-9])\*(0|1)\r\n'), self.__MatchATMute, None)
            self.AddMatchString(re.compile(b'Ds[gG]601([3-6][0-9])\*([0-9 -]{1,4})\r\n'), self.__MatchATPostmixerTrim, None)
            self.AddMatchString(re.compile(b'DsJ590([0-4][0-9])\*(0|1024)\r\n'), self.__MatchAutomixerGateMonitor, None)
            self.AddMatchString(re.compile(b'DsV590([0-4][0-9])\*[01]\*\d+\*([01])\r\n'), self.__MatchAutomixerGateStatus, None)
            self.AddMatchString(re.compile(b'GrpmD(\d+)\*([-+]{0,1}[0-9]{1,4})\r\n'), self.__MatchGroup, None)
            self.AddMatchString(re.compile(b'Ds[gG]600([0-2][0-9])\*([-]\d{1,4}|0)\r\n'), self.__MatchHDMIDTPAttenuation, None)
            self.AddMatchString(re.compile(b'Ds[mM]600([0-2][0-9])\*(0|1)\r\n'), self.__MatchHDMIDTPMute, None)
            self.AddMatchString(re.compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Ds[gG]400([0-4][0-9])\*([0-9 -]{1,4})\r\n'), self.__MatchFlexAnalogInputGain, None)
            self.AddMatchString(re.compile(b'Ds[hH]400([0-4][0-9])\*([0-9 -]{1,4})\r\n'), self.__MatchFlexDigitalInputGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]400([0-4][0-9])\*(0|1)\r\n'), self.__MatchFlexInputMute, None)
            self.AddMatchString(re.compile(b'DsJ400([0-4][0-9])\*(\d+)\r\n'), self.__MatchFlexInputSignalLevelMonitor, None)
            self.AddMatchString(re.compile(b'DsV400([0-4][0-9])\*[01]\*(\d+)\*([01])\r\n'), self.__MatchFlexInputSignalLevelStatus, None)
            self.AddMatchString(re.compile(b'Ds[gG]401([0-4][0-9])\*([0-9 -]{1,5})\r\n'), self.__MatchFlexPremixerGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]401([0-4][0-9])\*([01])\r\n'), self.__MatchFlexPremixerMute, None)
            self.AddMatchString(re.compile(b'Frz(\d{1,2})\*(0|1)\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'AfmtI(\d{1,2})\*([0-2])\r\n'), self.__MatchInputAudioSwitchMode, 'Single')
            self.AddMatchString(re.compile(b'AfmtI00\*([0-2]{12})\r\n'), self.__MatchInputAudioSwitchMode, 'All')
            self.AddMatchString(re.compile(b'Ityp([56])\*([12])\r\n'), self.__MatchInputConnectorType, None)
            self.AddMatchString(re.compile(b'Ds([gGhH])300([012][0-9])\*([0-9 -]{1,4})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]300([012][0-9])\*([01])\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'In00 ([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'SigI ([0-1]+)\r\n'), self.__MatchInputSignalStatus, 'Unsolicited')
            self.AddMatchString(re.compile(b'HdcpE(\d{1,2}[ab]?)\*(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'LogoE(\d{1,2})\*(.*)\r\n'), self.__MatchLogo, None)
            self.AddMatchString(re.compile(b'Nm([io])([1-9]|1[0-2]),([ \S]{0,32})\r\n'), self.__MatchMatrixIONameStatus, None)
            self.AddMatchString(re.compile(b'Ds[gG]2([0-9]{2})([0-9]{2})\*([-][0-9]{1,4}|0|[0-9]{1,3})\r\n'), self.__MatchMixpointGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]2([0-9]{2})([0-9]{2})\*(0|1)\r\n'), self.__MatchMixpointMute, None)
            self.AddMatchString(re.compile(b'AfmtO(\d{1,2})\*([0-2])\r\n'), self.__MatchOutputAudioSelect, 'Single')
            self.AddMatchString(re.compile(b'AfmtO00\*([0-2]{14})\r\n'), self.__MatchOutputAudioSelect, 'All')
            self.AddMatchString(re.compile(b'Ds[gG]601(0[0-9]|1[0-9]|2[0-3])\*([0-9 -]{1,4})\r\n'), self.__MatchHDMIDTPPostmixerTrim, None)
            self.AddMatchString(re.compile(b'HdcpI(\d{1,2}[ab]?)\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO(([0-9]){1,2}(A|B|a|b|))\*([012])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Rate(\d{1,2})\*(\d{1,3})\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'DsZ400([0-4][0-9])\*([01])\r\n'), self.__MatchPhantomPower, None)
            self.AddMatchString(re.compile(b'PsavM?([0129])\r\n'), self.__MatchPowerSaveMode, None) # SIS manual says there is a M but based on testing there isn't
            self.AddMatchString(re.compile(b'Ds[gG]301([0-2][0-9])\*([0-9 -]{1,4})\r\n'), self.__MatchPrematrixTrim, None)
            self.AddMatchString(re.compile(b'Ds[gG]500([0-2][0-9])\*([-]\d{1,4}|\d{1,3})\r\n'), self.__MatchPostMatrixGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]500([0-2][0-9])\*(0|1)\r\n'), self.__MatchPostMatrixMute, None)
            self.AddMatchString(re.compile(b'Sts00 +(\d+\.\d+) (\d+\.\d+)F (\d+\.\d+)C (\d+) (\d+) \d\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'UphnH1\*([01])\r\n'), self.__MatchUSBCallStatus, None)
            self.AddMatchString(re.compile(b'Vmut(([1-9]|1[0-2])(A|B|a|b|))\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(b'PrstR\d+\r\n'), self.__MatchQik, None)  # Response to a Set Preset Recall command
            self.AddMatchString(re.compile(b'Rpr\d+(?:\*\d+)?\r\n'), self.__MatchPreset, None) # FW 2.00+ changes to Rpr1\r\n
            self.AddMatchString(re.compile(b'Vgp00 Out1\*([0-9 -]*)Vid\r\nVgp00 Out1\*([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, None)
            self.AddMatchString(re.compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud))|(?:In(\d+) (All|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)

            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)             
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False
        self.UpdateAllMatrixTie( None, None)

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def __MatchQik(self, match, tag):

        self.UpdateAllMatrixTie( None, None)

    def __MatchPreset(self, match, tag):

        self.UpdateAllMatrixTie( None, None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSizeWAudio)] for _ in range(self.InputSize)]
        self.Send('w0*1*1VC\r\nw0*1*2VC\r\n')

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = range(output-1, output)
        else:
            output_range = range(self.OutputSizeWAudio)
        for input_ in range(self.InputSize):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):

        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = range(output-1, output)
        else:
            output_range = range(self.OutputSizeWAudio)

        matrixIONameStatus = self.ReadStatus('MatrixIONameStatus', {'Type': 'Output', 'Number': str(self.OutputSize)}) # used to check if 'Matrix IO Name Status' exists or not
        for input_ in range(self.InputSize):
            inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': str(input_+1)}) # get input name to write for 'Output Tie Status Name'
            for output in output_range:
                tietype = self.matrix_tie_status[input_][output]
                inputName = 'Untied' if not inputName else inputName # write 'Untied' for 'Output Tie Status Name' if no input name exists
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', str(input_+1), {'Output': str(output+1), 'Tie Type': tie_type})
                        if matrixIONameStatus: # only write 'Output Tie Status Name' if 'Matrix IO Name Status' has been written (prevents debug log error)
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output+1), 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output+1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_+1), {'Output': str(output+1), 'Tie Type': 'Audio'})
                    if matrixIONameStatus:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(output+1), 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output+1), 'Tie Type': 'Audio'})
                    AudioList.add(output)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output+1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_+1), {'Output': str(output+1), 'Tie Type': 'Video'})
                    if matrixIONameStatus:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(output+1), 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output+1), 'Tie Type': 'Video'})
                    VideoList.add(output)
        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o+1), 'Tie Type': 'Video'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o+1), 'Tie Type': 'Video'})
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o+1), 'Tie Type': 'Audio'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o+1), 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o+1), 'Tie Type': 'Audio/Video'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o+1), 'Tie Type': 'Audio/Video'})

    def __MatchAllMatrixTie(self, match, tag):

        ties = {
            'Video': match.group(1).decode(),
            'Audio': match.group(2).decode()
        }

        for tag, match in ties.items():
            opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

            for output, input_ in enumerate(match.strip().split()):
                if input_ in ['0', '-1']:
                    continue

                if self.matrix_tie_status[int(input_) - 1][int(output)] == opposite_tag:
                    self.matrix_tie_status[int(input_) - 1][int(output)] = 'Audio/Video'
                else:
                    self.matrix_tie_status[int(input_) - 1][int(output)] = tag

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetAmplifierAttenuation(self, value, qualifier):

        output = {
            '1' :'26',
            '2':'27'
        }

        if -100 <= int(value) <= 0 and qualifier['Output'] in output:
            commandString = 'WG600{0}*{1}AU\r'.format(output[qualifier['Output']],round(value*10))
            self.__SetHelper('AmplifierAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierAttenuation')

    def UpdateAmplifierAttenuation(self, value, qualifier):
        
        output = {
            '1' :'26',
            '2':'27'
        }
        
        if qualifier['Output'] in output:
            channel = output[qualifier['Output']]
            commandString = 'WG600{0}AU\r'.format(channel)
            self.__UpdateHelper('AmplifierAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmplifierAttenuation')
            
    def __MatchAmplifierAttenuation(self, match, qualifier):
        
        output = {
            '26':'1',
            '27':'2'
        }
        
        value = int(match.group(2))/10
        qualifier = {'Output' : output[match.group(1).decode()]}            
        self.WriteStatus('AmplifierAttenuation', value, qualifier)

    def SetAmplifierMute(self, value, qualifier):
        
        MuteState = {
            'On' :'1',
            'Off':'0'
        }

        output = {
            '1' :'26',
            '2':'27'
        }
        
        if value in MuteState and qualifier['Output'] in output:
            channel = output[qualifier['Output']]
            commandString = 'WM600{0}*{1}AU\r'.format(channel,MuteState[value])
            self.__SetHelper('AmplifierMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierMute')
            
    def UpdateAmplifierMute(self, value, qualifier):
        
        output = {
            '1' :'26',
            '2':'27'
        }
        
        if qualifier['Output'] in output:
            channel = output[qualifier['Output']]
            commandString = 'WM600{0}AU\r'.format(channel)
            self.__UpdateHelper('AmplifierMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmplifierMute')
            
    def __MatchAmplifierMute(self, match, qualifier):
        
        MuteState = {
            '1':'On',
            '0':'Off'
        }

        output = {
            '26':'1',
            '27':'2'
        }
        
        value = MuteState[match.group(2).decode()]
        qualifier = {'Output': output[match.group(1).decode()]}
        self.WriteStatus('AmplifierMute', value, qualifier)

    def UpdateAmplifierOutputMode(self, value, qualifier):

        AmplifierOutputModeCmdString = 'wSPKR\r'
        self.__UpdateHelper('AmplifierOutputMode', AmplifierOutputModeCmdString, value, qualifier)

    def __MatchAmplifierOutputMode(self, match, tag):

        ValueStateValues = {
            '1': 'Stereo, 4/8 ohms',
            '2': 'Bridged Mono, 8 ohms',
            '3': 'Bridged Mono, 70 volts',
            '4': 'Bridged Mono, 100 volts'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AmplifierOutputMode', value, None)

    def SetAmplifierPostmixerTrim(self, value, qualifier):
        
        output = {
            '1'  : '6',
            '2' : '7'
        }
        
        if -12 <= value <= 12 and qualifier['Output'] in output:
            AmplifierPostmixerTrimCmdString = 'WG6012{0}*{1}AU\r'.format(output[qualifier['Output']], round(value * 10))
            self.__SetHelper('AmplifierPostmixerTrim', AmplifierPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierPostmixerTrim')

    def UpdateAmplifierPostmixerTrim(self, value, qualifier):
        
        output = {
            '1'  : '6',
            '2' : '7'
        }
        
        if qualifier['Output'] in output:
            channel = output[qualifier['Output']]
            AmplifierPostmixerTrimCmdString = 'WG6012{0}AU\r'.format(channel)
            self.__UpdateHelper('AmplifierPostmixerTrim', AmplifierPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmplifierPostmixerTrim')

    def __MatchAmplifierPostmixerTrim(self, match, tag):
        
        output = {
            '6' : '1',
            '7' : '2'
        }

        qualifier = {'Output': output[match.group(1).decode()]}
        value = int(match.group(2).decode()) / 10
        self.WriteStatus('AmplifierPostmixerTrim', value, qualifier)

    def SetAnalogAttenuation(self, value, qualifier):
        
        output = {
            '1'  : '4',
            '2' : '5'
        }

        if qualifier['Output'] in output and -100 <= int(value) <= 0:
            level = round(value * 10)
            commandString = 'WG6002{0}*{1}AU\r'.format(output[qualifier['Output']], level)
            self.__SetHelper('AnalogAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogAttenuation')
            
    def UpdateAnalogAttenuation(self, value, qualifier):
        
        output = {
            '1'  : '4',
            '2' : '5'
        }

        if qualifier['Output'] in output:
            commandString = 'WG6002{0}AU\r'.format(output[qualifier['Output']])
            self.__UpdateHelper('AnalogAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogAttenuation')

    def __MatchAnalogAttenuation(self, match, tag):

        output = {
            '4': '1',
            '5': '2'
        }

        value = int(match.group(2).decode())/10
        self.WriteStatus('AnalogAttenuation', value, {'Output': output[match.group(1).decode()]})

    def SetAnalogMute(self, value, qualifier):

        MuteState = {
            'On'  : '1',
            'Off' : '0'
            }

        output = {
            '1' : '4',
            '2': '5'
            }

        if qualifier['Output'] in output:
            commandString = 'WM6002{0}*{1}AU\r'.format(output[qualifier['Output']], MuteState[value])
            self.__SetHelper('AnalogMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogMute')

    def UpdateAnalogMute(self, value, qualifier):

        output = {
            '1'  : '4',
            '2' : '5'
            }
        
        if qualifier['Output'] in output:
            commandString = 'WM6002{0}AU\r'.format(output[qualifier['Output']])
            self.__UpdateHelper('AnalogMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogMute')

    def __MatchAnalogMute(self, match, tag):

        MuteState = {
            '1' : 'On',
            '0' : 'Off'
            }
        
        output = {
            '4'  : '1',
            '5' : '2'
            }

        value = MuteState[match.group(2).decode()]
        self.WriteStatus('AnalogMute', value, {'Output': output[match.group(1).decode()]})

    def SetAnalogPostmixerTrim(self, value, qualifier):
        
        output = {
            '1'  : '4',
            '2' : '5'
        }
        
        if -12 <= value <= 12 and qualifier['Output'] in output:
            AnalogPostmixerTrimCmdString = 'WG6012{0}*{1}AU\r'.format(output[qualifier['Output']], round(value * 10))
            self.__SetHelper('AnalogPostmixerTrim', AnalogPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogPostmixerTrim')

    def UpdateAnalogPostmixerTrim(self, value, qualifier):
        
        output = {
            '1'  : '4',
            '2' : '5'
        }
        
        if qualifier['Output'] in output:
            channel = output[qualifier['Output']]
            AnalogPostmixerTrimCmdString = 'WG6012{0}AU\r'.format(channel)
            self.__UpdateHelper('AnalogPostmixerTrim', AnalogPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogPostmixerTrim')

    def __MatchAnalogPostmixerTrim(self, match, tag):
        
        output = {
            '4' : '1',
            '5' : '2'
        }

        qualifier = {'Output': output[match.group(1).decode()]}
        value = int(match.group(2).decode()) / 10
        self.WriteStatus('AnalogPostmixerTrim', value, qualifier)

    def SetATAttenuation(self, value, qualifier):


        tempOutput = int(qualifier['Output'])
        if -100 <= int(value) <= 0 and 1 <= tempOutput <= 32:
            level = round(value * 10)
            commandString = 'WG600{0:02d}*{1}AU\r'.format(tempOutput + 35, level)
            self.__SetHelper('ATAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATAttenuation')
            
    def UpdateATAttenuation(self, value, qualifier):
        
        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= 32:
            commandString = 'WG600{0:02d}AU\r'.format(tempOutput + 35)
            self.__UpdateHelper('ATAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATAttenuation')
            
    def __MatchATAttenuation(self, match, tag):

        output = int(match.group(1).decode()) - 35

        value = int(match.group(2).decode())/10
        self.WriteStatus('ATAttenuation', value, {'Output': str(output)})

    def SetATMute(self, value, qualifier):

        MuteState = {
            'On'  : '1',
            'Off' : '0'
            }

        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= 32:
            commandString = 'WM600{0:02d}*{1}AU\r'.format(tempOutput + 35, MuteState[value])
            self.__SetHelper('ATMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATMute')

    def UpdateATMute(self, value, qualifier):

        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= 32:
            commandString = 'WM600{0:02d}AU\r'.format(tempOutput + 35)
            self.__UpdateHelper('ATMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATMute')
            
    def __MatchATMute(self, match, tag):

        MuteState = {
            '1' : 'On',
            '0' : 'Off'
            }

        output = int(match.group(1).decode()) - 35
        value = MuteState[match.group(2).decode()]
        self.WriteStatus('ATMute', value, {'Output': str(output)})

    def SetATPostmixerTrim(self, value, qualifier):
        
        tempOutput = int(qualifier['Output'])
        if -12 <= value <= 12 and 1 <= tempOutput <= 32:
            ATPostmixerTrimCmdString = 'WG601{0:02d}*{1}AU\r'.format(tempOutput + 35, round(value * 10))
            self.__SetHelper('ATPostmixerTrim', ATPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATPostmixerTrim')

    def UpdateATPostmixerTrim(self, value, qualifier):
        
        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= 32:
            ATPostmixerTrimCmdString = 'WG601{0:02d}AU\r'.format(tempOutput + 35)
            self.__UpdateHelper('ATPostmixerTrim', ATPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATPostmixerTrim')

    def __MatchATPostmixerTrim(self, match, tag):
    
        output = int(match.group(1).decode()) - 35
        value = int(match.group(2).decode()) / 10
        self.WriteStatus('ATPostmixerTrim', value, {'Output': str(output)})

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill' : '1', 
            'Follow' : '2'
            }

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize and value in ValueStateValues:
            AspectRatioCmdString = 'w{0}*{1}ASPR\r\n'.format(tempInput, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize:
            AspectRatioCmdString = 'w{0}ASPR\r\n'.format(tempInput)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        InputStates = {
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
            12 : '12'
            }

        ValueStateValues = {
            '1' : 'Fill', 
            '2' : 'Follow'
            }

        tempInput = InputStates[int(match.group(1).decode())]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, {'Input':tempInput})

    def SetAutoImage(self, value, qualifier):

        ValuesStates = {
            'Execute': '0',
            'Execute and Fill': '1',
            'Execute and Follow': '2'
        }
        
        Output = qualifier['Output']
        if 1 <= int(Output) <= self.OutputSize:
            AutoImageCmdString = '{0}*{1}A'.format(Output, ValuesStates[value])
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetAutomixerGateMonitor(self, value, qualifier):

        input_ = int(qualifier['Input'])

        ValueStateValues = {
            'On': '1024',
            'Off': '0'
        }

        if 1 <= input_ <= 48 and value in ValueStateValues:
            AutomixerGateMonitorCmdString = 'wJ{}*{}AU\r'.format(58999 + input_, ValueStateValues[value])
            self.__SetHelper('AutomixerGateMonitor', AutomixerGateMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomixerGateMonitor')

    def UpdateAutomixerGateMonitor(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 48:
            AutomixerGateMonitorCmdString = 'wJ{}AU\r'.format(58999 + input_)
            self.__UpdateHelper('AutomixerGateMonitor', AutomixerGateMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutomixerGateMonitor')

    def __MatchAutomixerGateMonitor(self, match, tag):

        ValueStateValues = {
            '1024': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Input': str(int(match.group(1).decode()) + 1)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutomixerGateMonitor', value, qualifier)

    def __MatchAutomixerGateStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Opened',
            '0': 'Closed'
        }

        qualifier = {
            'Input': str(int(match.group(1).decode()) + 1)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutomixerGateStatus', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Mode 1' : '1X', 
            'Mode 2' : '2X', 
            'Off'    : '0X'
            }
        
        if value in ValueStateValues:
            ExecutiveModeCmdString = ValueStateValues[value]
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1' : 'Mode 1', 
            '2' : 'Mode 2', 
            '0' : 'Off'
            }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def UpdateFanSpeed(self, value, qualifier):

        if 1 <= int(qualifier['Fan']) <= 2:
            self.UpdateTemperature(None, {'Scale': 'Fahrenheit'})
        else:
            self.Discard('Invalid Command for UpdateFanSpeed')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
            }

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max'] and value in ValueStateValues:
            FreezeCmdString = '{0}*{1}F'.format(Output, ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max']:
            FreezeCmdString = '{0}F'.format(Output)
            self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
            }

        Output = int(match.group(1).decode())
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Freeze', value, {'Output':str(Output)})

    def SetFlexDigitalInputGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if -18 <= value <= 24:
            if 1 <= tempInput <= 48:
                level = round(value * 10)
                FlexDigitalInputGainCmdString = 'wH{0}*{1:05d}AU\r\n'.format(tempInput + 39999, level)
                self.__SetHelper('FlexDigitalInputGain', FlexDigitalInputGainCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetFlexDigitalInputGain')
        else:
            self.Discard('Invalid Command for SetFlexDigitalInputGain')

    def UpdateFlexDigitalInputGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 48:
            FlexDigitalInputGainCmdString = 'wH{0}AU\r'.format(tempInput + 39999)
            self.__UpdateHelper('FlexDigitalInputGain', FlexDigitalInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexDigitalInputGain')

    def __MatchFlexDigitalInputGain(self, match, tag):

        qualifier = {'Input': str(int(match.group(1)) + 1)}
        value = int(match.group(2)) / 10
        self.WriteStatus('FlexDigitalInputGain', value, qualifier)

    def SetFlexInputMute(self, value, qualifier):

        ValueStateValues = {
            'On' :'1',
            'Off':'0'
            }

        tempinput = int(qualifier['Input'])
        if 1 <= tempinput <= 48 and value in ValueStateValues:
            commandString = 'wM{0}*{1}AU\r'.format(tempinput + 39999,ValueStateValues[value])
            self.__SetHelper('FlexInputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlexInputMute')

    def UpdateFlexInputMute(self, value, qualifier):

        tempinput = int(qualifier['Input'])
        if 1 <= tempinput <= 48:
            commandString = 'wM{0}AU\r'.format(tempinput + 39999)
            self.__UpdateHelper('FlexInputMute', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateFlexInputMute')

    def __MatchFlexInputMute(self, match, tag):

        ValueStateValues = {
            '1':'On',
            '0':'Off'
            }

        input_ = int(match.group(1).decode()) + 1
        qualifier = {'Input' : str(input_)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FlexInputMute', value, qualifier)

    def SetFlexAnalogInputGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if -18 <= value <= 80:
            if 1 <= tempInput <= 48:
                level = round(value * 10)
                FlexAnalogInputGainCmdString = 'wG{0}*{1:05d}AU\r\n'.format(tempInput + 39999, level)
                self.__SetHelper('FlexAnalogInputGain', FlexAnalogInputGainCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetFlexAnalogInputGain')
        else:
            self.Discard('Invalid Command for SetFlexAnalogInputGain')

    def UpdateFlexAnalogInputGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 48:
            FlexAnalogInputGainCmdString = 'wG{0}AU\r'.format(tempInput + 39999)
            self.__UpdateHelper('FlexAnalogInputGain', FlexAnalogInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexAnalogInputGain')

    def __MatchFlexAnalogInputGain(self, match, tag):

        qualifier = {'Input': str(int(match.group(1)) + 1)}
        value = int(match.group(2)) / 10
        self.WriteStatus('FlexAnalogInputGain', value, qualifier)

    def SetFlexInputSignalLevelMonitor(self, value, qualifier):

        input_ = int(qualifier['Input'])

        value = round(value, 1)
        if 1 <= input_ <= 48 and -150 <= value <= 0:
            FlexInputSignalLevelMonitorCmdString = 'wJ{}*{}AU\r'.format(39999 + input_, -int(value * 10))
            self.__SetHelper('FlexInputSignalLevelMonitor', FlexInputSignalLevelMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlexInputSignalLevelMonitor')

    def UpdateFlexInputSignalLevelMonitor(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 48:
            FlexInputSignalLevelMonitorCmdString = 'wJ{}AU\r'.format(39999 + input_)
            self.__UpdateHelper('FlexInputSignalLevelMonitor', FlexInputSignalLevelMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexInputSignalLevelMonitor')

    def __MatchFlexInputSignalLevelMonitor(self, match, tag):

        qualifier = {
            'Input': str(int(match.group(1).decode()) + 1)
        }

        value = -int(match.group(2).decode()) / 10
        if -150 <= value <= 0:
            self.WriteStatus('FlexInputSignalLevelMonitor', value, qualifier)

    def __MatchFlexInputSignalLevelStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Above',
            '1': 'Equal to or below'
        }

        qualifier = {
            'Input': str(int(match.group(1).decode()) + 1)
        }

        value = -int(match.group(2).decode()) / 10
        if -150 <= value <= 0:
            self.WriteStatus('FlexInputSignalLevelValue', value, qualifier)
        
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('FlexInputSignalLevelStatus', value, qualifier.copy())

    def SetFlexPremixerGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if -100 <= value <= 12:
            if 1 <= tempInput <= 48:
                level = round(value * 10)
                FlexPremixerGainCmdString = 'wG{0}*{1:05d}AU\r'.format(tempInput + 40099, level)
                self.__SetHelper('FlexPremixerGain', FlexPremixerGainCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetFlexPremixerGain')
        else:
            self.Discard('Invalid Command for SetFlexPremixerGain')

    def UpdateFlexPremixerGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 48:
            FlexPremixerGainCmdString = 'wG{0}AU\r'.format(tempInput + 40099)
            self.__UpdateHelper('FlexPremixerGain', FlexPremixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexPremixerGain')

    def __MatchFlexPremixerGain(self, match, tag):

        qualifier = {'Input': str(int(match.group(1)) + 1)}
        value = int(match.group(2)) / 10
        self.WriteStatus('FlexPremixerGain', value, qualifier)

    def SetFlexPremixerMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 48 and value in ValueStateValues:
            FlexPremixerMuteCmdString = 'wM{0}*{1}AU\r'.format(tempInput + 40099, ValueStateValues[value])
            self.__SetHelper('FlexPremixerMute', FlexPremixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlexPremixerMute')

    def UpdateFlexPremixerMute(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 48:
            FlexPremixerMuteCmdString = 'wM{0}AU\r'.format(tempInput + 40099)
            self.__UpdateHelper('FlexPremixerMute', FlexPremixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexPremixerMute')

    def __MatchFlexPremixerMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {'Input': str(int(match.group(1)) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FlexPremixerMute', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 64:
            PresetRecallCmdString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetGlobalVideoMute(self, value, qualifier):

        GlobalMuteState={
            'Video':'1',
            'Video & Sync':'2',
            'Off':'0'
            }
        
        if value in GlobalMuteState:
            self.__SetHelper('GlobalVideoMute', 'w{0}*VMUT\r'.format(GlobalMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')
            
    def __MatchGroup(self, match, tag):

        group = str(int(match.group(1)))
        if group in self.GroupFunction:
            command = self.GroupFunction[group]
            if command == 'GroupMute':
                GroupMuteStateNames = {
                        '1' : 'On',
                        '0' : 'Off'
                }
                qualifier = {'Group' : group} 
                value = match.group(2).decode()[-1]
                if value in GroupMuteStateNames:
                    self.WriteStatus(command, GroupMuteStateNames[value], qualifier)
                else:
                    self.Error(['Group Mute: Invalid/unexpected response'])
            elif command in ['GroupPremixerGain', 'GroupOutputAttenuation', 'GroupMixpoint', 'GroupPostmixerTrim', 'GroupPrematrixTrim']:
                qualifier = {'Group' : group}
                value = int(match.group(2))/10
                self.WriteStatus(command, value, qualifier)

    def SetGroupMixpoint(self, value, qualifier):

        group = qualifier['Group']
        if -100 <= int(value) <= 12:
            if 1 <= int(group) <= 64:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupMixpoint', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupMixpoint'
            else:
                self.Discard('Invalid Command for SetGroupMixpoint')
        else:
            self.Discard('Invalid Command for SetGroupMixpoint')

    def UpdateGroupMixpoint(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMixpoint', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMixpoint'
        else:
            self.Discard('Invalid Command for UpdateGroupMixpoint')

    def SetGroupMute(self, value, qualifier):

        MuteState = {
            'On':'1',
            'Off':'0'
        }

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and value in MuteState:
            commandString = 'WD{0}*{1}GRPM\r'.format(group,MuteState[value])
            self.__SetHelper('GroupMute', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMute'
        else:
            self.Discard('Invalid Command for SetGroupMute')      

    def UpdateGroupMute(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMute', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMute'
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if -100 <= int(value) <= 0:
            if 1 <= int(group) <= 64:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupOutputAttenuation', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupOutputAttenuation'
            else:
                self.Discard('Invalid Command for SetGroupOutputAttenuation')   
        else:
            self.Discard('Invalid Command for SetGroupOutputAttenuation')

    def UpdateGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupOutputAttenuation', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
        else:
            self.Discard('Invalid Command for UpdateGroupOutputAttenuation')

    def SetGroupPremixerGain(self, value, qualifier):

        group = qualifier['Group']
        if -100 <= int(value) <= 12:
            if 1 <= int(group) <= 64:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupPremixerGain', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupPremixerGain'
            else:
                self.Discard('Invalid Command for SetGroupPremixerGain') 
        else:
            self.Discard('Invalid Command for SetGroupPremixerGain')

    def UpdateGroupPremixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPremixerGain', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupPremixerGain'
        else:
            self.Discard('Invalid Command for UpdateGroupPremixerGain')

    def SetGroupPrematrixTrim(self, value, qualifier):

        group = qualifier['Group']
        if -12 <= int(value) <= 12:
            if 1 <= int(group) <= 64:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupPrematrixTrim', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupPrematrixTrim'
            else:
                self.Discard('Invalid Command for SetGroupPrematrixTrim')  
        else:
            self.Discard('Invalid Command for SetGroupPrematrixTrim')

    def UpdateGroupPrematrixTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPrematrixTrim', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupPrematrixTrim'
        else:
            self.Discard('Invalid Command for UpdateGroupPrematrixTrim')

    def SetGroupPostmixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if -12 <= int(value) <= 12:
            if 1 <= int(group) <= 64:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupPostmixerTrim', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupPostmixerTrim'
            else:
                self.Discard('Invalid Command for SetGroupPostmixerTrim')     
        else:
            self.Discard('Invalid Command for SetGroupPostmixerTrim')

    def UpdateGroupPostmixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPostmixerTrim', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupPostmixerTrim'
        else:
            self.Discard('Invalid Command for UpdateGroupPostmixerTrim')

    def SetInputAudioSwitchMode(self, value, qualifier):

        input_ = int(qualifier['Input'])

        ValueStateValues = {
            'Auto'   : '0', 
            'Digital': '1',
            'Analog' : '2'
        }

        if input_ in [5, 6, 9, 10, 11, 12] and value in ValueStateValues:
            InputAudioSwitchModeCmdString = 'wI{0}*{1}AFMT\r\n'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('InputAudioSwitchMode', InputAudioSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputAudioSwitchMode')

    def UpdateInputAudioSwitchMode(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if input_ in [5, 6, 9, 10, 11, 12]:
            InputAudioSwitchModeCmdString = 'wIAFMT\r\n'
            self.__UpdateHelper('InputAudioSwitchMode', InputAudioSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputAudioSwitchMode')

    def __MatchInputAudioSwitchMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Auto', 
            '1' : 'Digital',
            '2' : 'Analog'
            }
        
        if tag == 'Single':
            tempInput = int(match.group(1).decode())
            if tempInput in [5, 6, 9, 10, 11, 12]:
                value = ValueStateValues[match.group(2).decode()]
                self.WriteStatus('InputAudioSwitchMode', value, {'Input': str(tempInput)})
        else:
            tempInput = 0
            for i in match.group(1).decode():
                tempInput = tempInput + 1
                if tempInput in [5, 6, 9, 10, 11, 12]:
                    value = ValueStateValues[i]
                    self.WriteStatus('InputAudioSwitchMode', value, {'Input':str(tempInput)})

    def SetInputConnectorType(self, value, qualifier):

        input_ = int(qualifier['Input'])

        ValueStateValues = {
            'TP':   '1', # Naming of this value follows PCS
            'HDMI': '2'
        }

        if 5 <= input_ <= 6 and value in ValueStateValues:
            InputConnectorTypeCmdString = 'w{}*{}ITYP\r\n'.format(input_, ValueStateValues[value])
            self.__SetHelper('InputConnectorType', InputConnectorTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputConnectorType')

    def UpdateInputConnectorType(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 5 <= input_ <= 6:
            InputConnectorTypeCmdString = 'w{}ITYP\r\n'.format(input_)
            self.__UpdateHelper('InputConnectorType', InputConnectorTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputConnectorType')

    def __MatchInputConnectorType(self, match, tag):

        ValueStateValues = {
            '1': 'TP',
            '2': 'HDMI'
        }

        qualifier = {
            'Input': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputConnectorType', value, qualifier)

    def SetInputGain(self, value, qualifier):

        formatStates = {
            'Analog'  : 'G',
            'Digital' : 'H'
            }

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        tempInput = int(qualifier['Input'])
        tempFormat = qualifier['Format']
        channel = qualifier['L/R']
        if -18 <= value <= 24:
            if 1 <= tempInput <= self.InputSize:
                if tempFormat in formatStates and channel in channelStates:
                    formatValue = formatStates[tempFormat]
                    level = round(value * 10)
                    channelValue = (tempInput * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1

                    InputGainCmdString = 'w{0}{1}*{2:05d}AU\r'.format(formatValue, channelValue + 30000, level)
                    self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetInputGain')
            else:
                self.Discard('Invalid Command for SetInputGain')
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        formatStates = {
            'Analog': 'G',
            'Digital': 'H'
            }

        channelStates = {
            'Left': 0,
            'Right': 1
            }

        tempInput = int(qualifier['Input'])
        tempFormat = qualifier['Format']
        channel = qualifier['L/R']
        if 1 <= tempInput <= self.InputSize:
            if tempFormat in formatStates and channel in channelStates:
                formatValue = formatStates[tempFormat]

                channelValue = (tempInput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                InputGainCmdString = 'w{0}{1}AU\r'.format(formatValue, channelValue + 30000)
                self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateInputGain')
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        formatStates = {
            'G': 'Analog',
            'H': 'Digital'
            }

        qualifier = {}
        qualifier['Format'] = formatStates[match.group(1).decode().upper()]
        inputValue = int(match.group(2).decode())  # Even
        if inputValue % 2 == 0:
            channelValue = int((inputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:  # Odd
            channelValue = int((inputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Input'] = str(channelValue)

        value = int(match.group(3).decode()) / 10
        self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        channelStates = {
            'Left': 0,
            'Right': 1
            }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        channel = qualifier['L/R']
        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= self.InputSize and value in ValueStateValues:
            if channel in channelStates:
                channelValue = (tempInput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                InputMuteCmdString = 'wM{0}*{1}AU\r'.format(channelValue + 30000, ValueStateValues[value])
                self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInputMute')
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        channelStates = {
            'Left': 0,
            'Right': 1
            }

        channel = qualifier['L/R']
        tempInput = int(qualifier['Input'])
        if channel in channelStates:
            channelValue = (tempInput * 2) - 2
            if channel == 'Right':
                channelValue = channelValue + 1
            InputMuteCmdString = 'wM{0}AU\r'.format(channelValue + 30000)
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        MuteStateNames = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        inputValue = int(match.group(1).decode())  # Even
        if inputValue % 2 == 0:
            channelValue = int((inputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:  # Odd
            channelValue = int((inputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Input'] = str(channelValue)

        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetHDCPInputAuthorization(self, value, qualifier):

        InputStates = [
            '1',
            '2',
            '3',
            '4',
            '5A',
            '5B',
            '6A',
            '6B',
            '7',
            '8',
            '9',
            '10',
            '11',
            '12'
        ]
        input_ = qualifier['Input']
        
        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        if input_ in InputStates and value in ValueStateValues:
            HDCPAuthorizationCmdString = 'wE{0}*{1}HDCP\r\n'.format(input_.lower(), ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        InputStates = [
            '1',
            '2',
            '3',
            '4',
            '5A',
            '5B',
            '6A',
            '6B',
            '7',
            '8',
            '9',
            '10',
            '11',
            '12'
        ]
        input_ = qualifier['Input']

        if input_ in InputStates:
            HDCPAuthorizationCmdString = 'wE{0}HDCP\r\n'.format(input_.lower())
            self.__UpdateHelper('HDCPInputAuthorization', HDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        tempInput = match.group(1).decode().upper()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'Input': tempInput})

    def UpdateInputSignalStatus(self, value, qualifier):

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize:
            InputSignalCmdString = 'w0LS\r'
            self.__UpdateHelper('InputSignalStatus', InputSignalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'Active', 
            '0' : 'Not Active'
            }

        signal = match.group(1).decode()
        inputNumber = 1
        for inputVal in signal:
            self.WriteStatus('InputSignalStatus', ValueStateValues[inputVal], {'Input':str(inputNumber)})
            inputNumber += 1

    def SetLogo(self, value, qualifier):

        ValueStateValues = {
            '1'   : '1', 
            '2'   : '2', 
            '3'   : '3', 
            '4'   : '4', 
            '5'   : '5', 
            '6'   : '6', 
            '7'   : '7', 
            '8'   : '8', 
            '9'   : '9', 
            '10'  : '10', 
            '11'  : '11', 
            '12'  : '12', 
            '13'  : '13', 
            '14'  : '14', 
            '15'  : '15', 
            '16'  : '16', 
            'Off' : '0'
            }

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max'] and value in ValueStateValues:
            LogoCmdString = 'wE{0}*{1}LOGO\r'.format(Output, ValueStateValues[value])
            self.__SetHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogo')

    def UpdateLogo(self, value, qualifier):

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max']:
            LogoCmdString = 'wE{0}LOGO\r'.format(Output)
            self.__UpdateHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogo')

    def __MatchLogo(self, match, tag):


        ValueStateValues = {
            '1'  : '1',
            '2'  : '2', 
            '3'  : '3', 
            '4'  : '4', 
            '5'  : '5', 
            '6'  : '6', 
            '7'  : '7', 
            '8'  : '8', 
            '9'  : '9', 
            '10' : '10', 
            '11' : '11', 
            '12' : '12', 
            '13' : '13', 
            '14' : '14', 
            '15' : '15', 
            '16' : '16',              
            '0'  : 'Off',
            '-1' : 'Off'
            }

        Output = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Logo', value, {'Output':Output})

    def SetMixpointGain(self, value, qualifier):

        tempInput = qualifier['Input']
        output = qualifier['Output']
        if -100 <= int(value) <= 12:            
            commandString = 'WG2{0}{1}*{2}AU\r'.format(self.MixPointInputs[tempInput], self.MixPointOutputs[output],round(value*10))
            self.__SetHelper('MixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointGain')
            
    def UpdateMixpointGain(self, value, qualifier):

        tempInput = qualifier['Input']
        output = qualifier['Output']
                
        commandString = 'WG2{0}{1}AU\r'.format(self.MixPointInputs[tempInput], self.MixPointOutputs[output])
        self.__UpdateHelper('MixpointGain', commandString, value, qualifier)

    def __MatchMixpointGain(self, match, qualifier):
        
        tempInput = self.MixPointInputsStatus[match.group(1).decode()]
        Output = self.MixPointOutputsStatus[match.group(2).decode()]
        
        qualifier = {'Input': tempInput, 'Output': Output}
        value = int(match.group(3).decode()) / 10
        self.WriteStatus('MixpointGain', value, qualifier)

    def SetMixpointMute(self, value, qualifier):

        ValueStates = {
            'On': 1,
            'Off': 0
            }

        tempInput = qualifier['Input']
        output = qualifier['Output']
        
        if value in ValueStates:
            commandString = 'WM2{0}{1}*{2}AU\r'.format(self.MixPointInputs[tempInput], self.MixPointOutputs[output],ValueStates[value])
            self.__SetHelper('MixpointMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointMute')

    def UpdateMixpointMute(self, value, qualifier):

        tempInput = qualifier['Input']
        output = qualifier['Output']

        commandString = 'WM2{0}{1}AU\r'.format(self.MixPointInputs[tempInput], self.MixPointOutputs[output])
        self.__UpdateHelper('MixpointMute', commandString, value, qualifier)

    def __MatchMixpointMute(self, match, qualifier):

        MuteState = {
            '1':'On',
            '0':'Off'
        }

        tempInput = self.MixPointInputsStatus[match.group(1).decode()]
        Output = self.MixPointOutputsStatus[match.group(2).decode()]
        
        qualifier = {'Input': tempInput, 'Output': Output}
        value = MuteState[match.group(3).decode()]
        self.WriteStatus('MixpointMute', value, qualifier)

    def SetMatrixIONameCommand(self, value, qualifier):

        TypeStates = {
            'Input': 'NI',
            'Output': 'NO'
        }

        number = qualifier['Number']
        name = qualifier['Name']
        if number and name and 0 <= len(name) <= 32 and qualifier['Type'] in TypeStates:
            cmdstring = 'w{0},{1}{2}\r'.format(number, name, TypeStates[qualifier['Type']])
            cmdstring = cmdstring.encode(encoding='iso-8859-1')
            self.__SetHelper('MatrixIONameCommand', cmdstring, None, None)
            if qualifier['Type'] == 'Input': #only write the name if it's for input
                for x in range(1, self.OutputSize + 1):
                    audioVal = self.ReadStatus('OutputTieStatus', {'Output': str(x), 'Tie Type': 'Audio'}) # get audio input
                    videoVal = self.ReadStatus('OutputTieStatus', {'Output': str(x), 'Tie Type': 'Video'}) # get video input
                    if audioVal == number:
                        self.WriteStatus('OutputTieStatusName', name, {'Output': str(x), 'Tie Type': 'Audio'})
                    if videoVal == number:
                        self.WriteStatus('OutputTieStatusName', name, {'Output': str(x), 'Tie Type': 'Video'})
                    if audioVal == videoVal == number: # if video input is the same as audio input
                        self.WriteStatus('OutputTieStatusName', name, {'Output': str(x), 'Tie Type': 'Audio/Video'}) # write AV name
        else:
            self.Discard('Invalid Command for SetMatrixIONameCommand')

    def SetMatrixIONameStatus(self, query, qualifier):

        self.Send(query, pacing=0.1) # 100 pacing between queries

    def __MatchMatrixIONameStatus(self, match, tag):

        TypeStates = {
            'i': 'Input',
            'o': 'Output'
        }

        type_ = TypeStates[match.group(1).decode()]
        number = match.group(2).decode()
        value = match.group(3).decode()
        self.WriteStatus('MatrixIONameStatus', value, {'Type': type_, 'Number': number})
        if type_ == 'Input': # only write the name if type is input
            for x in range(1, self.OutputSize + 1):
                audioVal = self.ReadStatus('OutputTieStatus', {'Output': str(x), 'Tie Type': 'Audio'}) # get audio input
                videoVal = self.ReadStatus('OutputTieStatus', {'Output': str(x), 'Tie Type': 'Video'}) # get video input
                if audioVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(x), 'Tie Type': 'Audio'})
                if videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(x), 'Tie Type': 'Video'})
                if audioVal == videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(x), 'Tie Type': 'Audio/Video'})

    def SetRefreshMatrixIONames(self, value, qualifier):

        for input_ in range(1, self.InputSize + 1):
            self.SetMatrixIONameStatus( 'w{}NI\r'.format(input_), None)
        for output in range(1, self.OutputSize + 1):
            self.SetMatrixIONameStatus( 'w{}NO\r'.format(output), None)
            
    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeStates = {
            'Audio'       : '$', 
            'Audio/Video' : '!', 
            'Video'       : '%'
        }
        tempInput = qualifier['Input']
        Output = qualifier['Output']
        
        if 0 <= int(tempInput) <= self.InputSize and qualifier['Tie Type'] in TieTypeStates:
            Tie = TieTypeStates[qualifier['Tie Type']]
            if Output == 'All':
                MatrixTieCommandCmdString = '{0}*{1}\r\n'.format(tempInput,  Tie)
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            elif 1 <= int(Output) <= self.OutputSizeWAudio:
                MatrixTieCommandCmdString = '{0}*{1}{2}\r\n'.format(tempInput,  Output, Tie)
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def SetOutputAudioSelect(self, value, qualifier):

        ValueStateValues = {
            'Original': '0',
            'From DSP': '1',
            'No Audio': '2'
        }

        Output = qualifier['Output']
        if 1 <= int(Output) <= self.OutputSize and value in ValueStateValues:
            OutputAudioSelectCmdString = 'wO{0}*{1}AFMT\r\n'.format(Output, ValueStateValues[value])
            self.__SetHelper('OutputAudioSelect', OutputAudioSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAudioSelect')

    def UpdateOutputAudioSelect(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputAudioSelectCmdString = 'wOAFMT\r\n'
            self.__UpdateHelper('OutputAudioSelect', OutputAudioSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputAudioSelect')

    def __MatchOutputAudioSelect(self, match, tag):

        ValueStateValues = {
            '0' : 'Original',
            '1' : 'From DSP',
            '2' : 'No Audio'
        }

        if tag == 'Single':
            Output = str(int(match.group(1).decode()))
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('OutputAudioSelect', value, {'Output':Output})
        else:
            Output = 0
            for i in match.group(1).decode():
                value = ValueStateValues[i]
                Output += 1
                self.WriteStatus('OutputAudioSelect', value, {'Output':str(Output)})

    def UpdateHDCPInputStatus(self, value, qualifier):

        InputStates = [
            '1',
            '2',
            '3',
            '4',
            '5A',
            '5B',
            '6A',
            '6B',
            '7',
            '8',
            '9',
            '10',
            '11',
            '12'
        ]
        input_ = qualifier['Input']

        if input_ in InputStates:
            HDCPInputStatusCmdString = 'wI{0}HDCP\r'.format(input_.lower())
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')
            
    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No Source Connected', 
            '1' : 'HDCP Content', 
            '2' : 'No HDCP Content'
            }

        qualifier = {'Input': (match.group(1).decode().upper())}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        
        if qualifier['Output'] in self.OutputStates:
            HDCPOutputStatusCmdString = 'wO{0}HDCP\r'.format(self.OutputStates[qualifier['Output']])
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')
            
    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No monitor connected',
            '1' : 'Monitor connected, not encrypted', 
            '2' : 'Monitor connected, currently encrypted'
        }

        Output = self.OutputStates[match.group(1).decode().upper()]
        value = ValueStateValues[match.group(4).decode()]
        self.WriteStatus('HDCPOutputStatus', value, {'Output': Output})

    def SetHDMIDTPAttenuation(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if -100 <= int(value) <= 0:
            if self.DTPConstraints['Min'] <= tempOutput <= self.DTPConstraints['Max']:
                if channel in channelStates:
                    level = round(value * 10)
                    channelValue = (tempOutput * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1

                    commandString = 'WG600{0:02d}*{1}AU\r'.format(channelValue, level)
                    self.__SetHelper('HDMIDTPAttenuation', commandString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetHDMIDTPAttenuation')
            else:
                self.Discard('Invalid Command for SetHDMIDTPAttenuation')
        else:
            self.Discard('Invalid Command for SetHDMIDTPAttenuation')

    def UpdateHDMIDTPAttenuation(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if self.DTPConstraints['Min'] <= tempOutput <= self.DTPConstraints['Max']:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WG600{0:02d}AU\r'.format(channelValue)
                self.__UpdateHelper('HDMIDTPAttenuation', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateHDMIDTPAttenuation')
        else:
            self.Discard('Invalid Command for UpdateHDMIDTPAttenuation')

    def __MatchHDMIDTPAttenuation(self, match, tag):

        qualifier = {}
        OutputValue = int(match.group(1).decode())  #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:   #Odd
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = int(match.group(2).decode())/10
        self.WriteStatus('HDMIDTPAttenuation', value, qualifier)

    def SetHDMIDTPMute(self, value, qualifier):

        MuteState = {
            'On'  : '1',
            'Off' : '0'
            }

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if self.DTPConstraints['Min'] <= tempOutput <= self.DTPConstraints['Max'] and value in MuteState:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM600{0:02d}*{1}AU\r'.format(channelValue, MuteState[value])
                self.__SetHelper('HDMIDTPMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetHDMIDTPMute')
        else:
            self.Discard('Invalid Command for SetHDMIDTPMute')

    def UpdateHDMIDTPMute(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if self.DTPConstraints['Min'] <= tempOutput <= self.DTPConstraints['Max']:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM600{0:02d}AU\r'.format(channelValue)
                self.__UpdateHelper('HDMIDTPMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateHDMIDTPMute')
        else:
            self.Discard('Invalid Command for UpdateHDMIDTPMute')

    def __MatchHDMIDTPMute(self, match, tag):

        MuteState = {
            '1' : 'On',
            '0' : 'Off'
            }

        qualifier = {}
        OutputValue = int(match.group(1).decode())  #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = MuteState[match.group(2).decode()]
        self.WriteStatus('HDMIDTPMute', value, qualifier)

    def SetHDMIDTPPostmixerTrim(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        output = int(qualifier['Output'])
        channel = qualifier['L/R']
        if -12 <= value <= 12:
            if 1 <= output <= self.OutputSize:
                if channel in channelStates:
                    level = round(value * 10)
                    channelValue = (output * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1
                    HDMIDTPPostmixerTrimCmdString = 'wG601{0:02d}*{1}AU\r'.format(channelValue, level)
                    self.__SetHelper('HDMIDTPPostmixerTrim', HDMIDTPPostmixerTrimCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetHDMIDTPPostmixerTrim')
            else:
                self.Discard('Invalid Command for SetHDMIDTPPostmixerTrim')
        else:
            self.Discard('Invalid Command for SetHDMIDTPPostmixerTrim')

    def UpdateHDMIDTPPostmixerTrim(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        output = int(qualifier['Output'])
        channel = qualifier['L/R']
        if 1 <= output <= self.OutputSize:
            if channel in channelStates:
                channelValue = (output * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1
                HDMIDTPPostmixerTrimCmdString = 'wG601{0:02d}AU\r'.format(channelValue)
                self.__UpdateHelper('HDMIDTPPostmixerTrim', HDMIDTPPostmixerTrimCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateHDMIDTPPostmixerTrim')
        else:
            self.Discard('Invalid Command for UpdateHDMIDTPPostmixerTrim')

    def __MatchHDMIDTPPostmixerTrim(self, match, tag):

        qualifier = {}
        outputValue = int(match.group(1).decode())
        if outputValue % 2 == 0:  # Even
            channelValue = int((outputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:  # Odd
            channelValue = int((outputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = int(match.group(2)) / 10
        self.WriteStatus('HDMIDTPPostmixerTrim', value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '640x480 (60Hz)'            : '10', 
            '800x600 (60Hz)'            : '11', 
            '1024x768 (60Hz)'           : '12', 
            '1280x768 (60Hz)'           : '13', 
            '1280x800 (60Hz)'           : '14', 
            '1280x1024 (60Hz)'          : '15', 
            '1360x768 (60Hz)'           : '16', 
            '1366x768 (60Hz)'           : '17', 
            '1440x900 (60Hz)'           : '18', 
            '1400x1050 (60Hz)'          : '19', 
            '1600x900 (60Hz)'           : '20', 
            '1680x1050 (60Hz)'          : '21', 
            '1600x1200 (60Hz)'          : '22', 
            '1920x1200 (60Hz)'          : '23', 
            '480p (59.94Hz)'            : '24', 
            '480p (60Hz)'               : '25', 
            '576p (50Hz)'               : '26',  
            '720p (25Hz)'               : '29', 
            '720p (29.97Hz)'            : '30', 
            '720p (30Hz)'               : '31', 
            '720p (50Hz)'               : '32', 
            '720p (59.94Hz)'            : '33', 
            '720p (60Hz)'               : '34', 
            '1080i (50Hz)'              : '35', 
            '1080i (59.94Hz)'           : '36', 
            '1080i (60Hz)'              : '37', 
            '1080p (23.98Hz)'           : '38', 
            '1080p (24Hz)'              : '39', 
            '1080p (25Hz)'              : '40', 
            '1080p (29.97Hz)'           : '41', 
            '1080p (30Hz)'              : '42', 
            '1080p (50Hz)'              : '43', 
            '1080p (59.94Hz)'           : '44', 
            '1080p (60Hz)'              : '45', 
            '2048x1080 (23.98Hz)'       : '46', 
            '2048x1080 (24Hz)'          : '47', 
            '2048x1080 (25Hz)'          : '48', 
            '2048x1080 (29.97Hz)'       : '49', 
            '2048x1080 (30Hz)'          : '50', 
            '2048x1080 (50Hz)'          : '51', 
            '2048x1080 (59.94Hz)'       : '52', 
            '2048x1080 (60Hz)'          : '53',  
            '2048x1200 (60Hz)'          : '54', 
            '2048x1536 (60Hz)'          : '55', 
            '2560x1080 (60Hz)'          : '56', 
            '2560x1440 (60Hz)'          : '57', 
            '2560x1600 (60Hz)'          : '58', 
            '3840x2160 (23.98Hz)'       : '59', 
            '3840x2160 (24Hz)'          : '60', 
            '3840x2160 (25Hz)'          : '61', 
            '3840x2160 (29.97Hz)'       : '62', 
            '3840x2160 (30Hz)'          : '63',
            '3840x2160 (50Hz)'          : '64',
            '3840x2160 (59.94Hz)'       : '65',
            '3840x2160 (60Hz)'          : '66',
            '4096x2160 (23.98Hz)'       : '69', 
            '4096x2160 (24Hz)'          : '70', 
            '4096x2160 (25Hz)'          : '71', 
            '4096x2160 (29.97Hz)'       : '72', 
            '4096x2160 (30Hz)'          : '73',
            '4096x2160 (50Hz)'          : '74',
            '4096x2160 (59.94Hz)'       : '75',
            '4096x2160 (60Hz)'          : '76' 
            }

        Output = qualifier['Output']        
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max'] and value in ValueStateValues:
            OutputResolutionCmdString = 'w{0}*{1}RATE\r\n'.format(Output, ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        Output = qualifier['Output']        
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max']:
            OutputResolutionCmdString = 'w{0}RATE\r\n'.format(Output)
            self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputResolution')

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            '10' : '640x480 (60Hz)', 
            '11' : '800x600 (60Hz)', 
            '12' : '1024x768 (60Hz)', 
            '13' : '1280x768 (60Hz)', 
            '14' : '1280x800 (60Hz)', 
            '15' : '1280x1024 (60Hz)', 
            '16' : '1360x768 (60Hz)', 
            '17' : '1366x768 (60Hz)', 
            '18' : '1440x900 (60Hz)', 
            '19' : '1400x1050 (60Hz)', 
            '20' : '1600x900 (60Hz)', 
            '21' : '1680x1050 (60Hz)', 
            '22' : '1600x1200 (60Hz)', 
            '23' : '1920x1200 (60Hz)', 
            '24' : '480p (59.94Hz)', 
            '25' : '480p (60Hz)', 
            '26' : '576p (50Hz)', 
            '29' : '720p (25Hz)', 
            '30' : '720p (29.97Hz)', 
            '31' : '720p (30Hz)', 
            '32' : '720p (50Hz)', 
            '33' : '720p (59.94Hz)', 
            '34' : '720p (60Hz)', 
            '35' : '1080i (50Hz)', 
            '36' : '1080i (59.94Hz)', 
            '37' : '1080i (60Hz)', 
            '38' : '1080p (23.98Hz)', 
            '39' : '1080p (24Hz)', 
            '40' : '1080p (25Hz)', 
            '41' : '1080p (29.97Hz)', 
            '42' : '1080p (30Hz)', 
            '43' : '1080p (50Hz)', 
            '44' : '1080p (59.94Hz)', 
            '45' : '1080p (60Hz)', 
            '46' : '2048x1080 (23.98Hz)', 
            '47' : '2048x1080 (24Hz)', 
            '48' : '2048x1080 (25Hz)', 
            '49' : '2048x1080 (29.97Hz)', 
            '50' : '2048x1080 (30Hz)', 
            '51' : '2048x1080 (50Hz)', 
            '52' : '2048x1080 (59.94Hz)', 
            '53' : '2048x1080 (60Hz)', 
            '54' : '2048x1200 (60Hz)', 
            '55' : '2048x1536 (60Hz)', 
            '56' : '2560x1080 (60Hz)', 
            '57' : '2560x1440 (60Hz)', 
            '58' : '2560x1600 (60Hz)', 
            '59' : '3840x2160 (23.98Hz)', 
            '60' : '3840x2160 (24Hz)', 
            '61' : '3840x2160 (25Hz)', 
            '62' : '3840x2160 (29.97Hz)', 
            '63' : '3840x2160 (30Hz)', 
            '64' : '3840x2160 (50Hz)', 
            '65' : '3840x2160 (59.94Hz)', 
            '66' : '3840x2160 (60Hz)', 
            '69' : '4096x2160 (23.98Hz)', 
            '70' : '4096x2160 (24Hz)', 
            '71' : '4096x2160 (25Hz)', 
            '72' : '4096x2160 (29.97Hz)', 
            '73' : '4096x2160 (30Hz)',
            '74' : '4096x2160 (50Hz)',
            '75' : '4096x2160 (59.94Hz)',
            '76' : '4096x2160 (60Hz)'
            }

        Output = str(int(match.group(1).decode()))
        value = ValueStateValues[str(int(match.group(2).decode()))]
        self.WriteStatus('OutputResolution', value, {'Output':Output})

    def __MatchOutputTieStatus(self, match, qualifier):
        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, qualifier):
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video',
        }
        output = int(match.group(1))
        input_ = int(match.group(2))
        tietype = TieTypeStates[match.group(3).decode()]

        if tietype == 'Audio/Video':
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output-1]
                if i != input_-1 and current_tie in ['Audio', 'Video', 'Audio/Video']:
                    self.matrix_tie_status[i][output-1] = 'Untied'
                elif i == input_-1:
                    self.matrix_tie_status[i][output-1] = 'Audio/Video'
        elif tietype in ['Video', 'Audio']:
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output-1]
                opTag = 'Audio' if tietype == 'Video' else 'Video'
                if i == input_-1:
                    if current_tie == opTag or current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output-1] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[i][output-1] = tietype
                elif input_ == 0 or i != input_-1:
                    if current_tie == tietype:
                        self.matrix_tie_status[i][output-1] = 'Untied'
                    elif current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output-1] = opTag

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, qualifier):
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video',
        }
        new_input = int(match.group(4))
        tietype = TieTypeStates[match.group(5).decode()]

        if tietype in ['Audio', 'Video']:
            op_tie_type = 'Audio' if tietype == 'Video' else 'Video'
            for output in range(self.OutputSizeWAudio):
                for input_ in range(self.InputSize):
                    if input_ == new_input-1:
                        if self.matrix_tie_status[input_][output] in [op_tie_type, 'Audio/Video']:
                            if output < self.OutputSize: # for regular outputs 1 - 12, merge tie normally
                                self.matrix_tie_status[input_][output] = 'Audio/Video'
                        else:
                            if output < self.OutputSize: # for regular outputs 1 - 12, write current tie normally
                                self.matrix_tie_status[input_][output] = tietype
                            elif output >= self.OutputSize and tietype == 'Audio': # for audio only outputs 13 - 14 that are audio only, only write if new tie is audio tie
                                self.matrix_tie_status[input_][output] = 'Audio'
                    else:
                        if self.matrix_tie_status[input_][output] == 'Audio/Video':
                            self.matrix_tie_status[input_][output] = op_tie_type
                        elif self.matrix_tie_status[input_][output] != op_tie_type:
                            self.matrix_tie_status[input_][output] = 'Untied'

        elif tietype == 'Audio/Video':
            for output in range(self.OutputSizeWAudio):
                for input_ in range(self.InputSize):
                    if input_ == new_input-1:
                        if output < self.OutputSize: # for regular outputs 1 - 12
                            self.matrix_tie_status[input_][output] = 'Audio/Video'
                        else: # for audio only outputs 13 - 14
                            self.matrix_tie_status[input_][output] = 'Audio'
                    else:
                        self.matrix_tie_status[input_][output] = 'Untied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetPhantomPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
            }
        
        if value in ValueStateValues and 1 <= int(qualifier['Input']) <= 48:
            PhantomPowerCmdString = 'wZ400{0:02d}*{1}AU\r'.format(int(qualifier['Input']) - 1, ValueStateValues[value])
            self.__SetHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhantomPower')

    def UpdatePhantomPower(self, value, qualifier):
        
        if 1 <= int(qualifier['Input']) <= 48:
            PhantomPowerCmdString = 'wZ400{0:02d}AU\r'.format(int(qualifier['Input']) - 1)
            self.__UpdateHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePhantomPower')

    def __MatchPhantomPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(2).decode()]
        inpt = int(match.group(1).decode()) + 1
        self.WriteStatus('PhantomPower', value, {'Input' : str(inpt)})

    def SetPowerSaveMode(self, value, qualifier):

        ValueStateValues = {
            'Off':      '0',
            'Mode 1':   '1',
            'Mode 2':   '2'
        }

        if value in ValueStateValues:
            PowerSaveModeCmdString = 'wM{}PSAV\r'.format(ValueStateValues[value])
            self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerSaveMode')

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = 'wMPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
            '9': 'Low Power (Over Temperature)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def UpdatePowerSupplyVoltage(self, value, qualifier):

        self.UpdateTemperature(None, {'Scale': 'Fahrenheit'})

    def SetPrematrixTrim(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        channel = qualifier['L/R']
        tempInput = int(qualifier['Input'])
        if -12 <= value <= 12:
            if 1 <= tempInput <= self.InputSize:
                if channel in channelStates:
                    level = round(value * 10)
                    channelValue = (tempInput * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1

                    PrematrixTrimCmdString = 'wG{0}*{1}AU\r'.format(channelValue + 30100, level)
                    self.__SetHelper('PrematrixTrim', PrematrixTrimCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetPrematrixTrim')
            else:
                self.Discard('Invalid Command for SetPrematrixTrim')
        else:
            self.Discard('Invalid Command for SetPrematrixTrim')

    def UpdatePrematrixTrim(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        tempInput = int(qualifier['Input'])
        channel = qualifier['L/R']
        if 1 <= tempInput <= self.InputSize:
            if channel in channelStates:
                channelValue = (tempInput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1
                PrematrixTrimCmdString = 'wG{0}AU\r'.format(channelValue + 30100)
                self.__UpdateHelper('PrematrixTrim', PrematrixTrimCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdatePrematrixTrim')
        else:
            self.Discard('Invalid Command for UpdatePrematrixTrim')

    def __MatchPrematrixTrim(self, match, tag):

        qualifier = {}
        inputValue = int(match.group(1).decode())  # Even
        if inputValue % 2 == 0:
            channelValue = int((inputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:  # Odd
            channelValue = int((inputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Input'] = str(channelValue)

        value = int(match.group(2).decode()) / 10
        self.WriteStatus('PrematrixTrim', value, qualifier)

    def SetPostMatrixGain(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        tempOutput = int(qualifier['Output'])
        channel = qualifier['L/R']
        if -100 <= int(value) <= 12:
            if 1 <= tempOutput <= self.OutputSizeWAudio:
                if channel in channelStates:
                    level = round(value * 10)
                    channelValue = (tempOutput * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1

                    PostMatrixGainCmdString = 'WG500{0:02d}*{1}AU\r'.format(channelValue, level)
                    self.__SetHelper('PostMatrixGain', PostMatrixGainCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetPostMatrixGain')
            else:
                self.Discard('Invalid Command for SetPostMatrixGain')     
        else:
            self.Discard('Invalid Command for SetPostMatrixGain')

    def UpdatePostMatrixGain(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        tempOutput = int(qualifier['Output'])
        channel = qualifier['L/R']
        if 1 <= tempOutput <= self.OutputSizeWAudio:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WG500{0:02d}AU\r'.format(channelValue)
                self.__UpdateHelper('PostMatrixGain', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdatePostMatrixGain')
        else:
            self.Discard('Invalid Command for UpdatePostMatrixGain')

    def __MatchPostMatrixGain(self, match, qualifier):

        qualifier = {}
        OutputValue = int(match.group(1).decode())  #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:   #Odd
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = int(match.group(2).decode()) / 10
        self.WriteStatus('PostMatrixGain', value, qualifier)

    def SetPostMatrixMute(self, value, qualifier):

        MuteState = {
            'On'  : '1',
            'Off' : '0'
            }

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= self.OutputSizeWAudio and value in MuteState:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM500{0:02d}*{1}AU\r'.format(channelValue, MuteState[value])
                self.__SetHelper('PostMatrixMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPostMatrixMute')
        else:
            self.Discard('Invalid Command for SetPostMatrixMute')   

    def UpdatePostMatrixMute(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
            }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= self.OutputSizeWAudio:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM500{0:02d}AU\r'.format(channelValue)
                self.__UpdateHelper('PostMatrixMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdatePostMatrixMute')
        else:
            self.Discard('Invalid Command for UpdatePostMatrixMute')

    def __MatchPostMatrixMute(self, match, qualifier):

        MuteState = {
            '1' : 'On',
            '0' : 'Off'
            }

        qualifier = {}
        OutputValue = int(match.group(1).decode())  #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:   #Odd
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = MuteState[match.group(2).decode()]
        self.WriteStatus('PostMatrixMute', value, qualifier)

    def SetRefreshMatrix(self, value, qualifier):

        self.UpdateAllMatrixTie(value, qualifier)

    def UpdateTemperature(self, value, qualifier):

        ScaleStates = [
            'Fahrenheit',
            'Celsius'
        ]
        scale = qualifier['Scale']

        if scale in ScaleStates:
            TemperatureCmdString = 'S'
            self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTemperature')

    def __MatchTemperature(self, match, tag):

        self.WriteStatus('PowerSupplyVoltage', round(float(match.group(1).decode()), 2), None)

        self.WriteStatus('Temperature', round(float(match.group(2).decode()), 2), {'Scale': 'Fahrenheit'})
        self.WriteStatus('Temperature', round(float(match.group(3).decode()), 2), {'Scale': 'Celsius'})

        self.WriteStatus('FanSpeed', int(match.group(4).decode()), {'Fan': '1'})
        self.WriteStatus('FanSpeed', int(match.group(5).decode()), {'Fan': '2'})

    def SetScalerPresetRecall(self, value, qualifier):

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max'] and 1 <= int(value) <= 32:
            ScalerPresetRecallCmdString = '2*{0}*{1}.\r\n'.format(Output, value)
            self.__SetHelper('ScalerPresetRecall', ScalerPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScalerPresetRecall')

    def UpdateUSBCallStatus(self, value, qualifier):

        USBCallStatusCmdString = 'wH1UPHN\r'
        self.__UpdateHelper('USBCallStatus', USBCallStatusCmdString, value, qualifier)

    def __MatchUSBCallStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'Active',
            '0' : 'Inactive'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBCallStatus', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Video'         : '1', 
            'Video & Sync'  : '2', 
            'Off'           : '0'
            }

        Output = qualifier['Output']
        if qualifier['Output'] == 'All' or (value in ValueStateValues and qualifier['Output'] in self.OutputStates):
            if Output == 'All':
                VideoMuteCmdString = 'w{0}*VMUT\r\n'.format(ValueStateValues[value])
            else:
                VideoMuteCmdString = 'w{0}*{1}VMUT\r\n'.format(self.OutputStates[Output], ValueStateValues[value])
                
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        Output = qualifier['Output']
        if Output != 'All' and qualifier['Output'] in self.OutputStates:
            VideoMuteCmdString = 'w{0}VMUT\r\n'.format(self.OutputStates[Output])
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'Video', 
            '2' : 'Video & Sync', 
            '0' : 'Off'
            }

        Output = self.OutputStates[match.group(1).decode().upper()]
        value = ValueStateValues[match.group(4).decode()]
        self.WriteStatus('VideoMute', value, {'Output':Output})

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
            '01' : 'Invalid input channel number (out of range)',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number (out of range)',
            '12' : 'Invalid output number (out of range)',
            '13' : 'Invalid value (out of range)',
            '14' : 'Invalid command for this configuration',
            '17' : 'Invalid command for signal type',
            '18' : 'System or command timed out',
            '22' : 'Busy',
            '24' : 'Privileges violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '28' : 'Bad filename or file not found',
            '33' : 'Bad file type or size (for logo assignment)'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: '+ match.group(0).decode().strip()])

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
