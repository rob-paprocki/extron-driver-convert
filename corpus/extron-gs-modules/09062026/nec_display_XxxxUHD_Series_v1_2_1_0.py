from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack
from binascii import hexlify

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 0x41
        self.Models = {
            'X841UHD': self.nec_10_1131_1,
            'X981UHD': self.nec_10_1131_1,
            'X651UHD': self.nec_10_1131_1,
            'X551UHD': self.nec_10_1131_1,
            'X651UHD-2': self.nec_10_1131_2,
            'X981UHD-2': self.nec_10_1131_2,
            'X841UHD-2': self.nec_10_1131_2,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveFrame': { 'Status': {}},
            'ActivePicture': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioInput': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'DVIMode': { 'Status': {}},
            'HDMIDVIModeSelect': { 'Status': {}},
            'Input': { 'Status': {}},
            'MultiPicture': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PIPPBPAspectRatio': { 'Status': {}},
            'PIPPBPInput': {'Parameters':['Picture'], 'Status': {}},
            'PIPPBPMode': { 'Status': {}},
            'PIPPBPPicturePosition': {'Parameters':['Direction'], 'Status': {}},
            'PIPPBPPictureSize': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.group = 0

        
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0x2A
            self.group = 1
        elif (value) in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
            self._DeviceID = ord(value) - 16
            self.group = 1
        elif 1 <= int(value) <= 100:
            self._DeviceID = 0x40 + int(value)
            self.group = 0

    def SetActiveFrame(self, value, qualifier):

        ValueStateValues = {                    # Response:
            'On' :  b'0E0A\x02110D0002\x03',    # \x0100AF12\x0200110D0000020002\x03q\r
            'Off' : b'0E0A\x02110D0001\x03'     # \x0100AF12\x0200110D0000020001\x03r\r
        }

        buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        ActiveFrameCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'

        self.__SetHelper('ActiveFrame', ActiveFrameCmdString, value, qualifier)

    def UpdateActiveFrame(self, value, qualifier):

        ValueStateValues = {    # Responses:
            b'2' : 'On',        # \x0100AD12\x0200110D0000020002\x03s\r
            b'1' : 'Off'        # \x0100AD12\x0200110D0000020001\x03p\r
        }

        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x02110D\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        ActiveFrameCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('ActiveFrame', ActiveFrameCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('ActiveFrame', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Active Frame: Invalid/unexpected response'])

    def SetActivePicture(self, value, qualifier):

        ValueStateValues = {                            'Picture 1' : b'0E0A\x02110B0001\x03',  # \x0100AF12\x0200110B0000040001\x03r\r
            'Picture 2' : b'0E0A\x02110B0002\x03',  # \x0100AF12\x0200110B0000040002\x03q\r
            'Picture 3' : b'0E0A\x02110B0003\x03',  # \x0100AF12\x0200110B0000040003\x03p\r
            'Picture 4' : b'0E0A\x02110B0004\x03'   # \x0100AF12\x0200110B0000040004\x03w\r
        }

        buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        ActivePictureCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'

        self.__SetHelper('ActivePicture', ActivePictureCmdString, value, qualifier)

    def UpdateActivePicture(self, value, qualifier):

        ValueStateValues = {    # Responses:
            b'1' : 'Picture 1', # \x0100AD12\x0200110B0000040001\x03p\r
            b'2' : 'Picture 2', # \x0100AD12\x0200110B0000040002\x03s\r
            b'3' : 'Picture 3', # \x0100AD12\x0200110B0000040003\x03r\r
            b'4' : 'Picture 4'  # \x0100AD12\x0200110B0000040004\x03u\r
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x02110B\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        ActivePictureCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'

        res = self.__UpdateHelper('ActivePicture', ActivePictureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('ActivePicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Active Picture: Invalid/unexpected response'])

    def SetAspectRatio(self, value, qualifier):

        buffer = pack( '>BB14s', 0x30, self.DeviceID, self.AspectSetStates[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        AspectRatioCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020270\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        AspectRatioCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = self.AspectUpdateStates[res[23:24]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {                        # Responses, where . is the checksum:
            'Mini-Jack':   b'0E0A\x02022E0001\x03', # \x0100AF12\x0200022E00000C0001\x03.\r
            'DisplayPort': b'0E0A\x02022E0007\x03', # \x0100AF12\x0200022E00000C0007\x03.\r
            'HDMI 1':      b'0E0A\x02022E0004\x03', # \x0100AF12\x0200022E00000C0004\x03.\r
            'HDMI 2':      b'0E0A\x02022E000A\x03', # \x0100AF12\x0200022E00000C000A\x03.\r
            'HDMI 3':      b'0E0A\x02022E000B\x03', # \x0100AF12\x0200022E00000C000B\x03.\r
            'HDMI 4':      b'0E0A\x02022E000C\x03'  # \x0100AF12\x0200022E00000C000C\x03.\r
        }

        buffer = pack('>BB14s', 0x30, self.DeviceID, ValueStateValues[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

        AudioInputCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def UpdateAudioInput(self, value, qualifier):

        ValueStateValues = {     # Responses, where . is the checksum:
            b'1': 'Mini-Jack',   # \x0100AD12\x0200022E00000C0001\x03.\r
            b'7': 'DisplayPort', # \x0100AD12\x0200022E00000C0007\x03.\r
            b'4': 'HDMI 1',      # \x0100AD12\x0200022E00000C0004\x03.\r
            b'A': 'HDMI 2',      # \x0100AD12\x0200022E00000C000A\x03.\r
            b'B': 'HDMI 3',      # \x0100AD12\x0200022E00000C000B\x03.\r
            b'C': 'HDMI 4'       # \x0100AD12\x0200022E00000C000C\x03.\r
        }

        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x02022E\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

        AudioInputCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('AudioInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Input: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {                 # Response:
            'On'  : b'0E0A\x02008D0001\x03', # \x0100AF12\x0200008D0000020001\x03z\r
            'Off' : b'0E0A\x02008D0002\x03'  # \x0100AF12\x0200008D0000020002\x03y\r
        }

        buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        AudioMuteCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r' 
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {    # Response:
            b'1' : 'On',        # \x0100AD12\x0200008D0000020001\x03x\r
            b'2' : 'Off'        # \x0100AD12\x0200008D0000020002\x03{\r
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x02008D\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        AudioMuteCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'    
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetDVIMode(self, value, qualifier):

        ValueStateValues = {
            'DVI-PC': b'\x01\x30\x2A\x30\x45\x30\x41\x02\x30\x32\x43\x46\x30\x30\x30\x31\x03\x19\x0D',
            'DVI-HD': b'\x01\x30\x2A\x30\x45\x30\x41\x02\x30\x32\x43\x46\x30\x30\x30\x32\x03\x1A\x0D'
        }

        DVIModeCmdString = ValueStateValues[value]
        self.__SetHelper('DVIMode', DVIModeCmdString, value, qualifier)

    def UpdateDVIMode(self, value, qualifier):

        ValueStateValues = {
            b'1': 'DVI-PC', 
            b'2': 'DVI-HD'
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x02\x30\x32\x43\x46\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

        DVIModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('DVIMode', DVIModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('DVIMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['DVI Mode: Invalid/unexpected response'])

    def SetHDMIDVIModeSelect(self, value, qualifier):

        ValueStateValues = {
            'HDMI':     b'\x01\x30\x2A\x30\x45\x30\x41\x02\x31\x31\x31\x38\x30\x30\x30\x31\x03\x17\x0D', 
            'DVI':      b'\x01\x30\x2A\x30\x45\x30\x41\x02\x31\x31\x31\x38\x30\x30\x30\x32\x03\x14\x0D', 
            'HDMI/DVI': b'\x01\x30\x2A\x30\x45\x30\x41\x02\x31\x31\x31\x38\x30\x30\x30\x33\x03\x15\x0D'
        }
        
        HDMIDVIModeSelectCmdString = ValueStateValues[value]
        self.__SetHelper('HDMIDVIModeSelect', HDMIDVIModeSelectCmdString, value, qualifier)

    def UpdateHDMIDVIModeSelect(self, value, qualifier):


        ValueStateValues = {
            b'1': 'HDMI', 
            b'2': 'DVI', 
            b'3': 'HDMI/DVI'
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x02\x31\x31\x31\x38\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

        HDMIDVIModeSelectCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('HDMIDVIModeSelect', HDMIDVIModeSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('HDMIDVIModeSelect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['HDMI DVI Mode Select: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        buffer = pack( '>BB14s', 0x30, self.DeviceID, self.InputSetStates[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        InputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r' 
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020060\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        InputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'    
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputUpdateStates[res[22:24]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetMultiPicture(self, value, qualifier):

        ValueStateValues = {                     'Off' : b'0E0A\x0202720001\x03', # \x0100AF12\x020002720000050001\x03\x06\r
            'PIP' : b'0E0A\x0202720002\x03', # \x0100AF12\x020002720000050002\x03\x05\r
            'PBP' : b'0E0A\x0202720005\x03'  # \x0100AF12\x020002720000050005\x03\x02\r
        }

        buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        MultiPictureCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        self.__SetHelper('MultiPicture', MultiPictureCmdString, value, qualifier)

    def UpdateMultiPicture(self, value, qualifier):

        ValueStateValues = {    # Responses:
            b'1' : 'Off',       # \x0100AD12\x020002720000050001\x03\x04\r
            b'2' : 'PIP',       # \x0100AD12\x020002720000050002\x03\x07\r
            b'5' : 'PBP'        # \x0100AD12\x020002720000050005\x03\x00\r
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020272\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        MultiPictureCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('MultiPicture', MultiPictureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('MultiPicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Multi Picture: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {                     'On'  : b'0E0A\x0202EA0002\x03', # \x0100AF12\x020002EA0000020002\x03\x03\r
            'Off' : b'0E0A\x0202EA0001\x03'  # \x0100AF12\x020002EA0000020001\x03\x00\r
        }

        buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        OnScreenDisplayCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r' 
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
    
    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = { # Responses:
            b'2' : 'On',     # \x0100AD12\x020002EA0000020002\x03\x01\r
            b'1' : 'Off'     # \x0100AD12\x020002EA0000020001\x03\x02\r
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x0202EA\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        OnScreenDisplayCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'    
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'sRGB'          : b'0E0A\x02021A0001\x03',
            'Highbright'    : b'0E0A\x02021A0003\x03',
            'Standard'      : b'0E0A\x02021A0004\x03',
            'Cinema'        : b'0E0A\x02021A0005\x03',
            'Custom 1'      : b'0E0A\x02021A0008\x03',
            'Custom 2'      : b'0E0A\x02021A0009\x03',
            'SVE-1 Setting' : b'0E0A\x02021A000D\x03',
            'SVE-2 Setting' : b'0E0A\x02021A000E\x03',
            'SVE-3 Setting' : b'0E0A\x02021A000F\x03',
            'SVE-4 Setting' : b'0E0A\x02021A0010\x03',
            'SVE-5 Setting' : b'0E0A\x02021A0011\x03'
        }

        buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        PictureModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'01' : 'sRGB',
            b'03' : 'Highbright',
            b'04' : 'Standard',
            b'05' : 'Cinema',
            b'08' : 'Custom 1',
            b'09' : 'Custom 2',
            b'0D' : 'SVE-1 Setting',
            b'0E' : 'SVE-2 Setting',
            b'0F' : 'SVE-3 Setting',
            b'10' : 'SVE-4 Setting',
            b'11' : 'SVE-5 Setting'
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x02021A\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        PictureModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[22:24]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPIPPBPAspectRatio(self, value, qualifier):

        buffer = pack( '>BB14s', 0x30, self.DeviceID, self.PIPPBPAspectSetStates[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        PIPPBPAspectRatioCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'

        self.__SetHelper('PIPPBPAspectRatio', PIPPBPAspectRatioCmdString, value, qualifier)

    def UpdatePIPPBPAspectRatio(self, value, qualifier):

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x021083\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        PIPPBPAspectRatioCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PIPPBPAspectRatio', PIPPBPAspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = self.PIPPBPAspectUpdateStates[res[23:24]]
                self.WriteStatus('PIPPBPAspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP PBP Aspect Ratio: Invalid/unexpected response'])

    def SetPIPPBPInput(self, value, qualifier):

        PictureStates = {
            'Picture 1' : b'0E0A\x02110E', 
            'Picture 2' : b'0E0A\x02110F', 
            'Picture 3' : b'0E0A\x021110', 
            'Picture 4' : b'0E0A\x021111'
        }

        valueStr = PictureStates[qualifier['Picture']] + self.PIPInputSet[value]
        buffer = pack( '>BB14s', 0x30, self.DeviceID, valueStr)
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        PIPPBPInputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'

        self.__SetHelper('PIPPBPInput', PIPPBPInputCmdString, value, qualifier)

    def UpdatePIPPBPInput(self, value, qualifier):

        PictureStates = {
            'Picture 1' : b'0E', 
            'Picture 2' : b'0F', 
            'Picture 3' : b'10', 
            'Picture 4' : b'11'
        }
                
        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x0211' + PictureStates[qualifier['Picture']] + b'\x03')
        checksum = 0
        
        for i in buffer:
            checksum = checksum ^ i
            
        PIPPBPInputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PIPPBPInput', PIPPBPInputCmdString, value, qualifier)
        if res:
            try:
                value = self.PIPInputUpdate[res[22:24]]
                self.WriteStatus('PIPPBPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP PBP Input: Invalid/unexpected response'])

    def SetPIPPBPMode(self, value, qualifier):

        PIPPBPValues = {                                       # Response:
            '2 Windows, PIP'        : b'0E0A\x0210B50002\x03', # \x0100AF12\x020010B50000060002\x03w\r
            '3 Windows, PIP/PBP 1'  : b'0E0A\x0210B50003\x03', # \x0100AF12\x020010B50000060003\x03v\r
            '2 Windows, PBP 1'      : b'0E0A\x0210B50001\x03', # \x0100AF12\x020010B50000060001\x03t\r
            '3 Windows, PBP 2'      : b'0E0A\x0210B50004\x03', # \x0100AF12\x020010B50000060004\x03q\r
            '3 Windows, PBP 3'      : b'0E0A\x0210B50005\x03', # \x0100AF12\x020010B50000060005\x03p\r
            '4 Windows, PBP 1'      : b'0E0A\x0210B50006\x03'  # \x0100AF12\x020010B50000060006\x03s\r
        }
        
        buffer = pack( '>BB14s', 0x30, self.DeviceID, PIPPBPValues[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
                
        PIPPBPModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'

        self.__SetHelper('PIPPBPMode', PIPPBPModeCmdString, value, qualifier)

    def UpdatePIPPBPMode(self, value, qualifier):

        PIPPBPValues = {        # Response:
            b'1' : '2 Windows', # \x0100AD12\x020010B50000060001\x03v\r
            b'2' : '2 Windows', # \x0100AD12\x020010B50000060002\x03u\r
            b'3' : '3 Windows', # \x0100AD12\x020010B50000060003\x03t\r
            b'4' : '3 Windows', # \x0100AD12\x020010B50000060004\x03s\r
            b'5' : '3 Windows', # \x0100AD12\x020010B50000060005\x03r\r
            b'6' : '4 Windows'  # \x0100AD12\x020010B50000060003\x03q\r
        }
        
        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x0210B5\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        PIPPBPModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PIPPBPMode', PIPPBPModeCmdString, value, qualifier)
        if res:
            try:
                value = PIPPBPValues[res[23:24]]
                self.WriteStatus('PIPPBPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP PBP Mode: Invalid/unexpected response'])

    def SetPIPPBPPicturePosition(self, value, qualifier):

        DirectionStates = {
            'X' : b'0E0A\x02027400', 
            'Y' : b'0E0A\x02027500'
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack('>BB11s2sB', 0x30, self.DeviceID, DirectionStates[qualifier['Direction']], result, 0x03)
            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PIPPBPPicturePositionCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PIPPBPPicturePosition', PIPPBPPicturePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPBPPicturePosition')

    def UpdatePIPPBPPicturePosition(self, value, qualifier):

        DirectionStates = {
            'X' : b'0274', 
            'Y' : b'0275'
        }

        buffer = pack( '>BB5s4sB', 0x30, self.DeviceID, b'0C06\x02', DirectionStates[qualifier['Direction']], 0x03)
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
            
        PIPPBPPicturePositionCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PIPPBPPicturePosition', PIPPBPPicturePositionCmdString, value, qualifier)
        if res:
            try:
                value = int(res[22:24], 16)
                self.WriteStatus('PIPPBPPicturePosition', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['PIP PBP Picture Position: Invalid/unexpected response'])

    def SetPIPPBPPictureSize(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 80
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack('>BB11s2sB', 0x30, self.DeviceID, b'0E0A\x0210B900', result, 0x03)
            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
                
            PIPPBPPictureSizeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PIPPBPPictureSize', PIPPBPPictureSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPBPPictureSize')

    def UpdatePIPPBPPictureSize(self, value, qualifier):

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x0210B9\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

        PIPPBPPictureSizeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PIPPBPPictureSize', PIPPBPPictureSizeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[22:24], 16)
                self.WriteStatus('PIPPBPPictureSize', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['PIP PBP Picture Size: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {                   # Response:
            'On'  : b'0A0C\x02C203D60001\x03', # \x0100AB0E\x0200C203D60001\x03v\r
            'Off' : b'0A0C\x02C203D60004\x03'  # \x0100AB0E\x0200C203D60004\x03s\r
        }

        buffer = pack( '>BB16s', 0x30, self.DeviceID, ValueStateValues[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        PowerCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'1' : 'On', 
            b'2'  :'Stand-by (Power Save)', 
            b'3'  :'Suspend (Power Save)',
            b'4'  :'Off'
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0A06\x0201D6\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        PowerCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'    
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {                 # Response:
            'On'  : b'0E0A\x0210B60001\x03', # \x0100AF12\x020010B60000020001\x03s\r
            'Off' : b'0E0A\x0210B60002\x03'  # \x0100AF12\x020010B60000020002\x03p\r
        }

        buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        VideoMuteCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {    # Response:
            b'1' : 'On',        # \x0100AD12\x020010B60000020001\x03q\r
            b'2' : 'Off'        # \x0100AD12\x020010B60000020002\x03r\r
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x0210B6\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        VideoMuteCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'    
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, self.DeviceID, b'0E0A\x02006200', result, b'\x03')
            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            VolumeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020062\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        VolumeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'    
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[22:24], 16)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or self.group == 1:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command + ':', res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if (self.Unidirectional == 'True') or self.group == 1:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            return self.__CheckResponseForErrors(command + ':', res)

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def nec_10_1131_1(self):


        self.InputSetStates = {                            
            'HDMI 1':        b'0E0A\x0200600011\x03',  # \x0100AF12\x020000600000860011\x03\r
            'HDMI 2':        b'0E0A\x0200600012\x03',  # \x0100AF12\x020000600000860012\x03\x0e\r
            'HDMI 3':        b'0E0A\x0211060082\x03',  # \x0100AF12\x020011060000860082\x03\x07\r
            'HDMI 4':        b'0E0A\x0211060083\x03',  # \x0100AF12\x020011060000860083\x03\x06\r
            'Option':        b'0E0A\x021106000D\x03',  # \x0100AF12\x02001106000086000D\x03y\r
            'DisplayPort 1': b'0E0A\x020060000F\x03',  # \x0100AD12\x02000060000086000F\x03y\r
            'DisplayPort 2': b'0E0A\x0200600010\x03',  
            'DVI 1':         b'0E0A\x0200600003\x03',  # \x0100AF12\x020000600000860003\x03\x0e\r
            'DVI 2':         b'0E0A\x0200600004\x03'   # \x0100AF12\x020000600000860004\x03\t\r
        }

        self.InputUpdateStates = { # Responses:
            b'11': 'HDMI 1',       # \x0100AD12\x020000600000860011\x03\x0f\r
            b'12': 'HDMI 2',       # \x0100AD12\x020000600000860012\x03\x0c\r
            b'82': 'HDMI 3',       # \x0100AD12\x020000600000860082\x03\x05\r
            b'83': 'HDMI 4',       # \x0100AD12\x020000600000860083\x03\x04\r
            b'0D': 'Option',       # Was unable to configure
            b'0F': 'DisplayPort 1',  # \x0100AD12\x02000060000086000F\x03y\r
            b'10': 'DisplayPort 2', 
            b'03': 'DVI 1',        # \x0100AD12\x020000600000860003\x03\x0c\r
            b'04': 'DVI 2'         # \x0100AD12\x020000600000860004\x03\x0b\r
        }

        self.PIPPBPAspectSetStates = {               
            'Normal' :  b'0E0A\x0210830001\x03', # \x0100AF12\x020010830000060001\x03\x08\r
            'Full' :    b'0E0A\x0210830002\x03', # \x0100AF12\x020010830000060002\x03\x0b\r
            'Wide' :    b'0E0A\x0210830003\x03',
            'Zoom' :    b'0E0A\x0210830004\x03'
        }

        self.PIPPBPAspectUpdateStates = { # Responses:
            b'1' : 'Normal',              # \x0100AD12\x020010830000060001\x03\n\r
            b'2' : 'Full',                # \x0100AD12\x020010830000060002\x03\t\r
            b'3' : 'Wide',   
            b'4' : 'Zoom'    
        }

        self.AspectSetStates = {                        
            'Normal'    : b'0E0A\x0202700001\x03',  # \x0100AF12\x020002700000070001\x03\x06\r
            'Full'      : b'0E0A\x0202700002\x03',  # \x0100AF12\x020002700000070002\x03\x05\r
            'Wide'      : b'0E0A\x0202700003\x03',  # \x0100AF12\x020002700000070003\x03\x04\r
            'Zoom'      : b'0E0A\x0202700004\x03',  # \x0100AF12\x020002700000070004\x03\x03\r
            'Dynamic'   : b'0E0A\x0202700006\x03',  # \x0100AF12\x020002700000070006\x03\x01\r
            'Dot by Dot': b'0E0A\x0202700007\x03'   # \x0100AF12\x020002700000070007\x03\x00\r
        }

        self.AspectUpdateStates = { # Responses:
            b'1' : 'Normal',        # \x0100AD12\x020002700000070001\x03\x04\r
            b'2' : 'Full',          # \x0100AD12\x020002700000070002\x03\x07\r
            b'3' : 'Wide',          # \x0100AD12\x020002700000070003\x03\x06\r
            b'4' : 'Zoom',          # \x0100AD12\x020002700000070004\x03\x01\r
            b'6' : 'Dynamic',       # \x0100AD12\x020002700000070006\x03\x03\r
            b'7' : 'Dot by Dot'     # \x0100AD12\x020002700000070007\x03\x02\r
        }

        self.PIPInputSet = {
            'DVI 1' :           b'0003\x03', 
            'DVI 2' :           b'0004\x03', 
            'Option' :          b'000D\x03', 
            'DisplayPort 1' :   b'000F\x03', 
            'DisplayPort 2' :   b'0010\x03', 
            'HDMI 1' :          b'0011\x03', 
            'HDMI 2' :          b'0012\x03', 
            'HDMI 3' :          b'0082\x03', 
            'HDMI 4' :          b'0083\x03'
        }

        self.PIPInputUpdate = {
            b'03' : 'DVI 1', 
            b'04' : 'DVI 2', 
            b'0D' : 'Option', 
            b'0F' : 'DisplayPort 1', 
            b'10' : 'DisplayPort 2', 
            b'11' : 'HDMI 1', 
            b'12' : 'HDMI 2', 
            b'82' : 'HDMI 3', 
            b'83' : 'HDMI 4'
        }



    def nec_10_1131_2(self):


        self.InputSetStates = {                            
            'HDMI 1':        b'0E0A\x0200600011\x03',  # \x0100AF12\x020000600000860011\x03\r
            'HDMI 2':        b'0E0A\x0200600012\x03',  # \x0100AF12\x020000600000860012\x03\x0e\r
            'HDMI 3':        b'0E0A\x0211060082\x03',  # \x0100AF12\x020011060000860082\x03\x07\r
            'HDMI 4':        b'0E0A\x0211060083\x03',  # \x0100AF12\x020011060000860083\x03\x06\r
            'Option':        b'0E0A\x021106000D\x03',  # \x0100AF12\x02001106000086000D\x03y\r
            'DisplayPort':   b'0E0A\x020060000F\x03',  # \x0100AD12\x02000060000086000F\x03y\r
            'DVI 1':         b'0E0A\x0200600003\x03',  # \x0100AF12\x020000600000860003\x03\x0e\r
            'DVI 2':         b'0E0A\x0200600004\x03',  # \x0100AF12\x020000600000860004\x03\t\r
        }

        self.InputUpdateStates = { # Responses:
            b'11': 'HDMI 1',       # \x0100AD12\x020000600000860011\x03\x0f\r
            b'12': 'HDMI 2',       # \x0100AD12\x020000600000860012\x03\x0c\r
            b'82': 'HDMI 3',       # \x0100AD12\x020000600000860082\x03\x05\r
            b'83': 'HDMI 4',       # \x0100AD12\x020000600000860083\x03\x04\r
            b'0D': 'Option',       # Was unable to configure (No Option Board)
            b'0F': 'DisplayPort',  # \x0100AD12\x02000060000086000F\x03y\r
            b'03': 'DVI 1',        # \x0100AD12\x020000600000860003\x03\x0c\r
            b'04': 'DVI 2'         # \x0100AD12\x020000600000860004\x03\x0b\r
        }

        self.PIPPBPAspectSetStates = {               
            'Normal':   b'0E0A\x0210830001\x03', # \x0100AF12\x020010830000060001\x03\x08\r
            'Full':     b'0E0A\x0210830002\x03', # \x0100AF12\x020010830000060002\x03\x0b\r
            'Expand':   b'0E0A\x0210830006\x03'  # \x0100AF12\x020010830000060006\x03\x0f\r
        }

        self.PIPPBPAspectUpdateStates = { # Responses:
            b'1' : 'Normal',              # \x0100AD12\x020010830000060001\x03\n\r
            b'2' : 'Full',                # \x0100AD12\x020010830000060002\x03\t\r
            b'6' : 'Expand'               # \x0100AD12\x020010830000060006\x03\r
        }

        self.AspectSetStates = {                      
            'Normal':   b'0E0A\x0202700001\x03',  # \x0100AF12\x020002700000070001\x03\x06\r
            'Full':     b'0E0A\x0202700002\x03',  # \x0100AF12\x020002700000070002\x03\x05\r
            'Wide':     b'0E0A\x0202700003\x03',  # \x0100AF12\x020002700000070003\x03\x04\r
            'Zoom':     b'0E0A\x0202700004\x03',  # \x0100AF12\x020002700000070004\x03\x03\r
            'Dynamic':  b'0E0A\x0202700006\x03',  # \x0100AF12\x020002700000070006\x03\x01\r
            '1:1':      b'0E0A\x0202700007\x03'   # \x0100AF12\x020002700000070007\x03\x00\r
        }

        self.AspectUpdateStates = { # Responses:
            b'1': 'Normal',         # \x0100AD12\x020002700000070001\x03\x04\r
            b'2': 'Full',           # \x0100AD12\x020002700000070002\x03\x07\r
            b'3': 'Wide',           # \x0100AD12\x020002700000070003\x03\x06\r
            b'4': 'Zoom',           # \x0100AD12\x020002700000070004\x03\x01\r
            b'6': 'Dynamic',        # \x0100AD12\x020002700000070006\x03\x03\r
            b'7': '1:1'             # \x0100AD12\x020002700000070007\x03\x02\r
        }

        self.PIPInputSet = {
            'DVI 1':       b'0003\x03', # \x0100AF12\x0200110E0000830003\x03x\r
            'DVI 2':       b'0004\x03', # \x0100AF12\x0200110E0000830004\x03\x7f\r
            'Option':      b'000D\x03', # \x0100AF12\x0200110E000083000D\x03\x0f\r
            'DisplayPort': b'000F\x03', # \x0100AF12\x0200110E000083000F\x03\r
            'HDMI 1':      b'0011\x03', # \x0100AF12\x0200110E0000830011\x03{\r
            'HDMI 2':      b'0012\x03', # \x0100AF12\x0200110E0000830012\x03x\r
            'HDMI 3':      b'0082\x03', # \x0100AF12\x0200110E0000830082\x03q\r
            'HDMI 4':      b'0083\x03'  # \x0100AF12\x0200110E0000830083\x03p\r
        }

        self.PIPInputUpdate = {
            b'03' : 'DVI 1',        # \x0100AD12\x0200110E0000830003\x03z\r
            b'04' : 'DVI 2',        # \x0100AD12\x0200110E0000830004\x03}\r
            b'0D' : 'Option',       # No Option Card
            b'0F' : 'DisplayPort',  # \x0100AD12\x02001111000083000F\x03z\r
            b'11' : 'HDMI 1',       # \x0100AD12\x020011110000830011\x03\x0c\r
            b'12' : 'HDMI 2',       # \x0100AD12\x0200110E0000830012\x03z\r
            b'82' : 'HDMI 3',       # \x0100AD12\x0200110E0000830082\x03s\r
            b'83' : 'HDMI 4'        # \x0100AD12\x0200110E0000830083\x03r\r
        }

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

