from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
from re import compile, search
from extronlib.system import Wait

class DeviceClass(): 
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {
            'EB-B1575WU': self.epsn_1_212_Other,
            'EB-Z9750WU': self.epsn_1_212_Other,
            'EB-Z8450WU': self.epsn_1_212_Other,
            'EB-Z8455WU': self.epsn_1_212_Other,
            'PowerLite Pro Z8450WU': self.epsn_1_212_Other,
            'PowerLite Pro Z8455WU': self.epsn_1_212_Other,
            'EB-Z9850W': self.epsn_1_212_Other,
            'EB-Z9805W': self.epsn_1_212_Other,
            'EB-Z8355W': self.epsn_1_212_Other,
            'EB-Z8350W': self.epsn_1_212_Other,
            'EB-B1585W': self.epsn_1_212_Other,
            'EB-Z10005': self.epsn_1_212_Other,
            'EB-Z10000': self.epsn_1_212_Other,
            'EB-Z9900': self.epsn_1_212_Other,
            'EB-Z9810': self.epsn_1_212_Other,
            'EB-Z9800': self.epsn_1_212_Other,
            'EB-Z8250': self.epsn_1_212_Other,
            'EB-Z8150': self.epsn_1_212_Other,
            'EB-B1500': self.epsn_1_212_Other,
            'PowerLite Pro Z10000': self.epsn_1_212_Other,
            'PowerLite Pro Z10005': self.epsn_1_212_Other,
            'PowerLite Pro Z8150': self.epsn_1_212_Other,
            'PowerLite Pro Z8250': self.epsn_1_212_Other,
            'PowerLite Pro Z8350W': self.epsn_1_212_Other,
            'PowerLite Pro Z8355W': self.epsn_1_212_Other,
            'PowerLite Pro Z9750WU': self.epsn_1_212_Other,
            'PowerLite Pro Z9800': self.epsn_1_212_Other,
            'PowerLite Pro Z9805W': self.epsn_1_212_Other,
            'PowerLite Pro Z9810': self.epsn_1_212_Other,
            'PowerLite Pro Z9850W': self.epsn_1_212_Other,
            'PowerLite Pro Z9900': self.epsn_1_212_Other,
            'EB-Z8050W': self.epsn_1_212_Z8000,
            'PowerLite Pro Z8050W': self.epsn_1_212_Z8000,
            'EB-Z8000WU': self.epsn_1_212_Z8000,
            'PowerLite Pro Z8000WU': self.epsn_1_212_Z8000,
            'PowerLite Pro Z9750UNL': self.epsn_1_212_Z9750,
            'PowerLite Pro Z9870NL': self.epsn_1_212_Z9750,
            'PowerLite Pro Z11005NL': self.epsn_1_212_Z9750,
            'PowerLite Pro Z9800WNL': self.epsn_1_212_Z9750,
            'PowerLite Pro Z9900WNL': self.epsn_1_212_Z9750,
            'PowerLite Pro Z11000WNL': self.epsn_1_212_Z9750,
            'PowerLite Pro Z9870UNL': self.epsn_1_212_Z9750,
            'PowerLite Pro Z10000UNL': self.epsn_1_212_Z9750,
            'PowerLite Pro Z10005UNL': self.epsn_1_212_Z9750,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'SplitScreen': {'Status': {}},
            'SplitScreenLeftInput': {'Status': {}},
            'SplitScreenMode': {'Status': {}},
            'SplitScreenRightInput': {'Status': {}},
            'SplitScreenSwap': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'PWR=(0[0-5])\r'), self.__MatchPower, None)
            self.AddMatchString(compile(b'SOURCE=(10|11|14|30|31|33|34|35|45|42|40|53|60|64|65|A1|A3|A4|A5|A0|B0|B1|B4)\r'), self.__MatchInput, None)
            self.AddMatchString(compile(b'ASPECT=(00|10|20|21|22|30|40|50|60)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'MUTE=(ON|OFF)\r'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'CCAP=(00|11|12)\r'), self.__MatchClosedCaption, None)
            self.AddMatchString(compile(b'FREEZE=(ON|OFF)\r'), self.__MatchFreeze, None)
            self.AddMatchString(compile(b'LUMINANCE=(00|01|A0)\r'), self.__MatchLampMode, None)
            self.AddMatchString(compile(b'(ERR=([0-1][0-9A-F])\r)'), self.__MatchDeviceStatus, None)
            self.AddMatchString(compile(b'(ERR\r)'), self.__MatchError, None)
            self.AddMatchString(compile(b'LAMP=([0-9]{1,5}) ([0-9]{1,5})\r'), self.__MatchLampUsage, None)
            
    def SetAspectRatio(self, value, qualifier): 
        
        AspectRatioCmdString = 'ASPECT {0}\r'.format(self.AspectRatioStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):


        AspectRatioCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, qualifier):
        

        value = self.AspectRatioStateNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)
                
    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier, 3)

    def SetVideoMute(self, value, qualifier):
        VideoMuteStateValues = {
            'On' : 'ON',
            'Off' : 'OFF',
            }
        VideoMuteCmdString = 'MUTE {0}\r'.format(VideoMuteStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier, 3)

    def UpdateVideoMute(self, value, qualifier):
        
        VideoMuteCmdString = 'MUTE?\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, qualifier):
        VideoMuteStateNames = {
            'ON' : 'On',
            'OFF' : 'Off',
            }

        value = VideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)
                
    def SetClosedCaption(self, value, qualifier):
        ClosedCaptionStateValues = {
            'Off' : '00',
            'CC1' : '11',
            'CC2' : '12',
            }

        ClosedCaptionCmdString = 'CCAP {0}\r'.format(ClosedCaptionStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):
        
        ClosedCaptionCmdString = 'CCAP?\r'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, qualifier):
        ClosedCaptionStateNames = {
            '00' : 'Off',
            '11' : 'CC1',
            '12' : 'CC2'
            }

        value = ClosedCaptionStateNames[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)
                
    def UpdateDeviceStatus(self, value, qualifier):
        if 'Serial' in self.ConnectionType:
            DeviceStatusCmdString = 'ERR?\r'
            self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateDeviceStatus')
        

    def __MatchDeviceStatus(self, match, qualifier):
        DeviceStatusStateNames = {
            '00' : 'Normal',
            '01' : 'Fan Error',
            '03' : 'Lamp failure at power on',
            '04' : 'High internal temperature error',
            '06' : 'Lamp error',
            '07' : 'Open Lamp cover door error',
            '08' : 'Cinema filter error',
            '09' : 'Electric dual-layered capacitor is disconnected',
            '0A' : 'Auto iris error',
            '0B' : 'Subsystem Error',
            '0C' : 'Low air flow error',
            '0D' : 'Air filter air flow sensor error',
            '0E' : 'Power supply unit error (Ballast)',
            '0F' : 'Shutter error',
            '10' : 'Cooling system error (peltiert element)',
            '11' : 'Cooling system error (Pump)',
            '12' : 'Static iris error',
            '13' : 'Power supply unit error (Disagreement of Ballast)',
            '14' : 'Exhaust shutter error',
            '15' : 'Obstacle detection error',
            '16' : 'IF board discernment error'
            }

        try :
            value = DeviceStatusStateNames[match.group(2).decode()]
        except:
            value = 'Device in unknown error state'
            print('Device in unknown error state')  
        self.WriteStatus('DeviceStatus', value, qualifier)

    def SetFocus(self, value, qualifier):
        ValueStateValues = {
            'In Continously' : 'MIN', 
            'Out Continously' : 'MAX', 
            'Out Increment' : 'INC', 
            'In Increment' : 'DEC', 
            'Stop' : 'OFF'
        }

        FocusCmdString = 'FOCUS {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Focus', FocusCmdString, value, qualifier, 3)    


    def SetFreeze(self, value, qualifier):
        FreezeStateValues = {
            'On' : 'ON',
            'Off' : 'OFF',
            }

        FreezeCmdString = 'FREEZE {0}\r'.format(FreezeStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
       
        FreezeCmdString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, qualifier):
        FreezeStateNames = {
            'ON' : 'On',
            'OFF' : 'Off',
            }

        value = FreezeStateNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)
                
    def SetInput(self, value, qualifier):

        InputCmdString = 'SOURCE {0}\r'.format(self.InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, qualifier):

        value = self.InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)
                                        
    def SetLampMode(self, value, qualifier):
        LampModeStateValues = {
            'Normal' : '00',
            'Eco' : '01',
            'Auto' : 'A0'
            }

        LampModeCmdString = 'LUMINANCE {0}\r'.format(LampModeStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):
       
        LampModeCmdString = 'LUMINANCE?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, qualifier):
        LampModeStateNames = {
            '00' : 'Normal',
            '01' : 'Eco',
            'A0' : 'Auto'
            }

        value = LampModeStateNames[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)
                
    def UpdateLampUsage(self, value, qualifier):
        
        LampUsageCmdString = 'LAMP?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, qualifier):
        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value,{'Lamp':'1'})
        value = int(match.group(2).decode())
        self.WriteStatus('LampUsage', value, {'Lamp':'2'})
                
    def SetMenuNavigation(self, value, qualifier):
        MenuNavigationStateValues = {
            'Menu' : '03',
            'Up' : '35',
            'Down' : '36',
            'Left' : '37',
            'Right' : '38',
            'Enter' : '16',
            }

        MenuNavigationCmdString = 'KEY {0}\r'.format(MenuNavigationStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 3)

          
    def SetPower(self, value, qualifier): 
        PowerStateValues = {
            'On' : 'ON',
            'Off' : 'OFF'
            }

        PowerCmdString = 'PWR {0}\r'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 10)  

    def UpdatePower(self, value, qualifier):  
   
        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        PowerStateNames = {
            '01' : 'On',
            '00' : 'Off',
            '04' : 'Off',
            '05' : 'Abnormal Standby',
            '02' : 'Warmup',
            '03' : 'Cooldown',
            }
        

        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetZoom(self, value, qualifier):
        ValueStateValues = {
            'Tele Continously' : 'MIN', 
            'Wide Continously' : 'MAX', 
            'Wide Increment' : 'INC', 
            'Tele Increment' : 'DEC', 
            'Stop' : 'OFF'
        }

        ZoomCmdString = 'ZOOM {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier, 3)    


    def SetSplitScreen(self, value, qualifier):
        SplitScreenStateValues = {
            'On' : '01',
            'Off' : '00',
            }

        SplitScreenCmdString = 'SPS 01 {0}\r'.format(SplitScreenStateValues[value])
        self.__SetHelper('SplitScreen', SplitScreenCmdString, value, qualifier)

    def SetSplitScreenLeftInput(self, value, qualifier):
        SplitScreenLeftInputModeStateValues = {
            'Input 1 D-Sub' : '10',
            'Input 1 RGB' : '11',
            'Input 1 Component' : '14',
            'Input 3 HDMI ' : '30',
            'Input 3 D-RGB' : '31',
            'Input 3 RGB' : '33',
            'Input 3 YCbCr' : '34',
            'Input 3 YPbPr': '35',
            'Video' : '40',
            'S-Video' : '42',
            'BNC' : '45',
            'LAN': '53',
            'SDI-1' : '60',
            'SDI-2' : '64',
            'SDI-3' : '65',
            'HDMI' : 'A0',
            'Digital-RGB' : 'A1',
            'RGB Video' : 'A3',
            'YCbCr' : 'A4',
            'YPbPr' : 'A5',
            'Input 4 BNC' : 'B0',
            'Input 4 RGB' : 'B1',
            'Input 4 Component' : 'B4',
            }

        SplitScreenLeftInputCmdString = 'SPS 03 {0}\r'.format(SplitScreenLeftInputModeStateValues[value])
        self.__SetHelper('SplitScreenLeftInput', SplitScreenLeftInputCmdString, value, qualifier, 3)

    def SetSplitScreenMode(self, value, qualifier):
        SplitScreenModeStateValues = {
            'Size 1' : '00',
            'Size 2' : '01',
            'Size 3' : '02',
            }

        SplitScreenModeCmdString = 'SPS 02 {0}\r'.format(SplitScreenModeStateValues[value])
        self.__SetHelper('SplitScreenMode', SplitScreenModeCmdString, value, qualifier)

    def SetSplitScreenRightInput(self, value, qualifier):
        SplitScreenRightInputModeStateValues = {
            'Input 1 D-Sub' : '10',
            'Input 1 RGB' : '11',
            'Input 1 Component' : '14',
            'Input 3 HDMI ' : '30',
            'Input 3 D-RGB' : '31',
            'Input 3 RGB' : '33',
            'Input 3 YCbCr' : '34',
            'Input 3 YPbPr': '35',
            'Video' : '40',
            'S-Video' : '42',
            'BNC' : '45',
            'LAN': '53',
            'SDI-1' : '60',
            'SDI-2' : '64',
            'SDI-3' : '65',
            'HDMI' : 'A0',
            'Digital-RGB' : 'A1',
            'RGB Video' : 'A3',
            'YCbCr' : 'A4',
            'YPbPr' : 'A5',
            'Input 4 BNC' : 'B0',
            'Input 4 RGB' : 'B1',
            'Input 4 Component' : 'B4',

            }

        SplitScreenRightInputCmdString = 'SPS 04 {0}\r'.format(SplitScreenRightInputModeStateValues[value])
        self.__SetHelper('SplitScreenRightInput', SplitScreenRightInputCmdString, value, qualifier, 3)


    def SetSplitScreenSwap(self, value, qualifier):

        SplitScreenSwapCmdString = 'SPS 05\r'
        self.__SetHelper('SplitScreenSwap', SplitScreenSwapCmdString, value, qualifier)
   

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)            

    def __MatchError(self, match, tag):
        value = match.group(0).decode()
        print('An error occured')
        
    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        if 'Serial' not in self.ConnectionType:
            self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
    def epsn_1_212_Z8000(self):
        self.InputStateValues = {
            'Input 1 D-Sub' : '10',
            'Input 1 RGB' : '11',
            'Input 1 Component' : '14',
            'Input 3 DVI-D' : '30',
            'Input 3 D-RGB' : '31',
            'Input 3 RGB' : '33',
            'Video' : '40',
            'S-Video' : '42',
            'BNC' : '45',
            'LAN': '53',
            'HDMI' : 'A0',
            'Digital-RGB' : 'A1',
            'RGB Video' : 'A3',
            'YCbCr' : 'A4',
            'YPbPr' : 'A5',
            'Input 4 BNC' : 'B0',
            'Input 4 RGB' : 'B1',
            'Input 4 Component' : 'B4',         
            }

        self.InputStateNames = {
            '10' : 'Input 1 D-Sub',
            '11' : 'Input 1 RGB',
            '14' : 'Input 1 Component',
            '30' : 'Input 3 DVI-D ',
            '31' : 'Input 3 D-RGB',
            '33' : 'Input 3 RGB',
            '40' : 'Video',
            '42' : 'S-Video',
            '45' : 'BNC',
            '53' : 'LAN',
            '60' : 'SDI-1',
            '64' : 'SDI-2',
            '65' : 'SDI-3',
            'A0' : 'HDMI',
            'A1' : 'Digital-RGB',
            'A3' : 'RGB Video',
            'A4' : 'YCbCr',
            'A5' : 'YPbPr',
            'B0' : 'Input 4 BNC',
            'B1' : 'Input 4 RGB',
            'B4' : 'Input 4 Component'
            }

        self.AspectRatioStateValues = {
            'Normal': '00',
            '16:9' : '20',
            'Auto' : '30',
            'Full' : '40',
            'Zoom' : '50',
            'Native' : '60',
            }

        self.AspectRatioStateNames = {
            '00' : 'Normal',
            '20' : '16:9',
            '30' : 'Auto',
            '40' : 'Full',
            '50' : 'Zoom',
            '60' : 'Native'
            }

    def epsn_1_212_Other(self):
        self.InputStateValues = {
            'Input 1 D-Sub' : '10',
            'Input 1 RGB' : '11',
            'Input 1 Component' : '14',
            'Input 3 HDMI' : '30',
            'Input 3 D-RGB' : '31',
            'Input 3 RGB' : '33',
            'Input 3 YCbCr' : '34',
            'Input 3 YPbPr': '35',
            'Video' : '40',
            'S-Video' : '42',
            'BNC' : '45',
            'LAN': '53',
            'SDI-1' : '60',
            'SDI-2' : '64',
            'SDI-3' : '65',
            'HDMI' : 'A0',
            'Digital-RGB' : 'A1',
            'RGB Video' : 'A3',
            'YCbCr' : 'A4',
            'YPbPr' : 'A5',
            'Input 4 BNC' : 'B0',
            'Input 4 RGB' : 'B1',
            'Input 4 Component' : 'B4',      
            }

        self.InputStateNames = {
            '10' : 'Input 1 D-Sub',
            '11' : 'Input 1 RGB',
            '14' : 'Input 1 Component',
            '30' : 'Input 3 HDMI',
            '31' : 'Input 3 D-RGB',
            '33' : 'Input 3 RGB',
            '34' : 'Input 3 YCbCr',
            '35' : 'Input 3 YPbPr',
            '40' : 'Video',
            '42' : 'S-Video',
            '45' : 'BNC',
            '53' : 'LAN',
            '60' : 'SDI-1',
            '64' : 'SDI-2',
            '65' : 'SDI-3',
            'A0' : 'HDMI',
            'A1' : 'Digital-RGB',
            'A3' : 'RGB Video',
            'A4' : 'YCbCr',
            'A5' : 'YPbPr',
            'B0' : 'Input 4 BNC',
            'B1' : 'Input 4 RGB',
            'B4' :'Input 4 Component',
            }

        self.AspectRatioStateValues = {
            'Normal': '00',
            '4:3' : '10',
            '16:9' : '20',
            '16:9 Up' : '21',
            '16:9 Low' : '22',
            'Auto' : '30',
            'Full' : '40',
            'Zoom' : '50',
            'Real' : '60',
            }

        self.AspectRatioStateNames = {
            '00' : 'Normal',
            '10' : '4:3',
            '20' : '16:9',
            '21' : '16:9 Up', 
            '22' : '16:9 Low',
            '30' : 'Auto',
            '40' : 'Full',
            '50' : 'Zoom',
            '60' : 'Real'
            }

    def epsn_1_212_Z9750(self):
        self.InputStateValues = {
            'Input 1 D-Sub' : '10',
            'Input 1 RGB' : '11',
            'Input 1 Component' : '14',
            'Input 3 HDMI' : '30',
            'Input 3 D-RGB' : '31',
            'Input 3 RGB' : '33',
            'Input 3 YCbCr' : '34',
            'Input 3 YPbPr': '35',
            'Video' : '40',
            'S-Video' : '42',
            'BNC' : '45',
            'LAN': '53',
            'SDI-1' : '60',
            'SDI-2' : '64',
            'SDI-3' : '65',
            'HDMI' : 'A0',
            'Digital-RGB' : 'A1',
            'RGB Video' : 'A3',
            'YCbCr' : 'A4',
            'YPbPr' : 'A5',
            'Input 4 BNC' : 'B0',
            'Input 4 RGB' : 'B1',
            'Input 4 Component' : 'B4',      
            }

        self.InputStateNames = {
            '10' : 'Input 1 D-Sub',
            '11' : 'Input 1 RGB',
            '14' : 'Input 1 Component',
            '30' : 'Input 3 HDMI',
            '31' : 'Input 3 D-RGB',
            '33' : 'Input 3 RGB',
            '34' : 'Input 3 YCbCr',
            '35' : 'Input 3 YPbPr',
            '40' : 'Video',
            '42' : 'S-Video',
            '45' : 'BNC',
            '53' : 'LAN',
            '60' : 'SDI-1',
            '64' : 'SDI-2',
            '65' : 'SDI-3',
            'A0' : 'HDMI',
            'A1' : 'Digital-RGB',
            'A3' : 'RGB Video',
            'A4' : 'YCbCr',
            'A5' : 'YPbPr',
            'B0' : 'Input 4 BNC',
            'B1' : 'Input 4 RGB',
            'B4' :'Input 4 Component',
            }

        self.AspectRatioStateValues = {
            'Normal': '00',
            '4:3' : '10',
            '16:9' : '20',
            'Auto' : '30',
            'Full' : '40',
            'Zoom' : '50',
            'Native' : '60',
            }

        self.AspectRatioStateNames = {
            '00' : 'Normal',
            '10' : '4:3',
            '20' : '16:9',
            '30' : 'Auto',
            '40' : 'Full',
            '50' : 'Zoom',
            '60' : 'Native'
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
        #try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        #except AttributeError:
         #   print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
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
                result = search(regexString, self._ReceiveBuffer)                
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
