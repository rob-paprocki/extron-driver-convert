from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog
from struct import pack

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
        self.DeviceID = '1'



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3ScreenMode': {'Parameters':['Mode','Sound','Size','Main Picture Size','Sub 1 Source','Sub 1 Picture Size','Sub 2 Source','Sub 2 Picture Size'], 'Status': {}},
            '3ScreenModeStatus': { 'Status': {}},
            '3ScreenPictureSizeMainStatus': { 'Status': {}},
            '3ScreenPictureSizeSub1Status': { 'Status': {}},
            '3ScreenPictureSizeSub2Status': { 'Status': {}},
            '3ScreenSizeStatus': { 'Status': {}},
            '3ScreenSoundStatus': { 'Status': {}},
            '3ScreenSourceSub1Status': { 'Status': {}},
            '3ScreenSourceSub2Status': { 'Status': {}},
            '4ScreenMode': {'Parameters':['Mode','Sound','Size','Main Picture Size','Sub 1 Source','Sub 1 Picture Size','Sub 2 Source','Sub 2 Picture Size','Sub 3 Source','Sub 3 Picture Size'], 'Status': {}},
            '4ScreenModeStatus': { 'Status': {}},
            '4ScreenPictureSizeMainStatus': { 'Status': {}},
            '4ScreenPictureSizeSub1Status': { 'Status': {}},
            '4ScreenPictureSizeSub2Status': { 'Status': {}},
            '4ScreenPictureSizeSub3Status': { 'Status': {}},
            '4ScreenSizeStatus': { 'Status': {}},
            '4ScreenSoundStatus': { 'Status': {}},
            '4ScreenSourceSub1Status': { 'Status': {}},
            '4ScreenSourceSub2Status': { 'Status': {}},
            '4ScreenSourceSub3Status': { 'Status': {}},            
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'Mute': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoWall': { 'Status': {}},
            'VideoWallMode': { 'Status': {}},
            'VideoWallSize': {'Parameters': ['Row', 'Column'], 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.Last3ScreenModeUpdate = 0
        self.Last4ScreenModeUpdate = 0


        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x0A\x41\xB2(?P<mode>\x00|\x01)(?P<sound>[\x00-\x03])(?P<size>[\x00-\x05])(?P<mainsize>\x09|\x20)(?P<sub1source>[\x0C\x14\x18\x1F\x20-\x26\x30\x31\x33\x40])(?P<sub1size>\x09|\x20)(?P<sub2source>[\x0C\x14\x18\x1F\x20-\x26\x30\x31\x33\x40])(?P<sub2size>\x09|\x20)[\x00-\xFF]'), self.__Match3ScreenModeStatus, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x0C\x41\xB2(?P<mode>\x00|\x01)(?P<sound>[\x00-\x03])(?P<size>[\x00-\x05])(?P<mainsize>\x09|\x20)(?P<sub1source>[\x0C\x14\x18\x1F\x20-\x26\x30\x31\x33\x40])(?P<sub1size>\x09|\x20)(?P<sub2source>[\x0C\x14\x18\x1F\x20-\x26\x30\x31\x33\x40])(?P<sub2size>\x09|\x20)(?P<sub3source>[\x0C\x14\x18\x1F\x20-\x26\x30\x31\x33\x40])(?P<sub3size>\x09|\x20)[\x00-\xFF]'), self.__Match4ScreenModeStatus, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x18([\x01\x04\x0B\x31])[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5D([\x00\x01])[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x14([\x0C\x14\x18\x1F\x20-\x26\x30\x31\x33\x40])[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x13([\x00\x01])[\x00-\xFF]'), self.__MatchMute, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x3C([\x00\x01])[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x11([\x00\x01])[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x84([\x00\x01])[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\\x5C([\x00\x01])[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x04\x41\x89([\x00-\xFF])([\x00-\x64])[\x00-\xFF]'), self.__MatchVideoWallSize, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'\xAA\xFF[\x00-\xFF]\x03\x4E([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        tempDeviceID = value
        if tempDeviceID == 'Broadcast':
            self._DeviceID = 0xFE
        elif 0 <= int(tempDeviceID) <= 224:
            self._DeviceID = int(tempDeviceID)
        else:
            self.Error(['Device ID Out of Range'])

    def Set3ScreenMode(self, value, qualifier):

        
        ModeStates = {
            'On'  : 0x01, 
            'Off' : 0x00
        }

        mode = ModeStates[qualifier['Mode']]

        SoundStates = {
            'Main Screen'  : 0x00, 
            'Sub Screen 1' : 0x01, 
            'Sub Screen 2' : 0x02, 
            'Sub Screen 3' : 0x03
        }

        sound = SoundStates[qualifier['Sound']]

        SizeStates = {
            'Mode 1' 			: 0x00, 
            'Mode 2' 			: 0x01, 
            'Mode 3' 			: 0x02, 
            'Mode 4 (960:960)'  : 0x03, 
            'Mode 5 (1440:480)' : 0x04, 
            'Mode 6 (1280:640)' : 0x05
        }

        size = SizeStates[qualifier['Size']]

        MainPictureSizeStates = {
            'Full (Screen Fit)'       : 0x09, 
            'Original (Aspect Ratio)' : 0x20
        }

        mainsize = MainPictureSizeStates[qualifier['Main Picture Size']]

        SourceStates = {
            'PC':            0x14,
            'DVI':           0x18,
            'MagicInfo':     0x20,
            'RF(TV)':        0x30,
            'DTV':           0x40,
            'HDMI 1':        0x21,
            'HDMI 2':        0x23,
            'DisplayPort 1': 0x25,
            'Input Source':  0x0C,
            'HDMI 3':        0x31,
            'HDMI 4':        0x33,
            'DisplayPort 2': 0x26,
        }

        sub1source = SourceStates[qualifier['Sub 1 Source']]
        sub2source = SourceStates[qualifier['Sub 2 Source']]

        Sub1PictureSizeStates = {
            'Full (Screen Fit)'       : 0x09, 
            'Original (Aspect Ratio)' : 0x20
        }

        sub1size = Sub1PictureSizeStates[qualifier['Sub 1 Picture Size']]

        Sub2PictureSizeStates = {
            'Full (Screen Fit)'       : 0x09, 
            'Original (Aspect Ratio)' : 0x20
        }
        
        sub2size = Sub2PictureSizeStates[qualifier['Sub 2 Picture Size']]

        cks = (0xB2 + self.DeviceID + 0x08 + mode + sound + size + mainsize + sub1source + sub1size + sub2source + sub2size) & 0xFF
        ScreenModeCmdString = pack('13B', 0xAA, 0xB2, self.DeviceID, 0x08, mode, sound, size, mainsize, sub1source, sub1size, sub2source, sub2size, cks)
        self.__SetHelper('3ScreenMode', ScreenModeCmdString, value, qualifier)
    def Update3ScreenModeStatus(self, value, qualifier):
    
        cks = (0xB2 + self.DeviceID) & 0xFF
        ScreenModeStatusCmdString = pack('5B', 0xAA, 0xB2, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('3ScreenModeStatus', ScreenModeStatusCmdString, value, qualifier)


    def __Match3ScreenModeStatus(self, match, tag):

        
        ModeStateValues = {
            '\x01' : 'On', 
            '\x00' : 'Off'
        }

        PictureSizeStateValues = {
            '\x09' : 'Full (Screen Fit)', 
            '\x20' : 'Original (Aspect Ratio)'
        }

        SizeStateValues = {
            '\x00' : 'Mode 1', 
            '\x01' : 'Mode 2', 
            '\x02' : 'Mode 3', 
            '\x03' : 'Mode 4 (960:960)', 
            '\x04' : 'Mode 5 (1440:480)', 
            '\x05' : 'Mode 6 (1280:640)'
        }

        SoundStateValues = {
            '\x00' : 'Main Screen', 
            '\x01' : 'Sub Screen 1', 
            '\x02' : 'Sub Screen 2', 
            '\x03' : 'Sub Screen 3'
        }

        SourceStateValues = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x20': 'MagicInfo',
            '\x1F': 'DVI Video',
            '\x30': 'RF(TV)',
            '\x40': 'DTV',
            '\x21': 'HDMI 1',
            '\x22': 'HDMI 1 PC',
            '\x23': 'HDMI 2',
            '\x24': 'HDMI 2 PC',
            '\x25': 'DisplayPort 1',
            '\x0C': 'Input Source',
            '\x31': 'HDMI 3',
            '\x33': 'HDMI 4',
            '\x26': 'DisplayPort 2',
        }
 
        mode = ModeStateValues[match.group('mode').decode()]
        self.WriteStatus('3ScreenModeStatus', mode, None)

        sound = SoundStateValues[match.group('sound').decode()]
        self.WriteStatus('3ScreenSoundStatus', sound, None)

        size = SizeStateValues[match.group('size').decode()]
        self.WriteStatus('3ScreenSizeStatus', size, None)

        mainsize = PictureSizeStateValues[match.group('mainsize').decode()]
        self.WriteStatus('3ScreenPictureSizeMainStatus', mainsize, None)

        sub1source = SourceStateValues[match.group('sub1source').decode()]
        self.WriteStatus('3ScreenSourceSub1Status', sub1source, None)

        sub1size = PictureSizeStateValues[match.group('sub1size').decode()]
        self.WriteStatus('3ScreenPictureSizeSub1Status', sub1size, None)

        sub2source = SourceStateValues[match.group('sub2source').decode()]
        self.WriteStatus('3ScreenSourceSub2Status', sub2source, None)

        sub2size = PictureSizeStateValues[match.group('sub2size').decode()]
        self.WriteStatus('3ScreenPictureSizeSub2Status', sub2size, None)

    def Update3ScreenPictureSizeMainStatus(self, value, qualifier):

        
        self.Update3ScreenModeStatus(value, None)

    def Update3ScreenPictureSizeSub1Status(self, value, qualifier):

        
        self.Update3ScreenModeStatus(value, None)

    def Update3ScreenPictureSizeSub2Status(self, value, qualifier):

        
        self.Update3ScreenModeStatus(value, None)

    def Update3ScreenSizeStatus(self, value, qualifier):

        
        self.Update3ScreenModeStatus(value, None)

    def Update3ScreenSoundStatus(self, value, qualifier):

        
        self.Update3ScreenModeStatus(value, None)

    def Update3ScreenSourceSub1Status(self, value, qualifier):

        
        self.Update3ScreenModeStatus(value, None)

    def Update3ScreenSourceSub2Status(self, value, qualifier):

        
        self.Update3ScreenModeStatus(value, None)

    def Set4ScreenMode(self, value, qualifier):

        
        ModeStates = {
            'On'  : 0x01, 
            'Off' : 0x00
        }

        mode = ModeStates[qualifier['Mode']]

        SoundStates = {
            'Main Screen'  : 0x00, 
            'Sub Screen 1' : 0x01, 
            'Sub Screen 2' : 0x02, 
            'Sub Screen 3' : 0x03
        }

        sound = SoundStates[qualifier['Sound']]

        SizeStates = {
            'Mode 1' 			: 0x00, 
            'Mode 2' 			: 0x01, 
            'Mode 3' 			: 0x02, 
            'Mode 4 (960:960)'  : 0x03, 
            'Mode 5 (1440:480)' : 0x04, 
            'Mode 6 (1280:640)' : 0x05
        }

        size = SizeStates[qualifier['Size']]

        MainPictureSizeStates = {
            'Full (Screen Fit)'       : 0x09, 
            'Original (Aspect Ratio)' : 0x20
        }

        mainsize = MainPictureSizeStates[qualifier['Main Picture Size']]

        SourceStates = {
            'PC':            0x14,
            'DVI':           0x18,
            'MagicInfo':     0x20,
            'RF(TV)':        0x30,
            'DTV':           0x40,
            'HDMI 1':        0x21,
            'HDMI 2':        0x23,
            'DisplayPort 1': 0x25,
            'Input Source':  0x0C,
            'HDMI 3':        0x31,
            'HDMI 4':        0x33,
            'DisplayPort 2': 0x26,
        }

        sub1source = SourceStates[qualifier['Sub 1 Source']]
        sub2source = SourceStates[qualifier['Sub 2 Source']]
        sub3source = SourceStates[qualifier['Sub 3 Source']]

        Sub1PictureSizeStates = {
            'Full (Screen Fit)'       : 0x09, 
            'Original (Aspect Ratio)' : 0x20
        }

        sub1size = Sub1PictureSizeStates[qualifier['Sub 1 Picture Size']]       

        Sub2PictureSizeStates = {
            'Full (Screen Fit)'       : 0x09, 
            'Original (Aspect Ratio)' : 0x20
        }
        
        sub2size = Sub2PictureSizeStates[qualifier['Sub 2 Picture Size']]

        Sub3PictureSizeStates = {
            'Full (Screen Fit)'       : 0x09, 
            'Original (Aspect Ratio)' : 0x20
        }
        
        sub3size = Sub3PictureSizeStates[qualifier['Sub 3 Picture Size']]

        cks = (0xB2 + self.DeviceID + 0x0A + mode + sound + size + mainsize + sub1source + sub1size + sub2source + sub2size + sub3source + sub3size) & 0xFF
        ScreenModeCmdString = pack('15B', 0xAA, 0xB2, self.DeviceID, 0x0A, mode, sound, size, mainsize, sub1source, sub1size, sub2source, sub2size, sub3source, sub3size, cks)
        
        self.__SetHelper('4ScreenMode', ScreenModeCmdString, value, qualifier)
    def Update4ScreenModeStatus(self, value, qualifier):

        
        cks = (0xB2 + self.DeviceID) & 0xFF
        ScreenModeStatusCmdString = pack('5B', 0xAA, 0xB2, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('4ScreenModeStatus', ScreenModeStatusCmdString, value, qualifier)

    def __Match4ScreenModeStatus(self, match, tag):

        
        ModeStateValues = {
            '\x01' : 'On', 
            '\x00' : 'Off'
        }

        PictureSizeStateValues = {
            '\x09' : 'Full (Screen Fit)', 
            '\x20' : 'Original (Aspect Ratio)'
        }

        SizeStateValues = {
            '\x00' : 'Mode 1', 
            '\x01' : 'Mode 2', 
            '\x02' : 'Mode 3', 
            '\x03' : 'Mode 4 (960:960)', 
            '\x04' : 'Mode 5 (1440:480)', 
            '\x05' : 'Mode 6 (1280:640)'
        }

        SoundStateValues = {
            '\x00' : 'Main Screen', 
            '\x01' : 'Sub Screen 1', 
            '\x02' : 'Sub Screen 2', 
            '\x03' : 'Sub Screen 3'
        }

        SourceStateValues = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x20': 'MagicInfo',
            '\x1F': 'DVI Video',
            '\x30': 'RF(TV)',
            '\x40': 'DTV',
            '\x21': 'HDMI 1',
            '\x22': 'HDMI 1 PC',
            '\x23': 'HDMI 2',
            '\x24': 'HDMI 2 PC',
            '\x25': 'DisplayPort 1',
            '\x0C': 'Input Source',
            '\x31': 'HDMI 3',
            '\x33': 'HDMI 4',
            '\x26': 'DisplayPort 2',
        }
 
        mode = ModeStateValues[match.group('mode').decode()]
        self.WriteStatus('4ScreenModeStatus', mode, None)

        sound = SoundStateValues[match.group('sound').decode()]
        self.WriteStatus('4ScreenSoundStatus', sound, None)

        size = SizeStateValues[match.group('size').decode()]
        self.WriteStatus('4ScreenSizeStatus', size, None)

        mainsize = PictureSizeStateValues[match.group('mainsize').decode()]
        self.WriteStatus('4ScreenPictureSizeMainStatus', mainsize, None)

        sub1source = SourceStateValues[match.group('sub1source').decode()]
        self.WriteStatus('4ScreenSourceSub1Status', sub1source, None)

        sub1size = PictureSizeStateValues[match.group('sub1size').decode()]
        self.WriteStatus('4ScreenPictureSizeSub1Status', sub1size, None)

        sub2source = SourceStateValues[match.group('sub2source').decode()]
        self.WriteStatus('4ScreenSourceSub2Status', sub2source, None)

        sub2size = PictureSizeStateValues[match.group('sub2size').decode()]
        self.WriteStatus('4ScreenPictureSizeSub2Status', sub2size, None)

        sub3source = SourceStateValues[match.group('sub3source').decode()]
        self.WriteStatus('4ScreenSourceSub3Status', sub3source, None)

        sub3size = PictureSizeStateValues[match.group('sub3size').decode()]
        self.WriteStatus('4ScreenPictureSizeSub3Status', sub3size, None)

    def Update4ScreenPictureSizeMainStatus(self, value, qualifier):

        
        self.Update4ScreenModeStatus(value, None)

    def Update4ScreenPictureSizeSub1Status(self, value, qualifier):

        
        self.Update4ScreenModeStatus(value, None)

    def Update4ScreenPictureSizeSub2Status(self, value, qualifier):

        
        self.Update4ScreenModeStatus(value, None)

    def Update4ScreenPictureSizeSub3Status(self, value, qualifier):

        
        self.Update4ScreenModeStatus(value, None)

    def Update4ScreenSizeStatus(self, value, qualifier):

        
        self.Update4ScreenModeStatus(value, None)

    def Update4ScreenSoundStatus(self, value, qualifier):

        
        self.Update4ScreenModeStatus(value, None)

    def Update4ScreenSourceSub1Status(self, value, qualifier):

        
        self.Update4ScreenModeStatus(value, None)

    def Update4ScreenSourceSub2Status(self, value, qualifier):

        
        self.Update4ScreenModeStatus(value, None)

    def Update4ScreenSourceSub3Status(self, value, qualifier):

        
        self.Update4ScreenModeStatus(value, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9':      0x01,
            'Zoom':      0x04,
            'Wide Zoom': 0x31,
            '4:3':       0x0B,
        }

        cks = (0x18 + self.DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        AspectRatioCmdString = pack('6B', 0xAA, 0x18, self.DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        cks = (0x18 + self.DeviceID) & 0xFF
        AspectRatioCmdString = pack('5B', 0xAA, 0x18, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x01': '16:9',
            '\x04': 'Zoom',
            '\x31': 'Wide Zoom',
            '\x0B': '4:3',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        cks = (0x3D + self.DeviceID + 0x01) & 0xFF
        AutoImageCmdString = pack('6B', 0xAA, 0x3D, self.DeviceID, 0x01, 0x00, cks)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00,
        }

        cks = (0x5D + self.DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        ExecutiveModeCmdString = pack('6B', 0xAA, 0x5D, self.DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        cks = (0x5D + self.DeviceID) & 0xFF
        ExecutiveModeCmdString = pack('5B', 0xAA, 0x5D, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'PC':            0x14,
            'DVI':           0x18,
            'MagicInfo':     0x20,
            'RF(TV)':        0x30,
            'DTV':           0x40,
            'HDMI 1':        0x21,
            'HDMI 2':        0x23,
            'DisplayPort 1': 0x25,
            'Input Source':  0x0C,
            'HDMI 3':        0x31,
            'HDMI 4':        0x33,
            'DisplayPort 2': 0x26,
        }

        cks = (0x14 + self.DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        InputCmdString = pack('6B', 0xAA, 0x14, self.DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        cks = (0x14 + self.DeviceID) & 0xFF
        InputCmdString = pack('>5B', 0xAA, 0x14, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x14': 'PC',
            '\x18': 'DVI',
            '\x20': 'MagicInfo',
            '\x1F': 'DVI Video',
            '\x30': 'RF(TV)',
            '\x40': 'DTV',
            '\x21': 'HDMI 1',
            '\x22': 'HDMI 1 PC',
            '\x23': 'HDMI 2',
            '\x24': 'HDMI 2 PC',
            '\x25': 'DisplayPort 1',
            '\x0C': 'Input Source',
            '\x31': 'HDMI 3',
            '\x33': 'HDMI 4',
            '\x26': 'DisplayPort 2',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x01,
            'Off' : 0x00
        }

        cks = (0x13 + self.DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        MuteCmdString = pack('6B', 0xAA, 0x13, self.DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        cks = (0x13 + self.DeviceID) & 0xFF
        MuteCmdString = pack('5B', 0xAA, 0x13, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00
        }

        cks = (0x3C + self.DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        PIPModeCmdString = pack('6B', 0xAA, 0x3C, self.DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        cks = (0x3C + self.DeviceID) & 0xFF
        PIPModeCmdString = pack('5B', 0xAA, 0x3C, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00,
        }

        cks = (0x11 + self.DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        PowerCmdString = pack('6B', 0xAA, 0x11, self.DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        cks = (0x11 + self.DeviceID) & 0xFF
        PowerCmdString = pack('5B', 0xAA, 0x11, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off',
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00,
        }

        cks = (0x84 + self.DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        VideoWallCmdString = pack('6B', 0xAA, 0x84, self.DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        cks = (0x84 + self.DeviceID) & 0xFF
        VideoWallCmdString = pack('5B', 0xAA, 0x84, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoWall', value, None)

    def SetVideoWallMode(self, value, qualifier):

        ValueStateValues = {
            'Full':    0x01,
            'Natural': 0x00,
        }

        cks = (0x5C + self.DeviceID + 0x01 + ValueStateValues[value]) & 0xFF
        VideoWallModeCmdString = pack('6B', 0xAA, 0x5C, self.DeviceID, 0x01, ValueStateValues[value], cks)
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        cks = (0x5C + self.DeviceID) & 0xFF
        VideoWallModeCmdString = pack('5B', 0xAA, 0x5C, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'Full',
            '\x00': 'Natural',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoWallMode', value, None)

    def SetVideoWallSize(self, value, qualifier):

        rowState = {
            '1':  0x10,
            '2':  0x20,
            '3':  0x30,
            '4':  0x40,
            '5':  0x50,
            '6':  0x60,
            '7':  0x70,
            '8':  0x80,
            '9':  0x90,
            '10': 0xA0,
            '11': 0xB0,
            '12': 0xC0,
            '13': 0xD0,
            '14': 0xE0,
            '15': 0xF0,
        }

        row_temp = int(qualifier['Row'])
        column = int(qualifier['Column'])
        display_num = int(value)

        if 0 < column <= 15 and 0 < row_temp <= 15:
            if 0 < display_num <= 100:
                row = rowState[qualifier['Row']]
                size = row + column
                if row <= 0x60 and column <= 15 and display_num <= 90:      # 6x15 display: 1 - 90
                    valid_value = True
                elif row <= 0x70 and column < 15 and display_num <= 98:     # 7x14 display: 1 - 98
                    valid_value = True
                elif row <= 0x80 and column < 13 and display_num <= 96:     # 8x12 display: 1 - 96
                    valid_value = True
                elif row <= 0x90 and column < 12 and display_num <= 99:     # 9x11 display: 1 - 99
                    valid_value = True
                elif row <= 0xA0 and column < 11:                           # 10x10 display: 1 - 100
                    valid_value = True
                elif row <= 0xB0 and column < 10 and display_num <= 99:     # 11x9 display: 1 - 99
                    valid_value = True
                elif row <= 0xC0 and column < 9 and display_num <= 96:      # 12x8 display: 1 - 96
                    valid_value = True
                elif row <= 0xD0 and column < 8 and display_num <= 91:      # 13x7 display: 1 - 91
                    valid_value = True
                elif row <= 0xE0 and column < 8 and display_num <= 98:      # 14x7 display: 1 - 98
                    valid_value = True
                elif row <= 0xF0 and column < 7 and display_num <= 90:      # 15x6 display: 1 - 90
                    valid_value = True
                else:
                    valid_value = False  # All qualifiers configured wrong
                if valid_value:
                    cks = int(hex(0x89 + self.DeviceID + 0x02 + size + display_num)[-2:], 16)
                    VideoWallSizeCmdString = pack('7B', 0xAA, 0x89, self.DeviceID, 0x02, size, display_num, cks)
                    self.__SetHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetVideoWallSize')
            else:
                self.Discard('Invalid Command for SetVideoWallSize')
        else:
            self.Discard('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):

        cks = int(hex(0x89 + self.DeviceID)[-2:], 16)
        VideoWallSizeCmdString = pack('5B', 0xAA, 0x89, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('VideoWallSize', VideoWallSizeCmdString, value, qualifier)

    def __MatchVideoWallSize(self, match, tag):

        value = str(ord(match.group(2).decode()))  # value
        value2 = ord(match.group(1).decode(encoding='iso-8859-1'))  # size
        value3 = None
        row = None
        if value2 < 0x20:  # row  1
            row = '1'
            value3 = value2 - 0x10
        elif value2 < 0x30:  # row  2
            row = '2'
            value3 = value2 - 0x20
        elif value2 < 0x40:  # row  3
            row = '3'
            value3 = value2 - 0x30
        elif value2 < 0x50:  # row  4
            row = '4'
            value3 = value2 - 0x40
        elif value2 < 0x60:  # row  5
            row = '5'
            value3 = value2 - 0x50
        elif value2 < 0x70:  # row  6
            row = '6'
            value3 = value2 - 0x60
        elif value2 < 0x80:  # row  7
            row = '7'
            value3 = value2 - 0x70
        elif value2 < 0x90:  # row  8
            row = '8'
            value3 = value2 - 0x80
        elif value2 < 0xA0:  # row  9
            row = '9'
            value3 = value2 - 0x90
        elif value2 < 0xB0:  # row  10
            row = '10'
            value3 = value2 - 0xA0
        elif value2 < 0xC0:  # row  11
            row = '11'
            value3 = value2 - 0xB0
        elif value2 < 0xD0:  # row  12
            row = '12'
            value3 = value2 - 0xC0
        elif value2 < 0xE0:  # row  13
            row = '13'
            value3 = value2 - 0xD0
        elif value2 < 0xF0:  # row  14
            row = '14'
            value3 = value2 - 0xE0
        elif value2 < 0xF7:  # row  15
            row = '15'
            value3 = value2 - 0xF0

        if value3 and row:
            qualifier = {'Column': str(value3), 'Row': row}
            self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            cks = (0x12 + self.DeviceID + 0x01 + value) & 0xFF
            VolumeCmdString = pack('6B', 0xAA, 0x12, self.DeviceID, 0x01, value, cks)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        cks = (0x12 + self.DeviceID) & 0xFF
        VolumeCmdString = pack('5B', 0xAA, 0x12, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == 0xFE:  # Broadcast
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

        DEVICE_ERROR_CODES = {
            b'\x18': 'Aspect Ratio',
            b'\x5D': 'Executive Mode',
            b'\x14': 'Input',
            b'\x13': 'Mute',
            b'\x3C': 'PIP Mode',
            b'\x11': 'Power',
            b'\x84': 'Video Wall',
            b'\x5C': 'Video Wall Mode',
            b'\x89': 'Video Wall Size',
            b'\x12': 'Volume'
        }

        if match.group(1) in DEVICE_ERROR_CODES:
            self.Error(['Error with Command: {0} and Error code is {1}.'.format(DEVICE_ERROR_CODES[match.group(1)], match.group(2))])
        else:
            self.Error(['Error with Unknown Command and Error code is {0}.'.format(match.group(2))])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Last3ScreenModeUpdate = 0
        self.Last4ScreenModeUpdate = 0
                ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
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

