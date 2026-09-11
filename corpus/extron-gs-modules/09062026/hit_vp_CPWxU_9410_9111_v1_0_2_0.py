from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
import hashlib
from binascii import hexlify

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
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {
            'CP-WU9410': self.hit_1_147_others,
            'CP-WX9210': self.hit_1_147_others,
            'CP-X9110': self.hit_1_147_X911,
            'CP-WU9411': self.hit_1_147_others,
            'CP-WX9211': self.hit_1_147_others,
            'CP-X9111': self.hit_1_147_X911,
            }



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},       
            'AutoImage': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'ClosedCaptionChannel': { 'Status': {}},
            'ClosedCaptionMode': { 'Status': {}},
            'ErrorStatus': { 'Status': {}},
            'FilterTime': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampTime': {'Parameters':['Lamp'], 'Status': {}},
            'LampMode': { 'Status': {}},
            'LensMemory': { 'Status': {}},
            'LensMemoryIndex': { 'Status': {}},
            'PbyPLeftSource': { 'Status': {}},
            'PbyPMode': { 'Status': {}},
            'PbyPRightSource': { 'Status': {}},
            'PIPMainInput': { 'Status': {}},
            'PIPMode': { 'Status': {}}, 
            'PIPPosition': { 'Status': {}},
            'PIPSubInput': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},

            }

        self.Authenticated = 'Not Needed'
        self.Regex = compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2})')

        
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'([a-f0-9]{8})'), self.__MatchPassword, None)

    def SetPassword(self):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.SetPassword()

    def SetAspectRatio(self, value, qualifier):

        if value in self.AspectRatioStateValues:
            AspectRatioCmdString = self.AspectRatioStateValues[value]
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:       #res '\x1d\x00\x00
                value = self.AspectRatioStates[res[-2:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            'On' : b'\xBE\xEF\x03\x06\x00\x6A\x63\x01\x00\x00\x37\x01\x00', 
            'Off' : b'\xBE\xEF\x03\x06\x00\xFA\x62\x01\x00\x00\x37\x00\x00'
            }

        if value in ClosedCaptionStateValues:
            ClosedCaptionCmdString = ClosedCaptionStateValues[value]
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionStateNames = {
            b'\x00': 'Off',
            b'\x01': 'On',
            }

        ClosedCaptionCmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionStateNames[res[-2:-1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetClosedCaptionChannel(self, value, qualifier):

        ClosedCaptionChannelStateValues = {
            'CC1' : b'\xBE\xEF\x03\x06\x00\xD2\x62\x01\x00\x02\x37\x01\x00', 
            'CC2' : b'\xBE\xEF\x03\x06\x00\x22\x62\x01\x00\x02\x37\x02\x00',
            'CC3' : b'\xBE\xEF\x03\x06\x00\xB2\x63\x01\x00\x02\x37\x03\x00',
		    'CC4' : b'\xBE\xEF\x03\x06\x00\x82\x61\x01\x00\x02\x37\x04\x00'

            }

        if value in ClosedCaptionChannelStateValues:
            ClosedCaptionChannelCmdString = ClosedCaptionChannelStateValues[value]
            self.__SetHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaptionChannel')

    def UpdateClosedCaptionChannel(self, value, qualifier):

        ClosedCaptionChannelStateNames = {
            b'\x01': 'CC1',
            b'\x02': 'CC2',
            b'\x03': 'CC3',
            b'\x04': 'CC4',
            }

        ClosedCaptionChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionChannelStateNames[res[-2:-1]]
                self.WriteStatus('ClosedCaptionChannel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Channel: Invalid/unexpected response'])

    def SetClosedCaptionMode(self, value, qualifier):

        ClosedCaptionModeStateValues = {
            'Captions' : b'\xBE\xEF\x03\x06\x00\x06\x63\x01\x00\x01\x37\x00\x00', 
            'Text' : b'\xBE\xEF\x03\x06\x00\x96\x62\x01\x00\x01\x37\x01\x00'
            }

        if value in ClosedCaptionModeStateValues:
            ClosedCaptionModeCmdString = ClosedCaptionModeStateValues[value]
            self.__SetHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaptionMode')

    def UpdateClosedCaptionMode(self, value, qualifier):

        ClosedCaptionModeStateNames = {
            b'\x00': 'Captions',
            b'\x01': 'Text',
            }

        ClosedCaptionModeCmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionModeStateNames[res[-2:-1]]
                self.WriteStatus('ClosedCaptionMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Mode: Invalid/unexpected response'])

    def UpdateErrorStatus(self, value, qualifier):

        ErrorStatusStateNames = {
            b'\x00' : 'Normal',
            b'\x01' : 'Cover Error',
            b'\x02' : 'Fan Error',
            b'\x03' : 'Lamp Error',
            b'\x04' : 'Temp Error',
            b'\x05' : 'Air Flow Error',
            b'\x07' : 'Cold Error',
            b'\x08' : 'Filter Error',
            b'\x0F' : 'Shutter Error',
            b'\x10' : 'Lens Shift Error',
            b'\x13' : 'Lamp 1 Warning',
            b'\x23' : 'Lamp 2 Warning',
            b'\x41' : 'Humidity Error',
            b'\x52' : 'Color Wheel Error',
            b'\x53' : 'Active Iris Error',
            b'\x42' : 'Other Error',
            b'\x43' : 'Other Error',
            b'\x44' : 'Other Error',
            b'\x50' : 'Other Error',
            b'\x51' : 'Other Error',
            b'\x54' : 'Other Error',
            b'\x55' : 'Other Error',
            b'\x56' : 'Other Error'
            }

        ErrorStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('ErrorStatus', ErrorStatusCmdString, value, qualifier)
        if res:
            try:
                value = ErrorStatusStateNames[res[-2:-1]]
                self.WriteStatus('ErrorStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Error Status: Invalid/unexpected response'])

    def UpdateFilterTime(self, value, qualifier):

        FilterHighByteCommand = b'\xBE\xEF\x03\x06\x00\xD6\xFC\x02\x00\x9F\x10\x00\x00' #Higher Bytes
        resHighByte = self.__UpdateHelper('FilterTime', FilterHighByteCommand, value, qualifier)   
        FilterLowByteCommand = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00' #Lower Bytes
        resLowByte = self.__UpdateHelper('FilterTime', FilterLowByteCommand, value, qualifier)
        if resLowByte:
            try:
                FilterTime = resLowByte[1] + 256*resHighByte[1]
                self.WriteStatus('FilterTime', FilterTime, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Time: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFilterTime')        

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On' : b'\xBE\xEF\x03\x06\x00\x13\xD3\x01\x00\x02\x30\x01\x00', 
            'Off' : b'\xBE\xEF\x03\x06\x00\x83\xD2\x01\x00\x02\x30\x00\x00'
            }
        
        if value in FreezeStateValues:
            FreezeCmdString = FreezeStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeStateNames = {
            b'\x00': 'Off',
            b'\x01': 'On',
            }

        FreezeCmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeStateNames[res[-2:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Computer 1' : b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer 2' : b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'LAN' : b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'HDMI 1' : b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'HDMI 2' : b'\xBE\xEF\x03\x06\x00\x6E\xD6\x01\x00\x00\x20\x0D\x00',
            'DVI':b'\xBE\xEF\x03\x06\x00\xAE\xD4\x01\x00\x00\x20\x09\x00',
            'HDBaseT':b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x00\x20\x11\x00',
            'Video':b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00'
            }

        if value in InputStateValues:
            InputCmdString = InputStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputStateNames = {
            b'\x00' : 'Computer 1',
            b'\x04' : 'Computer 2',
            b'\x0B' : 'LAN',
            b'\x03' : 'HDMI 1',
            b'\x0D' : 'HDMI 2',
            b'\x09' : 'DVI',
            b'\x11' : 'HDBaseT',
            b'\x01' : 'Video'
            }

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputStateNames[res[-2:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Normal' : b'\xBE\xEF\x03\x06\x00\x3B\x23\x01\x00\x00\x33\x00\x00', 
            'Eco' : b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00'
            }

        if value in LampModeStateValues:
            LampModeCmdString = LampModeStateValues[value]
            self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLampMode')

    def UpdateLampMode(self, value, qualifier):

        LampModeStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Eco',
            }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeStateNames[res[-2:-1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampTime(self, value, qualifier):

        lamp = qualifier['Lamp']
        if int(lamp) < 1 or int(lamp) > 2:
            self.Discard('Invalid Command for UpdateLampTime')
        else:
            if lamp == '1':
                Lamp1HighByteCommand = b'\xBE\xEF\x03\x06\x00\x2A\xFD\x02\x00\x9E\x10\x00\x00' #Higher Bytes
                resHighByte = self.__UpdateHelper('LampTime', Lamp1HighByteCommand, value, qualifier)   
                Lamp1LowByteCommand = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00' #Lower Bytes
                resLowByte = self.__UpdateHelper('LampTime', Lamp1LowByteCommand, value, qualifier)
            elif lamp == '2':
                Lamp2HighByteCommand = b'\xBE\xEF\x03\x06\x00\xFE\xAF\x02\x00\x91\x11\x00\x00' #Higher Bytes
                resHighByte = self.__UpdateHelper('LampTime', Lamp2HighByteCommand, value, qualifier)   
                Lamp2LowByteCommand = b'\xBE\xEF\x03\x06\x00\x02\xAE\x02\x00\x90\x11\x00\x00' #Lower Bytes
                resLowByte = self.__UpdateHelper('LampTime', Lamp2LowByteCommand, value, qualifier)
            if resLowByte:
                try:
                    LampTime = resLowByte[1] + 256*resHighByte[1]
                    self.WriteStatus('LampTime', LampTime, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Lamp Time: Invalid/unexpected response'])
            else:
                self.Discard('Invalid Command for UpdateLampTime')       

    def SetLensMemory(self, value, qualifier):

        LensMemoryStateValues = {
            'Clear' : b'\xBE\xEF\x03\x06\x00\x50\x91\x06\x00\x0A\x24\x00\x00', 
            'Load' : b'\xBE\xEF\x03\x06\x00\xE8\x90\x06\x00\x08\x24\x00\x00',
	        'Save' : b'\xBE\xEF\x03\x06\x00\x14\x91\x06\x00\x09\x24\x00\x00'
            }

        if value in LensMemoryStateValues:
            LensMemoryCmdString = LensMemoryStateValues[value]
            self.__SetHelper('LensMemory', LensMemoryCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLensMemory')
    def SetLensMemoryIndex(self, value, qualifier):

        LensMemoryIndexStateValues = {
            '1' : b'\xBE\xEF\x03\x06\x00\x4B\x92\x01\x00\x07\x24\x00\x00', 
            '2' : b'\xBE\xEF\x03\x06\x00\xDB\x93\x01\x00\x07\x24\x01\x00',
            '3' : b'\xBE\xEF\x03\x06\x00\x2B\x93\x01\x00\x07\x24\x02\x00'
            }

        if value in LensMemoryIndexStateValues:
            LensMemoryIndexCmdString = LensMemoryIndexStateValues[value]
            self.__SetHelper('LensMemoryIndex', LensMemoryIndexCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLensMemoryIndex')

    def UpdateLensMemoryIndex(self, value, qualifier):

        LensMemoryIndexStateNames = {
            b'\x00': '1',
            b'\x01': '2',
	        b'\x02': '3'
            }

        LensMemoryIndexCmdString = b'\xBE\xEF\x03\x06\x00\x78\x92\x02\x00\x07\x24\x00\x00'
        res = self.__UpdateHelper('LensMemoryIndex', LensMemoryIndexCmdString, value, qualifier)
        if res:
            try:
                value = LensMemoryIndexStateNames[res[-2:-1]]
                self.WriteStatus('LensMemoryIndex', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lens Memory Index: Invalid/unexpected response'])

    def SetPbyPLeftSource(self, value, qualifier):

        PbyPLeftSourceStateValues = {
            'Computer 1' : b'\xBE\xEF\x03\x06\x00\xF2\x26\x01\x00\x15\x23\x00\x00',
            'Computer 2' : b'\xBE\xEF\x03\x06\x00\x32\x24\x01\x00\x15\x23\x04\x00',
            'HDMI 1' : b'\xBE\xEF\x03\x06\x00\x02\x26\x01\x00\x15\x23\x03\x00',
            'HDMI 2' : b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x15\x23\x0D\x00',
            'DVI':b'\xBE\xEF\x03\x06\x00\xA2\x20\x01\x00\x15\x23\x09\x00',
            'HDBaseT':b'\xBE\xEF\x03\x06\x00\xA2\x2A\x01\x00\x15\x23\x11\x00',
            'Video':b'\xBE\xEF\x03\x06\x00\x62\x27\x01\x00\x15\x23\x01\x00'
            }

        if value in PbyPLeftSourceStateValues:
            PbyPLeftSourceCmdString = PbyPLeftSourceStateValues[value]
            self.__SetHelper('PbyPLeftSource', PbyPLeftSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPbyPLeftSource')

    def UpdatePbyPLeftSource(self, value, qualifier):

        PbyPLeftSourceStateNames = {
            b'\x00' : 'Computer 1',
            b'\x04' : 'Computer 2',
            b'\x03' : 'HDMI 1',
            b'\x0D' : 'HDMI 2',
            b'\x09' : 'DVI',
            b'\x11' : 'HDBaseT',
            b'\x01' : 'Video'
            }

        PbyPLeftSourceCmdString = b'\xBE\xEF\x03\x06\x00\xC1\x26\x02\x00\x15\x23\x00\x00'
        res = self.__UpdateHelper('PbyPLeftSource', PbyPLeftSourceCmdString, value, qualifier)
        if res:
            try:
                value = PbyPLeftSourceStateNames[res[-2:-1]]
                self.WriteStatus('PbyPLeftSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Left Source: Invalid/unexpected response'])

    def SetPbyPMode(self, value, qualifier):

        PbyPModeStateValues = {
            'On' : b'\xBE\xEF\x03\x06\x00\xAE\x27\x01\x00\x10\x23\x01\x00', 
            'Off' : b'\xBE\xEF\x03\x06\x00\x3E\x26\x01\x00\x10\x23\x00\x00'
            }

        if value in PbyPModeStateValues:
            PbyPModeCmdString = PbyPModeStateValues[value]
            self.__SetHelper('PbyPMode', PbyPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPbyPMode')

    def UpdatePbyPMode(self, value, qualifier):

        PbyPModeStateNames = {
            b'\x00': 'Off',
            b'\x01': 'On',
            b'\x02' : 'Off',
            }

        PbyPModeCmdString = b'\xBE\xEF\x03\x06\x00\x0D\x26\x02\x00\x10\x23\x00\x00'
        res = self.__UpdateHelper('PbyPMode', PbyPModeCmdString, value, qualifier)
        if res:
            try:
                value = PbyPModeStateNames[res[-2:-1]]
                self.WriteStatus('PbyPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Mode: Invalid/unexpected response'])

    def SetPbyPRightSource(self, value, qualifier):

        PbyPRightSourceStateValues = {
            'Computer 1' : b'\xBE\xEF\x03\x06\x00\x86\x27\x01\x00\x12\x23\x00\x00',
            'Computer 2' : b'\xBE\xEF\x03\x06\x00\x46\x25\x01\x00\x12\x23\x04\x00',
            'HDMI 1' : b'\xBE\xEF\x03\x06\x00\x76\x27\x01\x00\x12\x23\x03\x00',
            'HDMI 2' : b'\xBE\xEF\x03\x06\x00\x16\x23\x01\x00\x12\x23\x0D\x00',
            'DVI':b'\xBE\xEF\x03\x06\x00\xD6\x21\x01\x00\x12\x23\x09\x00',
            'HDBaseT':b'\xBE\xEF\x03\x06\x00\xD6\x2B\x01\x00\x12\x23\x11\x00',
            'Video':b'\xBE\xEF\x03\x06\x00\x16\x26\x01\x00\x12\x23\x01\x00'
            }

        if value in PbyPRightSourceStateValues:
            PbyPRightSourceCmdString = PbyPRightSourceStateValues[value]
            self.__SetHelper('PbyPRightSource', PbyPRightSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPbyPRightSource')

    def UpdatePbyPRightSource(self, value, qualifier):

        PbyPRightSourceStateNames = {
            b'\x00' : 'Computer 1',
            b'\x04' : 'Computer 2',
            b'\x03' : 'HDMI 1',
            b'\x0D' : 'HDMI 2',
            b'\x09' : 'DVI',
            b'\x11' : 'HDBaseT',
            b'\x01' : 'Video'
            }

        PbyPRightSourceCmdString = b'\xBE\xEF\x03\x06\x00\xB5\x27\x02\x00\x12\x23\x00\x00'
        res = self.__UpdateHelper('PbyPRightSource', PbyPRightSourceCmdString, value, qualifier)
        if res:
            try:
                value = PbyPRightSourceStateNames[res[-2:-1]]
                self.WriteStatus('PbyPRightSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Right Source: Invalid/unexpected response'])

    def SetPIPMainInput(self, value, qualifier):

        PIPMainInputStateValues = {
            'Computer 1' : b'\xBE\xEF\x03\x06\x00\xCE\x23\x01\x00\x04\x23\x00\x00',
            'Computer 2' : b'\xBE\xEF\x03\x06\x00\x0E\x21\x01\x00\x04\x23\x04\x00',
            'HDMI 1' : b'\xBE\xEF\x03\x06\x00\x3E\x23\x01\x00\x04\x23\x03\x00',
            'HDMI 2' : b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x04\x23\x0D\x00',
            'DVI':b'\xBE\xEF\x03\x06\x00\x9E\x25\x01\x00\x04\x23\x09\x00',
            'HDBaseT':b'\xBE\xEF\x03\x06\x00\x9E\x2F\x01\x00\x04\x23\x11\x00',
            'Video':b'\xBE\xEF\x03\x06\x00\x5E\x22\x01\x00\x04\x23\x01\x00'
            }

        if value in PIPMainInputStateValues:
            PIPMainInputCmdString = PIPMainInputStateValues[value]
            self.__SetHelper('PIPMainInput', PIPMainInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMainInput')

    def UpdatePIPMainInput(self, value, qualifier):

        PIPMainInputStateNames = {
            b'\x00' : 'Computer 1',
            b'\x04' : 'Computer 2',
            b'\x03' : 'HDMI 1',
            b'\x0D' : 'HDMI 2',
            b'\x09' : 'DVI',
            b'\x11' : 'HDBaseT',
            b'\x01' : 'Video'
            }

        PIPMainInputCmdString = b'\xBE\xEF\x03\x06\x00\xFD\x23\x02\x00\x04\x23\x00\x00'
        res = self.__UpdateHelper('PIPMainInput', PIPMainInputCmdString, value, qualifier)
        if res:
            try:
                value = PIPMainInputStateNames[res[-2:-1]]
                self.WriteStatus('PIPMainInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Main Input: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        PIPModeStateValues = {
            'On' : b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x10\x23\x02\x00', 
            'Off' : b'\xBE\xEF\x03\x06\x00\x3E\x26\x01\x00\x10\x23\x00\x00'
            }

        if value in PIPModeStateValues:
            PIPModeCmdString = PIPModeStateValues[value]
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def UpdatePIPMode(self, value, qualifier):

        PIPModeStateNames = {
            b'\x00': 'Off',
            b'\x02': 'On',
            b'\x01': 'Off', 
            }

        PIPModeCmdString = b'\xBE\xEF\x03\x06\x00\x0D\x26\x02\x00\x10\x23\x00\x00'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = PIPModeStateNames[res[-2:-1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPIPPosition(self, value, qualifier):

        PIPPositionStateValues = {
            'Top Left' : b'\xBE\xEF\x03\x06\x00\x02\x23\x01\x00\x01\x23\x00\x00',
            'Top Right' : b'\xBE\xEF\x03\x06\x00\x92\x22\x01\x00\x01\x23\x01\x00',
            'Bottom Left' : b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x01\x23\x02\x00',
            'Bottom Right' : b'\xBE\xEF\x03\x06\x00\xF2\x23\x01\x00\x01\x23\x03\x00'
        }

        if value in PIPPositionStateValues:
            PIPPositionCmdString = PIPPositionStateValues[value]
            self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPosition')

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionStateNames = {
            b'\x00' : 'Top Left',
            b'\x01' : 'Top Right',
            b'\x02' : 'Bottom Left',
            b'\x03' : 'Bottom Right'
            }

        PIPPositionCmdString = b'\xBE\xEF\x03\x06\x00\x31\x23\x02\x00\x01\x23\x00\x00'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = PIPPositionStateNames[res[-2:-1]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position: Invalid/unexpected response'])

    def SetPIPSubInput(self, value, qualifier):

        PIPSubInputStateValues = {
            'Computer 1' : b'\xBE\xEF\x03\x06\x00\x46\x23\x01\x00\x02\x23\x00\x00',
            'Computer 2' : b'\xBE\xEF\x03\x06\x00\x86\x21\x01\x00\x02\x23\x04\x00',
            'HDMI 1' : b'\xBE\xEF\x03\x06\x00\xB6\x23\x01\x00\x02\x23\x03\x00',
            'HDMI 2' : b'\xBE\xEF\x03\x06\x00\xD6\x27\x01\x00\x02\x23\x0D\x00',
            'DVI':b'\xBE\xEF\x03\x06\x00\x16\x25\x01\x00\x02\x23\x09\x00',
            'HDBaseT':b'\xBE\xEF\x03\x06\x00\x16\x2F\x01\x00\x02\x23\x11\x00',
            'Video':b'\xBE\xEF\x03\x06\x00\xD6\x22\x01\x00\x02\x23\x01\x00'
            }

        if value in PIPSubInputStateValues:
            PIPSubInputCmdString = PIPSubInputStateValues[value]
            self.__SetHelper('PIPSubInput', PIPSubInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSubInput')

    def UpdatePIPSubInput(self, value, qualifier):

        PIPSubInputStateNames = {
            b'\x00' : 'Computer 1',
            b'\x04' : 'Computer 2',
            b'\x03' : 'HDMI 1',
            b'\x0D' : 'HDMI 2',
            b'\x09' : 'DVI',
            b'\x11' : 'HDBaseT',
            b'\x01' : 'Video'
            }

        PIPSubInputCmdString = b'\xBE\xEF\x03\x06\x00\x75\x23\x02\x00\x02\x23\x00\x00'
        res = self.__UpdateHelper('PIPSubInput', PIPSubInputCmdString, value, qualifier)
        if res:
            try:
                value = PIPSubInputStateNames[res[-2:-1]]
                self.WriteStatus('PIPSubInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Sub Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On' : b'\xBE\xEF\x03\x06\x00\xBA\xD2\x01\x00\x00\x60\x01\x00',
            'Off' : b'\xBE\xEF\x03\x06\x00\x2A\xD3\x01\x00\x00\x60\x00\x00'
            }

        if value in PowerStateValues:
            PowerCmdString = PowerStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            b'\x00' : 'Off',
            b'\x01' : 'On',
            b'\x02' : 'Cooling',
            }
        PowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateNames[res[-2:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On' : b'\xBE\xEF\x03\x06\x00\x6B\xD9\x01\x00\x20\x30\x01\x00',
            'Off' : b'\xBE\xEF\x03\x06\x00\xFB\xD8\x01\x00\x20\x30\x00\x00'
            }

        if value in VideoMuteStateValues:
            VideoMuteCmdString = VideoMuteStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteStateNames = {
            b'\x00' : 'Off',
            b'\x01' : 'On'
            }
        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteStateNames[res[-2:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
   
        DEVICE_ERROR_CODES = {
            b'\x15': "Invalid Command",
            b'\x1C': "Projector Error",
            b'\x1F': "Authentication Error",
        }
        if response[0:1] in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
            if response[0:1] == b'\x1F':
                self.Authenticated = 'None'
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        elif command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Regex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:    
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Regex)
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'

    def hit_1_147_others(self):
        self.AspectRatioStateValues = {
            '4:3'    : b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00', 
            '16:9'   : b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00', 
            '16:10'  : b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9'   : b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Native' : b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00', 
            'Normal' : b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
            }

        self.AspectRatioStates ={
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x09': '14:9',
            b'\x0A': '16:10',
            b'\x08': 'Native',
            b'\x10': 'Normal'
        }


    def hit_1_147_X911(self):
        self.AspectRatioStateValues = {
            '4:3'    : b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00', 
            '16:9'   : b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00', 
            '16:10'  : b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9'   : b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Normal' : b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
            }

        self.AspectRatioStates ={
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x09': '14:9',
            b'\x0A': '16:10',
            b'\x10': 'Normal'
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
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

