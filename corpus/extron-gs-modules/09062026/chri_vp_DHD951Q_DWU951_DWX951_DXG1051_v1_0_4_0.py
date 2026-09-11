from extronlib.interface import SerialInterface, EthernetClientInterface
import struct
import re
from binascii import hexlify

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
            'DHD951-Q': self.chri_1_656_dhd951,
            'DWU951': self.chri_1_656_other,
            'DHD951': self.chri_1_656_dhd951,
            'DWX951': self.chri_1_656_other,
            'DXG1051': self.chri_1_656_other,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Blank': { 'Status': {}},
            'BlankColor': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'ClosedCaptionChannel': { 'Status': {}},
            'ClosedCaptionMode': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'EcoMode': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': {'Parameters':['Lamp'], 'Status': {}},
            'LensMemoryIndex': { 'Status': {}},
            'LensMemoryLoad': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'Shutter': { 'Status': {}},
        }
        
        self.Authenticated = 'Not Needed' 
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'([a-f0-9]{8})'), self.__MatchPassword, None)

        self.setRegex = re.compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2})')
        self.updateRegex = re.compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2})')

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):

        value = match.group(1).decode()
        if value == '\x1F\x04\x00':
            self.Authenticated = 'None'
            self.Error(['Authentication Error'])
        else:      
            self.SetPassword( value, None)
      
    def SetAspectRatio(self, value, qualifier):  
    
        AR_Values = {
            'Normal' : (0x5E, 0xDD, 0x10) ,
            '4:3'    : (0x9E, 0xD0, 0x00) ,
            '16:9'   : (0x0E, 0xD1, 0x01) ,
            '16:10'  : (0x3E, 0xD6, 0x0A) ,
            '14:9'   : (0xCE, 0xD6, 0x09) ,
            'Native' : (0x5E, 0xD7, 0x08) ,
        }

        CmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, AR_Values[value][0], AR_Values[value][1], 0x01, 0x00, \
                                0x08, 0x20, AR_Values[value][2], 0x00)
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)  

    def UpdateAspectRatio(self, value, qualifier): 

        AR_State = {
            0x10: 'Normal' ,
            0x00: '4:3'    ,
            0x01: '16:9'   ,
            0x0A: '16:10'  ,
            0x09: '14:9'   ,
            0x08: 'Native' ,
        }

        CmdString =  b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00' 
        res = self.__UpdateHelper('AspectRatio', CmdString, value, qualifier) 
        if res:
            try:
                value= AR_State[res[1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetBlank(self, value, qualifier):

        ValueStateValues = {
            'Off'  : (0xFB, 0xD8, 0x00),
            'On'   : (0x6B, 0xD9, 0x01)
        }

        BlankCmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, ValueStateValues[value][0], ValueStateValues[value][1], 0x01, 0x00, \
                                     0x20, 0x30, ValueStateValues[value][2], 0x00)
        self.__SetHelper('Blank', BlankCmdString, value, qualifier)

    def UpdateBlank(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'On', 
            0x00 : 'Off'
        }

        BlankCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('Blank', BlankCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Blank', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Blank: Invalid/unexpected response'])

    def SetBlankColor(self, value, qualifier):

        ValueStateValues = {
            'My Screen' : (0xFB, 0xCA, 0x20), 
            'Original'  : (0xFB, 0xE2, 0x40), 
            'Blue'      : (0xCB, 0xD3, 0x03), 
            'White'     : (0x6B, 0xD0, 0x05), 
            'Black'     : (0x9B, 0xD0, 0x06)
        }

        BlankColorCmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, ValueStateValues[value][0], ValueStateValues[value][1], \
                                            0x01, 0x00, 0x00, 0x30, ValueStateValues[value][2], 0x00 )
        self.__SetHelper('BlankColor', BlankColorCmdString, value, qualifier)

    def UpdateBlankColor(self, value, qualifier):

        ValueStateValues = {
            0x20 : 'My Screen', 
            0x40 : 'Original', 
            0x03 : 'Blue', 
            0x05 : 'White', 
            0x06 : 'Black'
        }

        BlankColorCmdString = b'\xBE\xEF\x03\x06\x00\x08\xD3\x02\x00\x00\x30\x00\x00'
        res = self.__UpdateHelper('BlankColor', BlankColorCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('BlankColor', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Blank Color: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):  
    
        CC_Values = {
            'Off' : (0xFA, 0x62, 0x00) ,
            'On'  : (0x6A, 0x63, 0x01) ,
        }

        CmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, CC_Values[value][0], CC_Values[value][1], 0x01, 0x00, \
                                0x00, 0x37, CC_Values[value][2], 0x00)
        self.__SetHelper('ClosedCaption', CmdString, value, qualifier)  

    def UpdateClosedCaption(self, value, qualifier): 


        CC_State = {
            0x10: 'On' ,
            0x00: 'Off' ,
        }
        CmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaption', CmdString, value, qualifier) 
        if res:
            try:
                value= CC_State[res[1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetClosedCaptionChannel(self, value, qualifier):

        ValueStateValues = {
            '1' : (0xD2, 0x62, 0x01), 
            '2' : (0x22, 0x62, 0x02), 
            '3' : (0xB2, 0x63, 0x03), 
            '4' : (0x82, 0x61, 0x04)
        }

        ClosedCaptionChannelCmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, ValueStateValues[value][0], ValueStateValues[value][1], \
                                                       0x01, 0x00, 0x02, 0x37, ValueStateValues[value][2], 0x00 )
        self.__SetHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)

    def UpdateClosedCaptionChannel(self, value, qualifier):

        ValueStateValues = {
            0x01 : '1', 
            0x02 : '2', 
            0x03 : '3', 
            0x04 : '4'
        }

        ClosedCaptionChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ClosedCaptionChannel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Channel: Invalid/unexpected response'])

    def SetClosedCaptionMode(self, value, qualifier):

        ValueStateValues = {
            'Captions' : (0x06, 0x63, 0x00), 
            'Text'     : (0x96, 0x62, 0x01)
        }

        ClosedCaptionModeCmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, ValueStateValues[value][0], ValueStateValues[value][1], \
                                                  0x01, 0x00, 0x01, 0x37, ValueStateValues[value][2], 0x00 )
        self.__SetHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)

    def UpdateClosedCaptionMode(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Captions', 
            0x01 : 'Text'
        }

        ClosedCaptionModeCmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ClosedCaptionMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Mode: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Normal', 
            0x01 : 'Cover Error', 
            0x02 : 'Fan Error', 
            0x03 : 'Lamp Error', 
            0x04 : 'Temp Error', 
            0x05 : 'Air flow Error', 
            0x07 : 'Cold Error', 
            0x08 : 'Filter Error', 
            0x0F : 'Shutter Error', 
            0x10 : 'Lens Shift Error', 
            0x13 : 'Lamp 1 Warning', 
            0x23 : 'Lamp 2 Warning', 
            0x41 : 'Humidity Error', 
            0x52 : 'Color Wheel Error', 
            0x53 : 'Dynamic Iris Error', 
            0x40 : 'Other Error',
            0x42 : 'Other Error',
            0x43 : 'Other Error',
            0x44 : 'Other Error',
            0x50 : 'Other Error',
            0x51 : 'Other Error',
            0x54 : 'Other Error',
            0x55 : 'Other Error',
            0x56 : 'Other Error',
        }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'Normal' : (0x3B, 0x23, 0x00), 
            'Eco'    : (0xAB, 0x22, 0x01)
        }

        EcoModeCmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, ValueStateValues[value][0], ValueStateValues[value][1], \
                                        0x01, 0x00, 0x00, 0x33, ValueStateValues[value][2], 0x00)
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Normal', 
            0x01 : 'Eco'
        }

        EcoModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('EcoMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Eco Mode: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off'  : (0x3B, 0xEF, 0x00), 
            'On'   : (0xAB, 0xEE, 0x01)
        }

        ExecutiveModeCmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, ValueStateValues[value][0], ValueStateValues[value][1], \
                                               0x01, 0x00, 0xC0, 0x30, ValueStateValues[value][2], 0x00)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'On', 
            0x00 : 'Off'
        }

        ExecutiveModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\xEF\x02\x00\xC0\x30\x00\x00'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[2:3])*256 + ord(res[1:2])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):  
    
        Frz_Values = {
            'Off' : (0x83, 0xD2, 0x00) ,
            'On'  : (0x13, 0xD3, 0x01) ,
        }

        CmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, Frz_Values[value][0], Frz_Values[value][1], 0x01, 0x00, \
                                0x02, 0x30, Frz_Values[value][2], 0x00)
        self.__SetHelper('Freeze', CmdString, value, qualifier)  

    def UpdateFreeze(self, value, qualifier): 


        Frz_State = {
            0x00  : 'Off'  ,
            0x01  : 'On'   ,
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', CmdString, value, qualifier) 
        if res:
            try:
                value= Frz_State[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):  
    
        CmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, self.Inp_Values[value][0], self.Inp_Values[value][1], 0x01, 0x00, \
                                0x00, 0x20, self.Inp_Values[value][2], 0x00)
        self.__SetHelper('Input', CmdString, value, qualifier)  

    def UpdateInput(self, value, qualifier): 

        CmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', CmdString, value, qualifier) 
        if res:
            try:
                value = self.Inp_State[res[1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):  
    
        Lamp_Values = {
            'Dual'       : (0x1F, 0x21, 0x00) ,
            'Lamp 1'     : (0x8F, 0x20, 0x01) ,
            'Lamp 2'     : (0x7F, 0x20, 0x02) ,
            'Alternate'  : (0xDF, 0x2C, 0x10) ,
        }

        CmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, Lamp_Values[value][0], Lamp_Values[value][1], 0x01, 0x00, \
                                0x0B, 0x33, Lamp_Values[value][2], 0x00)
        self.__SetHelper('LampMode', CmdString, value, qualifier)  

    def UpdateLampMode(self, value, qualifier): 


        Lamp_State = {
            0x00  :  'Dual'      ,
            0x01  :  'Lamp 1'    ,
            0x02  :  'Lamp 2'    ,
            0x10  :  'Alternate' ,
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x2C\x21\x02\x00\x0B\x33\x00\x00'
        res = self.__UpdateHelper('LampMode', CmdString, value, qualifier) 
        if res:
            try:
                value= Lamp_State[res[1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier): 


        Lamp_Num = {
            '1'  :  (0xC2, 0xFF, 0x90, 0x10),
            '2'  :  (0x02, 0xAE, 0x90, 0x11),
        }

        lamp_val = qualifier['Lamp']

        CmdString =  struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, Lamp_Num[lamp_val][0], Lamp_Num[lamp_val][1], 0x02, 0x00, \
                                Lamp_Num[lamp_val][2], Lamp_Num[lamp_val][3], 0x00, 0x00)
        res = self.__UpdateHelper('LampUsage', CmdString, value, qualifier) 
        if res:
            try:
                value = ord(res[2:3])*256 + ord(res[1:2])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetLensMemoryIndex(self, value, qualifier):

        ValueStateValues = {
            '1' : b'\xBE\xEF\x03\x06\x00\x4B\x92\x01\x00\x07\x24\x00\x00', #Page 1, Christie Protocolo Lens Memory.pdf
            '2' : b'\xBE\xEF\x03\x06\x00\xDB\x93\x01\x00\x07\x24\x01\x00',
            '3' : b'\xBE\xEF\x03\x06\x00\x2B\x93\x01\x00\x07\x24\x02\x00' 
        }

        LensMemoryIndexCmdString = ValueStateValues[value]
        self.__SetHelper('LensMemoryIndex', LensMemoryIndexCmdString, value, qualifier)
    
    def UpdateLensMemoryIndex(self, value, qualifier):


        ValueStateValues = {
            0x00  :  '1',
            0x01  :  '2',
            0x02  :  '3'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x78\x92\x02\x00\x07\x24\x00\x00'
        res = self.__UpdateHelper('LampMode', CmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('LensMemoryIndex', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lens Memory Index: Invalid/unexpected response'])

    def SetLensMemoryLoad(self, value, qualifier):

        LensMemoryLoadCmdString = b'\xBE\xEF\x03\x06\x00\xE8\x90\x06\x00\x08\x24\x00\x00' #Page 2, Christie Protocolo Lens Memory.pdf
        self.__SetHelper('LensMemoryLoad', LensMemoryLoadCmdString, value, qualifier)
    def SetOnScreenDisplay(self, value, qualifier):  
    
        OSD_Values = {
            'Off'    : (0x8F, 0xD6, 0x00) ,
            'On'     : (0x1F, 0xD7, 0x01) ,
            'Hide'   : (0xEF, 0xD7, 0x02) ,
        }

        CmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, OSD_Values[value][0], OSD_Values[value][1], 0x01, 0x00, \
                                0x17, 0x30, OSD_Values[value][2], 0x00)
        self.__SetHelper('OnScreenDisplay', CmdString, value, qualifier)  

    def UpdateOnScreenDisplay(self, value, qualifier): 


        OSD_State = {
            0x00  :  'Off' ,
            0x01  :  'On'  ,
            0x02  :  'Hide',
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xBC\xD6\x02\x00\x17\x30\x00\x00'
        res = self.__UpdateHelper('OnScreenDisplay', CmdString, value, qualifier) 
        if res:
            try:
                value= OSD_State[res[1]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard'   : (0x83, 0xF5, 0x06), 
            'Natural'    : (0x23, 0xF6, 0x00), 
            'Cinema'     : (0xB3, 0xF7, 0x01), 
            'Dynamic'    : (0xE3, 0xF4, 0x04), 
            'BlackBoard' : (0xE3, 0xEF, 0x20), 
            'GreenBoard' : (0x73, 0xEE, 0x21), 
            'WhiteBoard' : (0x83, 0xEE, 0x22), 
            'Daytime'    : (0xE3, 0xC7, 0x40), 
            'Dicom'      : (0x73, 0xC6, 0x41), 
            'User 1'     : (0xE3, 0xFB, 0x10), 
            'User 2'     : (0x73, 0xFA, 0x11), 
            'User 3'     : (0x83, 0xFA, 0x12)
        }

        PictureModeCmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, ValueStateValues[value][0], ValueStateValues[value][1], \
                                           0x01, 0x00, 0xBA, 0x30, ValueStateValues[value][2], 0x00 )
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            0x06 : 'Standard', 
            0x00 : 'Natural', 
            0x01 : 'Cinema', 
            0x04 : 'Dynamic', 
            0x20 : 'BlackBoard', 
            0x21 : 'GreenBoard', 
            0x22 : 'WhiteBoard', 
            0x40 : 'Daytime', 
            0x41 : 'Dicom', 
            0x10 : 'User 1', 
            0x11 : 'User 2', 
            0x12 : 'User 3'
        }

        PictureModeCmdString = b'\xBE\xEF\x03\x06\x00\x10\xF6\x02\x00\xBA\x30\x00\x00'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):  
    
        Power_Values = {
            'Off'    : (0x2A, 0xD3, 0x00) ,
            'On'     : (0xBA, 0xD2, 0x01) ,
        }

        CmdString = struct.pack('>13B', 0xBE, 0xEF, 0x03, 0x06, 0x00, Power_Values[value][0], Power_Values[value][1], 0x01, 0x00, \
                                0x00, 0x60, Power_Values[value][2], 0x00)
        self.__SetHelper('Power', CmdString, value, qualifier)  

    def UpdatePower(self, value, qualifier): 


        Power_State = {
            0x00  :  'Off',
            0x01  :  'On',
            0x02  :  'Cooling Down',
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', CmdString, value, qualifier)
        if res:
            try:
                value = Power_State[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xBE\xEF\x03\x06\x00\x63\x92\x01\x00\x05\x24\x01\x00',
            'Off' : b'\xBE\xEF\x03\x06\x00\xF3\x93\x01\x00\x05\x24\x00\x00'
        }
        ShutterCmdString = ValueStateValues[value]
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }
        ShutterCmdString = b'\xBE\xEF\x03\x06\x00\xC0\x93\x02\x00\x05\x24\x00\x00'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

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

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=.5):
        self.Debug = True



        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.setRegex)
                if not res:
                    self.Error(['No response received'])
                else:
                    response = self.__CheckResponseForErrors(command + ':' + str(commandstring), res)

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
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.updateRegex)
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command + ':' + str(commandstring), res)
            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def chri_1_656_dhd951(self):

        self.Inp_Values = {
            'PC'            : (0xFE, 0xD2, 0x00) ,
            'LAN'           : (0xCE, 0xD5, 0x0B) ,
            'HDMI 1'        : (0x0E, 0xD2, 0x03) ,
            'HDMI 2'        : (0x6E, 0xD6, 0x0D) ,
            'DVI-D'         : (0xAE, 0xD4, 0x09) ,
            'HDBaseT'       : (0xAE, 0xDE, 0x11) ,
            'SDI/DIGITAL 1' : (0x5E, 0xDE, 0x12) ,
            'VIDEO'         : (0x6E, 0xD3, 0x01) ,
        }

        self.Inp_State = {
            0x00   : 'PC'           ,
            0x0B   : 'LAN'          ,
            0x03   : 'HDMI 1'       ,
            0x0D   : 'HDMI 2'       ,
            0x09   : 'DVI-D'        ,
            0x11   : 'HDBaseT'      ,
            0x12   : 'SDI/DIGITAL 1',
            0x01   : 'VIDEO'        ,
        }

    def chri_1_656_other(self):

        self.Inp_Values = {
            'PC'            : (0xFE, 0xD2, 0x00) ,
            'LAN'           : (0xCE, 0xD5, 0x0B) ,
            'HDMI 1'        : (0x0E, 0xD2, 0x03) ,
            'HDMI 2'        : (0x6E, 0xD6, 0x0D) ,
            'DVI-D'         : (0xAE, 0xD4, 0x09) ,
            'HDBaseT'       : (0xAE, 0xDE, 0x11) ,
            'VIDEO'         : (0x6E, 0xD3, 0x01) ,
            'PC 2'          : (0x3E, 0xD0, 0x04) ,
        }
        self.Inp_State = {
            0x00   : 'PC'           ,
            0x0B   : 'LAN'          ,
            0x03   : 'HDMI 1'       ,
            0x0D   : 'HDMI 2'       ,
            0x09   : 'DVI-D'        ,
            0x11   : 'HDBaseT'      ,
            0x01   : 'VIDEO'        ,
            0x04   : 'PC 2'         ,
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

