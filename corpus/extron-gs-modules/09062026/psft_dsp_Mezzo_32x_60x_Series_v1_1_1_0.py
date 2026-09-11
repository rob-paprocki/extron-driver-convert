# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
import re
import math

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
        self.Models = {
            'Mezzo 322 A': self.psft_25_4602_2Ch,
            'Mezzo 322 AD': self.psft_25_4602_2Ch,
            'Mezzo 602 AD': self.psft_25_4602_2Ch,
            'Mezzo 604 AD': self.psft_25_4602_4Ch,
            'Mezzo 324 AD': self.psft_25_4602_4Ch
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Blink': { 'Status': {}},
            'FaultStatus': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'MatrixLinearGain': {'Parameters':['Source','Output'], 'Status': {}},
            'MatrixMute': {'Parameters':['Source','Output'], 'Status': {}},
            'MatrixPreGain': {'Parameters':['Source'], 'Status': {}},
            'MatrixPreMute': {'Parameters':['Source'], 'Status': {}},
            'SlowMeterAliStatus': {'Parameters':['Type'], 'Status': {}},
            'SlowMeterAmpliStatus': {'Parameters':['Channel'], 'Status': {}},
            'Standby': { 'Status': {}},
            'UserGain': {'Parameters':['Channel'], 'Status': {}},
            'UserMute': {'Parameters':['Channel'], 'Status': {}},
            'WayGain': {'Parameters':['Channel'], 'Status': {}},
            'WayMute': {'Parameters':['Channel'], 'Status': {}},
        }

        FirmwareRegex       = re.compile(b'\x02MZO\x01\x00\xe0\xc0\x10\x10\x52\x60\x00\x00\x00'
                                         b'\x14\x00\x00\x00([\x00-\xFF]{20})[\x00-\xFF]{2,4}\x03')
        FaultStatusRegex    = re.compile(b'\x02MZO\x01\x00\xe1\xc2\x12\x11\x52\x56\xb6\x00\x00'
                                         b'\x01\x00\x00\x00([\x00-\x01]|\x1b[\x42\x43]|[\x04-\x12])([\x00-\xFF]{2,4})\x03')
        SMAliStatusRegex    = re.compile(b'\x02MZO\x01\x00\xe2\xc3\x13\x14\x52([\x00\x04\x08\x0c\x10\x14\x18\x1c]\xb0\x00\x00)'
                                         b'\x04\x00\x00\x00([\x00-\xFF]{4,8})([\x00-\xFF]{2,4})\x03')
        SMAmpliStatRegex    = re.compile(b'\x02MZO\x01\x00\xe3\xc4\x16\x15\x52([\xf4\xf8\xfc\x00][\xb0\xb1]\x00\x00)'
                                         b'\x04\x00\x00\x00([\x00-\xFF]{4,8})([\x00-\xFF]{2,4})\x03')
        LinearGainRegex     = re.compile(b'\x02MZO\x01\x00\xe2\xc2\x1d\x15\x52'
                                         b'([\x18\x1c\x20\x24\x28\x2c\x30\x34\x38\x3c\x40\x44\x48\x4c\x50\x54]\x30\x00\x00)'
                                         b'\x04\x00\x00\x00([\x00-\xFF]{4,8})([\x00-\xFF]{2,4})\x03')
        MuteRegex           = re.compile(b'\x02MZO\x01\x00\xe6\xc6\x16\x16\x52([\x58-\x67]\x30\x00\x00)'
                                         b'\x01\x00\x00\x00(\x01|\x00)[\x00-\xFF]{2,4}\x03')
        PreGainRegex        = re.compile(b'\x02MZO\x01\x00\xe3\xc3\x1e\x16\x52([\x08|\x0c|\x10|\x14]\x30\x00\x00)'
                                         b'\x04\x00\x00\x00([\x00-\xFF]{4,8})([\x00-\xFF]{2,4})\x03')
        PreMuteRegex        = re.compile(b'\x02MZO\x01\x00\xe5\xc5\x1f\x14\x52([\x04-\x07]\x30\x00\x00)'
                                         b'\x01\x00\x00\x00(\x01|\x00)[\x00-\xFF]{2,4}\x03')
        UserGainRegex       = re.compile(b'\x02MZO\x01\x00\xe2\xc5\x1a\x12\x52([\x00|\x04|\x08|\x0c]\x40\x00\x00)'
                                         b'\x04\x00\x00\x00([\x00-\xFF]{4,8})([\x00-\xFF]{2,4})\x03')
        UserMuteRegex       = re.compile(b'\x02MZO\x01\x00\xe1\xc5\x1a\x18\x52([\x24-\x27]\x40\x00\x00)'
                                         b'\x01\x00\x00\x00(\x01|\x00)[\x00-\xFF]{2,4}\x03')
        WayGainRegex        = re.compile(b'\x02MZO\x01\x00\xe3\xc4\x15\x16\x52([\x10|\x14|\x18|\x1c]\x70\x00\x00)'
                                         b'\x04\x00\x00\x00([\x00-\xFF]{4,8})([\x00-\xFF]{2,4})\x03')
        WayMuteRegex        = re.compile(b'\x02MZO\x01\x00\xe6\xc7\x18\x19\x52([\x40|\x44|\x48|\x4c]\x70\x00\x00)'
                                         b'\x04\x00\x00\x00(\x01|\x00)\x00\x00\x00[\x00-\xFF]{2,4}\x03')
        ErrorRegex          = re.compile(b'\x02MZO\x01\x00[\x00-\xFF]{4}[\x52\x57][\x00-\xFF]{4,8}'
                                         b'\x00\x00\x00\x00[\x00-\xFF]{2,4}\x03')
        
        if self.Unidirectional == 'False':
            self.AddMatchString(FaultStatusRegex, self.__MatchFaultStatus, None)
            self.AddMatchString(FirmwareRegex, self.__MatchFirmwareVersion, None)
            self.AddMatchString(LinearGainRegex, self.__MatchMatrixLinearGain, None)
            self.AddMatchString(MuteRegex, self.__MatchMatrixMute, None)
            self.AddMatchString(PreGainRegex, self.__MatchMatrixPreGain, None)
            self.AddMatchString(PreMuteRegex, self.__MatchMatrixPreMute, None)
            self.AddMatchString(SMAliStatusRegex, self.__MatchSlowMeterAliStatus, None)
            self.AddMatchString(SMAmpliStatRegex, self.__MatchSlowMeterAmpliStatus, None)
            self.AddMatchString(UserGainRegex, self.__MatchUserGain, None)
            self.AddMatchString(UserMuteRegex, self.__MatchUserMute, None)
            self.AddMatchString(WayGainRegex, self.__MatchWayGain, None)
            self.AddMatchString(WayMuteRegex, self.__MatchWayMute, None)
            self.AddMatchString(ErrorRegex, self.__MatchError, None)

    def escape(self, data):
        Data = b''
        Escaped = {
            0x02: b'\x1b\x42', 
            0x03: b'\x1b\x43', 
            0x1b: b'\x1b\x5b'
            }
        for byte in data:
            if byte in Escaped:
                Data += Escaped[byte]
            else:
                Data += byte.to_bytes(1, byteorder='big')
        return Data
        
    def unescape(self, data):
        Data = b''
        Unescaped = {
            b'\x1b\x42': 0x02, 
            b'\x1b\x43': 0x03, 
            b'\x1b\x5b': 0x1b 
            }
        skip = False
        for byte in range(len(data)):
            if skip:
                skip = False
            else:
                if data[byte] == 0x1b:
                    Data += Unescaped[data[byte:byte + 2]].to_bytes(1, byteorder='big')
                    skip = True
                else:
                    Data += data[byte].to_bytes(1, byteorder='big')
        return Data
    
    def dBToLinear(self, dbValue):
        lin_val = math.pow(10, dbValue/20)
        return pack('<f', lin_val)
        
    def linearTodB(self, linearValue):
        try:
            float_val = unpack('<f', linearValue)[0]
            dB_val = 20 * math.log10(float_val)
            return round(dB_val, 1)
        except:
            return 'Unknown'
        
    def CalCRC(self, data):

        CRC_Table = [
            0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
            0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
            0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
            0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
            0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
            0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
            0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
            0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
            0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
            0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
            0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
            0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
            0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
            0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
            0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
            0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
            0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
            0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
            0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
            0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
            0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
            0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
            0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
            0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
            0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
            0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
            0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
            0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
            0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
            0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
            0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
            0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0,
            ]
    
        CRC = 0x00
        for ch in data:
            CRC = CRC_Table[((CRC >> 8) ^ ch) & 0xFF] ^ (CRC << 8)
        return pack('<H', int(CRC & 0xffff))
        
    def SetBlink(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01', 
            'Off' : b'\x00'
        }

        if value in ValueStateValues:
            initial_buffer = b''.join([b'\xe1\xc1\x11\x11\x57\x00\x00\x10\x00', 
                                   b'\x01\x00\x00\x00', ValueStateValues[value]])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            BlinkCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__SetHelper('Blink', BlinkCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBlink')

    def UpdateFaultStatus(self, value, qualifier):

        initial_buffer = b'\xe1\xc2\x12\x11\x52\x56\xb6\x00\x00\x01\x00\x00\x00'
        crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
        escaped_buffer = self.escape(crced_buffer)
        FaultStatusCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
        self.__UpdateHelper('FaultStatus', FaultStatusCmdString, value, qualifier)

    def __MatchFaultStatus(self, match, tag):

        ValueStateValues = {
            b'\x00'     : 'No Fault', 
            b'\x01'     : 'HWGoodT', 
            b'\x1b\x42' : 'PGoodPOn', 
            b'\x1b\x43' : 'CtrlVer', 
            b'\x04'     : 'RailsPOn', 
            b'\x05'     : 'RailsOverV', 
            b'\x06'     : 'RailsUnderV', 
            b'\x07'     : 'OutDC', 
            b'\x08'     : 'Fan Broken', 
            b'\x09'     : 'Fan Short', 
            b'\x0a'     : 'Fan Stuck', 
            b'\x0b'     : 'Software', 
            b'\x0c'     : 'MainBoardVer', 
            b'\x0d'     : 'PGoodMon', 
            b'\x0e'     : 'FuseBlown', 
            b'\x0f'     : 'PsuTemp', 
            b'\x10'     : 'HiFreq', 
            b'\x11'     : 'Model', 
            b'\x12'     : 'OverCurrPOn'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('FaultStatus', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        initial_buffer = b'\xe0\xc0\x10\x10\x52\x60\x00\x00\x00\x14\x00\x00\x00'
        crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
        escaped_buffer = self.escape(crced_buffer)
        FirmwareVersionCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        
        value = match.group(1).decode().rstrip('\x00')
        self.WriteStatus('FirmwareVersion', value, None)

    def SetMatrixLinearGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -60,
            'Max' : 0
            }

        source_val = qualifier['Source']
        output_val = qualifier['Output']
        srcOutVal  = ''.join([source_val, output_val])
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
            srcOutVal in self.SourceOutputStatesLinearGain):
            initial_buffer = b''.join([b'\xe8\xc8\x1d\x15\x57', self.SourceOutputStatesLinearGain[srcOutVal], 
                                       b'\x04\x00\x00\x00', self.dBToLinear(value)])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            MatrixLinearGainCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__SetHelper('MatrixLinearGain', MatrixLinearGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixLinearGain')

    def UpdateMatrixLinearGain(self, value, qualifier):

        source_val = qualifier['Source']
        output_val = qualifier['Output']
        srcOutVal  = ''.join([source_val, output_val])
        if srcOutVal in self.SourceOutputStatesLinearGain:
            initial_buffer = b''.join([b'\xe2\xc2\x1d\x15\x52', self.SourceOutputStatesLinearGain[srcOutVal], 
                                            b'\x04\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer) 
            escaped_buffer = self.escape(crced_buffer)
            MatrixLinearGainCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__UpdateHelper('MatrixLinearGain', MatrixLinearGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixLinearGain')

    def __MatchMatrixLinearGain(self, match, tag):

        qualifier = {}
        qualifier['Source'] = self.SourceOutputValuesLinearGain[match.group(1)][0]
        qualifier['Output'] = self.SourceOutputValuesLinearGain[match.group(1)][1]
        hex_value = self.unescape(match.group(2) + match.group(3))
        if hex_value[:4] == b'\x00\x00\x00\x00':
            value = -60
        else:
            value = self.linearTodB(hex_value[:4])
        if value != 'Unknown':
            self.WriteStatus('MatrixLinearGain', value, qualifier)
        else:
            self.Error(['Matrix Linear Gain: Invalid/unexpected response'])

    def SetMatrixMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01', 
            'Off' : b'\x00'
        }

        source_val = qualifier['Source']
        output_val = qualifier['Output']
        srcOutVal  = ''.join([source_val, output_val])
        if srcOutVal in self.SourceOutputStatesMute and value in ValueStateValues:
            initial_buffer = b''.join([b'\xe4\xc4\x14\x14\x57', self.SourceOutputStatesMute[srcOutVal], 
                                            b'\x01\x00\x00\x00', ValueStateValues[value]])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            MatrixMuteCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__SetHelper('MatrixMute', MatrixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMute')

    def UpdateMatrixMute(self, value, qualifier):

        source_val = qualifier['Source']
        output_val = qualifier['Output']
        srcOutVal  = ''.join([source_val, output_val])
        if srcOutVal in self.SourceOutputStatesMute:
            initial_buffer = b''.join([b'\xe6\xc6\x16\x16\x52', self.SourceOutputStatesMute[srcOutVal], 
                                            b'\x01\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            MatrixMuteCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__UpdateHelper('MatrixMute', MatrixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixMute')

    def __MatchMatrixMute(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        qualifier = {}
        qualifier['Source'] = self.SourceOutputValuesMute[match.group(1)][0]
        qualifier['Output'] = self.SourceOutputValuesMute[match.group(1)][1]
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('MatrixMute', value, qualifier)

    def SetMatrixPreGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -60,
            'Max' : 0
            }

        source_val = qualifier['Source']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and source_val in self.SourceStatesPreGain:
            initial_buffer = b''.join([b'\xe9\xc9\x1e\x16\x57', self.SourceStatesPreGain[source_val], 
                                       b'\x04\x00\x00\x00', self.dBToLinear(value)])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            MatrixPreGainCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__SetHelper('MatrixPreGain', MatrixPreGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixPreGain')

    def UpdateMatrixPreGain(self, value, qualifier):

        source_val = qualifier['Source']
        if source_val in self.SourceStatesPreGain:
            initial_buffer = b''.join([b'\xe3\xc3\x1e\x16\x52', self.SourceStatesPreGain[source_val], 
                                            b'\x04\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer) 
            escaped_buffer = self.escape(crced_buffer)
            MatrixPreGainCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__UpdateHelper('MatrixPreGain', MatrixPreGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixPreGain')

    def __MatchMatrixPreGain(self, match, tag):

        qualifier = {}
        qualifier['Source'] = self.SourceValuesPreGain[match.group(1)]
        hex_value = self.unescape(match.group(2) + match.group(3))
        if hex_value[:4] == b'\x00\x00\x00\x00':
            value = -60
        else:
            value = self.linearTodB(hex_value[:4])
        if value != 'Unknown':
            self.WriteStatus('MatrixPreGain', value, qualifier)
        else:
            self.Error(['Matrix Pre Gain: Invalid/unexpected response'])

    def SetMatrixPreMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01', 
            'Off' : b'\x00'
        }

        source_val = qualifier['Source']
        if source_val in self.SourceStatesPreMute and value in ValueStateValues:
            initial_buffer = b''.join([b'\xd3\xd2\x1e\x26\x57', self.SourceStatesPreMute[source_val], 
                                            b'\x01\x00\x00\x00', ValueStateValues[value]])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer) 
            escaped_buffer = self.escape(crced_buffer)
            PreMuteCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__SetHelper('MatrixPreMute', PreMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixPreMute')

    def UpdateMatrixPreMute(self, value, qualifier):

        source_val = qualifier['Source']
        if source_val in self.SourceStatesPreMute:
            initial_buffer = b''.join([b'\xe5\xc5\x1f\x14\x52', self.SourceStatesPreMute[source_val], 
                                            b'\x01\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer) 
            escaped_buffer = self.escape(crced_buffer)
            PreMuteCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__UpdateHelper('MatrixPreMute', PreMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixPreMute')

    def __MatchMatrixPreMute(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        qualifier = {}
        qualifier['Source'] = self.SourceValuesPreMute[match.group(1)]
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('MatrixPreMute', value, qualifier)

    def UpdateSlowMeterAliStatus(self, value, qualifier):

        TypeStates = {
            'TempTrasf'    : b'\x00\xb0\x00\x00', 
            'TempHeatSink' : b'\x04\xb0\x00\x00', 
            'VMainsRms'    : b'\x08\xb0\x00\x00', 
            'VccP'         : b'\x0c\xb0\x00\x00', 
            'VccN'         : b'\x10\xb0\x00\x00', 
            'FanCurrent'   : b'\x14\xb0\x00\x00', 
            'VAuxP'        : b'\x18\xb0\x00\x00', 
            'VAuxN'        : b'\x1c\xb0\x00\x00'
        }
        
        type_val = qualifier['Type']
        if type_val in TypeStates:
            initial_buffer = b''.join([b'\xe2\xc3\x13\x14\x52', TypeStates[type_val], b'\x04\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            SlowMeterAliStatusCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__UpdateHelper('SlowMeterAliStatus', SlowMeterAliStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSlowMeterAliStatus')

    def __MatchSlowMeterAliStatus(self, match, tag):

        TypeStates = {
            b'\x00\xb0\x00\x00' : 'TempTrasf', 
            b'\x04\xb0\x00\x00' : 'TempHeatSink', 
            b'\x08\xb0\x00\x00' : 'VMainsRms', 
            b'\x0c\xb0\x00\x00' : 'VccP', 
            b'\x10\xb0\x00\x00' : 'VccN', 
            b'\x14\xb0\x00\x00' : 'FanCurrent', 
            b'\x18\xb0\x00\x00' : 'VAuxP', 
            b'\x1c\xb0\x00\x00' : 'VAuxN'       
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1)]
        hex_value = self.unescape(match.group(2) + match.group(3))
        value =  value = self.linearTodB(hex_value[:4])
        if value != 'Unknown':
            self.WriteStatus('SlowMeterAliStatus', value, qualifier)
        else:
            self.Error(['Slow Meter Ali Status: Invalid/unexpected response'])

    def UpdateSlowMeterAmpliStatus(self, value, qualifier):
        
        channel_val = qualifier['Channel']
        if channel_val in self.SlowMeterAmpliChannelStates:
            initial_buffer = b''.join([b'\xe3\xc4\x16\x15\x52', self.SlowMeterAmpliChannelStates[channel_val], b'\x04\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            SlowMeterAmpliStatusCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__UpdateHelper('SlowMeterAmpliStatus', SlowMeterAmpliStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSlowMeterAmpliStatus')

    def __MatchSlowMeterAmpliStatus(self, match, tag):

        qualifier = {}
        qualifier['Channel'] = self.ChannelValuesSlowMeterAmpli[match.group(1)]
        hex_value = self.unescape(match.group(2) + match.group(3))
        value =  value = self.linearTodB(hex_value[:4])
        if value != 'Unknown':
            self.WriteStatus('SlowMeterAmpliStatus', value, qualifier)
        else:
            self.Error(['Slow Meter Ampli Status: Invalid/unexpected response'])

    def SetStandby(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01', 
            'Off' : b'\x00'
        }

        if value in ValueStateValues:
            initial_buffer = b''.join([b'\x00\x04\x00\x04\x57\x00\xa0\x00\x00', 
                                       b'\x04\x00\x00\x00', ValueStateValues[value], b'\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            StandbyCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__SetHelper('Standby', StandbyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandby')

    def SetUserGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -60,
            'Max' : 15
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in self.ChannelStatesUserGain:
            initial_buffer = b''.join([b'\xea\xca\x1a\x17\x57', self.ChannelStatesUserGain[channel_val], 
                                       b'\x04\x00\x00\x00', self.dBToLinear(value)])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            UserGainCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__SetHelper('UserGain', UserGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUserGain')

    def UpdateUserGain(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStatesUserGain:
            initial_buffer = b''.join([b'\xe2\xc5\x1a\x12\x52', self.ChannelStatesUserGain[channel_val], 
                                            b'\x04\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer) 
            escaped_buffer = self.escape(crced_buffer)
            UserGainCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__UpdateHelper('UserGain', UserGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateUserGain')

    def __MatchUserGain(self, match, tag):

        qualifier = {}
        qualifier['Channel'] = self.ChannelValuesUserGain[match.group(1)]
        hex_value = self.unescape(match.group(2) + match.group(3))
        if hex_value[:4] == b'\x00\x00\x00\x00':
            value = -60
        else:
            value = self.linearTodB(hex_value[:4])
        if value != 'Unknown':
            self.WriteStatus('UserGain', value, qualifier)
        else:
            self.Error(['User Gain: Invalid/unexpected response'])

    def SetUserMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01', 
            'Off' : b'\x00'
        }

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStatesUserMute and value in ValueStateValues:
            initial_buffer = b''.join([b'\xea\xca\x1a\x17\x57', self.ChannelStatesUserMute[channel_val], 
                                       b'\x01\x00\x00\x00', ValueStateValues[value]])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            UserMuteCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__SetHelper('UserMute', UserMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUserMute')

    def UpdateUserMute(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStatesUserMute:
            initial_buffer = b''.join([b'\xe1\xc5\x1a\x18\x52', self.ChannelStatesUserMute[channel_val], 
                                            b'\x01\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer) 
            escaped_buffer = self.escape(crced_buffer)
            UserMuteCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__UpdateHelper('UserMute', UserMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateUserMute')

    def __MatchUserMute(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = self.ChannelValuesUserMute[match.group(1)]
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('UserMute', value, qualifier)

    def SetWayGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -60,
            'Max' : 15
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in self.ChannelStatesWayGain:
            initial_buffer = b''.join([b'\xe1\xc2\x13\x14\x57', self.ChannelStatesWayGain[channel_val], 
                                       b'\x04\x00\x00\x00', self.dBToLinear(value)])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            WayGainCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__SetHelper('WayGain', WayGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWayGain')

    def UpdateWayGain(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStatesWayGain:
            initial_buffer = b''.join([b'\xe3\xc4\x15\x16\x52', self.ChannelStatesWayGain[channel_val], 
                                            b'\x04\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer) 
            escaped_buffer = self.escape(crced_buffer)
            WayGainCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            
            self.__UpdateHelper('WayGain', WayGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWayGain')

    def __MatchWayGain(self, match, tag):

        qualifier = {}
        qualifier['Channel'] = self.ChannelValuesWayGain[match.group(1)]
        hex_value = self.unescape(match.group(2) + match.group(3))
        if hex_value[:4] == b'\x00\x00\x00\x00':
            value = -60
        else:
            value = self.linearTodB(hex_value[:4])
        if value != 'Unknown':
            self.WriteStatus('WayGain', value, qualifier)
        else:
            self.Error(['Way Gain: Invalid/unexpected response'])

    def SetWayMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01', 
            'Off' : b'\x00'
        }

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStatesWayMute and value in ValueStateValues:
            initial_buffer = b''.join([b'\xe5\xc6\x17\x18\x57', self.ChannelStatesWayMute[channel_val], 
                                       b'\x04\x00\x00\x00', ValueStateValues[value], b'\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer)
            escaped_buffer = self.escape(crced_buffer)
            WayMuteCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__SetHelper('WayMute', WayMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWayMute')

    def UpdateWayMute(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val in self.ChannelStatesWayMute:
            initial_buffer = b''.join([b'\xe6\xc7\x18\x19\x52', self.ChannelStatesWayMute[channel_val], 
                                            b'\x04\x00\x00\x00'])
            crced_buffer = initial_buffer + self.CalCRC(initial_buffer) 
            escaped_buffer = self.escape(crced_buffer)
            WayMuteCmdString = b''.join([b'\x02', escaped_buffer, b'\x03'])
            self.__UpdateHelper('WayMute', WayMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWayMute')

    def __MatchWayMute(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = self.ChannelValuesWayMute[match.group(1)]
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('WayMute', value, qualifier)

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

        self.Error(['An error occurred.'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
    
    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def psft_25_4602_2Ch(self):

        self.Channel = 2
        self.SourceOutputStatesLinearGain = {
            '11' : b'\x18\x30\x00\x00', 
            '12' : b'\x1c\x30\x00\x00', 
            '21' : b'\x28\x30\x00\x00', 
            '22' : b'\x2c\x30\x00\x00', 
        }
        self.SourceOutputStatesMute = {
            '11' : b'\x58\x30\x00\x00', 
            '12' : b'\x59\x30\x00\x00', 
            '21' : b'\x5c\x30\x00\x00', 
            '22' : b'\x5d\x30\x00\x00', 
        }
        self.SourceStatesPreGain = {
            '1' : b'\x08\x30\x00\x00', 
            '2' : b'\x0c\x30\x00\x00', 
        }
        self.SourceStatesPreMute = {
            '1' : b'\x04\x30\x00\x00', 
            '2' : b'\x05\x30\x00\x00', 
        }
        self.ChannelStatesUserGain = {
            '1' : b'\x00\x40\x00\x00', 
            '2' : b'\x04\x40\x00\x00', 
        }
        self.ChannelStatesUserMute = {
            '1' : b'\x24\x40\x00\x00', 
            '2' : b'\x25\x40\x00\x00', 
        }
        self.ChannelStatesWayGain = {
            '1' : b'\x10\x70\x00\x00', 
            '2' : b'\x14\x70\x00\x00', 
        }
        self.ChannelStatesWayMute = {
            '1' : b'\x40\x70\x00\x00', 
            '2' : b'\x44\x70\x00\x00', 
        }
        self.SlowMeterAmpliChannelStates = {
            '1' : b'\xf4\xb0\x00\x00', 
            '2' : b'\xf8\xb0\x00\x00', 
        }
        
        self.SourceOutputValuesLinearGain = {
            b'\x18\x30\x00\x00' : '11', 
            b'\x1c\x30\x00\x00' : '12', 
            b'\x28\x30\x00\x00' : '21', 
            b'\x2c\x30\x00\x00' : '22', 
        }
        self.SourceOutputValuesMute = {
            b'\x18\x30\x00\x00' : '11', 
            b'\x1c\x30\x00\x00' : '12', 
            b'\x28\x30\x00\x00' : '21', 
            b'\x2c\x30\x00\x00' : '22', 
        }
        self.SourceValuesPreGain = {
            b'\x08\x30\x00\x00' : '1', 
            b'\x0c\x30\x00\x00' : '2', 
        }
        self.SourceValuesPreMute = {
            b'\x04\x30\x00\x00' : '1', 
            b'\x05\x30\x00\x00' : '2', 
        }
        self.ChannelValuesUserGain = {
            b'\x00\x40\x00\x00' : '1', 
            b'\x04\x40\x00\x00' : '2', 
        }
        self.ChannelValuesUserMute = {
            b'\x24\x40\x00\x00' : '1', 
            b'\x25\x40\x00\x00' : '2', 
        }
        self.ChannelValuesWayGain = {
            b'\x10\x70\x00\x00' : '1', 
            b'\x14\x70\x00\x00' : '2', 
        }
        self.ChannelValuesWayMute = {
            b'\x40\x70\x00\x00' : '1', 
            b'\x44\x70\x00\x00' : '2', 
        }
        self.ChannelValuesSlowMeterAmpli = {
            b'\xf4\xb0\x00\x00' : '1', 
            b'\xf8\xb0\x00\x00' : '2', 
        }
        
    def psft_25_4602_4Ch(self):

        self.Channel = 4
        self.SourceOutputStatesLinearGain = {
            '11' : b'\x18\x30\x00\x00', 
            '12' : b'\x1c\x30\x00\x00', 
            '13' : b'\x20\x30\x00\x00', 
            '14' : b'\x24\x30\x00\x00', 
            '21' : b'\x28\x30\x00\x00', 
            '22' : b'\x2c\x30\x00\x00', 
            '23' : b'\x30\x30\x00\x00', 
            '24' : b'\x34\x30\x00\x00', 
            '31' : b'\x38\x30\x00\x00', 
            '32' : b'\x3c\x30\x00\x00', 
            '33' : b'\x40\x30\x00\x00', 
            '34' : b'\x44\x30\x00\x00', 
            '41' : b'\x48\x30\x00\x00',
            '42' : b'\x4c\x30\x00\x00',
            '43' : b'\x50\x30\x00\x00',
            '44' : b'\x54\x30\x00\x00',
        }
        self.SourceOutputStatesMute = {
            '11' : b'\x58\x30\x00\x00', 
            '12' : b'\x59\x30\x00\x00', 
            '13' : b'\x5a\x30\x00\x00', 
            '14' : b'\x5b\x30\x00\x00', 
            '21' : b'\x5c\x30\x00\x00', 
            '22' : b'\x5d\x30\x00\x00', 
            '23' : b'\x5e\x30\x00\x00', 
            '24' : b'\x5f\x30\x00\x00', 
            '31' : b'\x60\x30\x00\x00', 
            '32' : b'\x61\x30\x00\x00', 
            '33' : b'\x62\x30\x00\x00', 
            '34' : b'\x63\x30\x00\x00', 
            '41' : b'\x64\x30\x00\x00',
            '42' : b'\x65\x30\x00\x00',
            '43' : b'\x66\x30\x00\x00',
            '44' : b'\x67\x30\x00\x00',
        }
        self.SourceStatesPreGain = {
            '1' : b'\x08\x30\x00\x00', 
            '2' : b'\x0c\x30\x00\x00', 
            '3' : b'\x10\x30\x00\x00', 
            '4' : b'\x14\x30\x00\x00'
        }
        self.SourceStatesPreMute = {
            '1' : b'\x04\x30\x00\x00', 
            '2' : b'\x05\x30\x00\x00', 
            '3' : b'\x06\x30\x00\x00', 
            '4' : b'\x07\x30\x00\x00'
        }
        self.ChannelStatesUserGain = {
            '1' : b'\x00\x40\x00\x00', 
            '2' : b'\x04\x40\x00\x00', 
            '3' : b'\x08\x40\x00\x00', 
            '4' : b'\x0c\x40\x00\x00'
        }
        self.ChannelStatesUserMute = {
            '1' : b'\x24\x40\x00\x00', 
            '2' : b'\x25\x40\x00\x00', 
            '3' : b'\x26\x40\x00\x00', 
            '4' : b'\x27\x40\x00\x00'
        }
        self.ChannelStatesWayGain = {
            '1' : b'\x10\x70\x00\x00', 
            '2' : b'\x14\x70\x00\x00', 
            '3' : b'\x18\x70\x00\x00', 
            '4' : b'\x1c\x70\x00\x00'
        }
        self.ChannelStatesWayMute = {
            '1' : b'\x40\x70\x00\x00', 
            '2' : b'\x44\x70\x00\x00', 
            '3' : b'\x48\x70\x00\x00', 
            '4' : b'\x4c\x70\x00\x00'
        }
        self.SlowMeterAmpliChannelStates = {
            '1' : b'\xf4\xb0\x00\x00', 
            '2' : b'\xf8\xb0\x00\x00', 
            '3' : b'\xfc\xb0\x00\x00', 
            '4' : b'\x00\xb1\x00\x00'
        }
        
        self.SourceOutputValuesLinearGain = {
            b'\x18\x30\x00\x00' : '11', 
            b'\x1c\x30\x00\x00' : '12', 
            b'\x20\x30\x00\x00' : '13', 
            b'\x24\x30\x00\x00' : '14', 
            b'\x28\x30\x00\x00' : '21', 
            b'\x2c\x30\x00\x00' : '22', 
            b'\x30\x30\x00\x00' : '23', 
            b'\x34\x30\x00\x00' : '24', 
            b'\x38\x30\x00\x00' : '31', 
            b'\x3c\x30\x00\x00' : '32', 
            b'\x40\x30\x00\x00' : '33', 
            b'\x44\x30\x00\x00' : '34', 
            b'\x48\x30\x00\x00' : '41',
            b'\x4c\x30\x00\x00' : '42',
            b'\x50\x30\x00\x00' : '43',
            b'\x54\x30\x00\x00' : '44',
        }
        self.SourceOutputValuesMute = {
            b'\x58\x30\x00\x00' : '11', 
            b'\x59\x30\x00\x00' : '12', 
            b'\x5a\x30\x00\x00' : '13', 
            b'\x5b\x30\x00\x00' : '14', 
            b'\x5c\x30\x00\x00' : '21', 
            b'\x5d\x30\x00\x00' : '22', 
            b'\x5e\x30\x00\x00' : '23', 
            b'\x5f\x30\x00\x00' : '24', 
            b'\x60\x30\x00\x00' : '31', 
            b'\x61\x30\x00\x00' : '32', 
            b'\x62\x30\x00\x00' : '33', 
            b'\x63\x30\x00\x00' : '34', 
            b'\x64\x30\x00\x00' : '41',
            b'\x65\x30\x00\x00' : '42',
            b'\x66\x30\x00\x00' : '43',
            b'\x67\x30\x00\x00' : '44',
        }
        self.SourceValuesPreGain = {
            b'\x08\x30\x00\x00' : '1', 
            b'\x0c\x30\x00\x00' : '2', 
            b'\x10\x30\x00\x00' : '3', 
            b'\x14\x30\x00\x00' : '4'
        }
        self.SourceValuesPreMute = {
            b'\x04\x30\x00\x00' : '1', 
            b'\x05\x30\x00\x00' : '2', 
            b'\x06\x30\x00\x00' : '3', 
            b'\x07\x30\x00\x00' : '4'
        }
        self.ChannelValuesUserGain = {
            b'\x00\x40\x00\x00' : '1', 
            b'\x04\x40\x00\x00' : '2', 
            b'\x08\x40\x00\x00' : '3', 
            b'\x0c\x40\x00\x00' : '4'
        }
        self.ChannelValuesUserMute = {
            b'\x24\x40\x00\x00' : '1', 
            b'\x25\x40\x00\x00' : '2', 
            b'\x26\x40\x00\x00' : '3', 
            b'\x27\x40\x00\x00' : '4'
        }
        self.ChannelValuesWayGain = {
            b'\x10\x70\x00\x00' : '1', 
            b'\x14\x70\x00\x00' : '2', 
            b'\x18\x70\x00\x00' : '3', 
            b'\x1c\x70\x00\x00' : '4'
        }
        self.ChannelValuesWayMute = {
            b'\x40\x70\x00\x00' : '1', 
            b'\x44\x70\x00\x00' : '2', 
            b'\x48\x70\x00\x00' : '3', 
            b'\x4c\x70\x00\x00' : '4'
        }
        self.ChannelValuesSlowMeterAmpli = {
            b'\xf4\xb0\x00\x00' : '1', 
            b'\xf8\xb0\x00\x00' : '2', 
            b'\xfc\xb0\x00\x00' : '3', 
            b'\x00\xb1\x00\x00' : '4'
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