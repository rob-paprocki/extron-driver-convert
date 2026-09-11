from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.Commands =              {
            'AudioMicrophoneSelect': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AudioVolume': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'ColorMode': { 'Status': {}},
            'Detail': { 'Status': {}},
            'EraseMemory': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'Iris': {'Parameters':['Speed'], 'Status': {}},
            'Keylock': { 'Status': {}},
            'LaserMarkerPortable': { 'Status': {}},
            'MainResolution': { 'Status': {}},
            'MemoryRecall': { 'Status': {}},
            'MemorySave': { 'Status': {}},
            'MenuControl': { 'Status': {}},
            'MenuOnOff': { 'Status': {}},
            'PIP': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PosNegBlue': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetStore': { 'Status': {}},
            'Snapshot': { 'Status': {}},
            'Source': { 'Status': {}},
            'StreamingMode': { 'Status': {}},
            'VideoPlayback': {'Parameters':['Speed'], 'Status': {}},
            'VideoRecording': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
            }   
        
        self.SetHelper = re.compile(b'([\x09|\x01][\x00-\xFF][\x00-\x03][\x00]{0,1})')
        self.UpdateHelper = re.compile(b'([\x00|\x08][\x00-\xFF][\x00-\x05]{2,3}[\x00-\xFF]{0,2})')    
        
    def SetAudioMicrophoneSelect(self, value, qualifier):

        ValueStateValues = {
            'Off' :     b'\x09\x04\x01\x01\x00', 
            'Line-In' : b'\x09\x04\x01\x01\x02'
        }

        AudioMicrophoneSelectCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMicrophoneSelect', AudioMicrophoneSelectCmdString, value, qualifier)

    def UpdateAudioMicrophoneSelect(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Off', 
            b'\x02' : 'Line-In'
        }

        AudioMicrophoneSelectCmdString = b'\x08\x04\x01\x00'
        res = self.__UpdateHelper('AudioMicrophoneSelect', AudioMicrophoneSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('AudioMicrophoneSelect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On' :  b'\x09\x04\x02\x01\x01', 
            'Off' : b'\x09\x04\x02\x01\x00'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        AudioMuteCmdString = b'\x08\x04\x02\x00'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAudioVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioVolumeCmdString = pack('>BBBBBB',0x09,0x04,0x03,0x02,0x00,int(value))
            self.__SetHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def UpdateAudioVolume(self, value, qualifier):

        AudioVolumeCmdString = b'\x08\x04\x03\x00'
        res = self.__UpdateHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5])
                self.WriteStatus('AudioVolume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        AutoFocusStateValues = {
            'On' :  b'\x01\x31\x01\x01',
            'Off' : b'\x01\x31\x01\x00',
            }

        AutoFocusCmdString = AutoFocusStateValues[value]
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusStateNames = {
            b'\x01' : 'On',
            b'\x00' : 'Off',
           }

        AutoFocusCmdString = b'\x00\x31\x00'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = AutoFocusStateNames[res[3:4]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetColorMode(self, value, qualifier):

        ValueStateValues = {
            'Black/White' :      b'\x01\x6D\x01\x00', 
            'Presentation' :     b'\x01\x6D\x01\x01', 
            'Natural' :          b'\x01\x6D\x01\x02', 
            'Video Conference' : b'\x01\x6D\x01\x03', 
            'Manual' :           b'\x01\x6D\x01\x04'
        }

        ColorModeCmdString = ValueStateValues[value]
        self.__SetHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def UpdateColorMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Black/White', 
            b'\x01' : 'Presentation', 
            b'\x02' : 'Natural', 
            b'\x03' : 'Video Conference', 
            b'\x04' : 'Manual'
        }

        ColorModeCmdString = b'\x00\x6D\x00'
        res = self.__UpdateHelper('ColorMode', ColorModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('ColorMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'Off' :    b'\x01\x53\x01\x00', 
            'Medium' : b'\x01\x53\x01\x02', 
            'High' :   b'\x01\x53\x01\x03'
        }

        DetailCmdString = ValueStateValues[value]
        self.__SetHelper('Detail', DetailCmdString, value, qualifier)

    def UpdateDetail(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Off', 
            b'\x02' : 'Medium', 
            b'\x03' : 'High'
        }

        DetailCmdString = b'\x00\x53\x00'
        res = self.__UpdateHelper('Detail', DetailCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Detail', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetEraseMemory(self, value, qualifier):

        EraseMemoryCmdString = b'\x01\x92\x01\x20'
        self.__SetHelper('EraseMemory', EraseMemoryCmdString, value, qualifier)
    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far' :  0x01, 
            'Near' : 0x02
        }
        focusspeed = int(qualifier['Speed'])
        if 1 <= focusspeed <= 15:
            if value == 'Stop':
                FocusCmdString = pack('>BBBBBB',0x01,0x21,0x03,0x00,0x00,0x00)
            else:
                FocusCmdString = pack('>BBBBBB',0x01,0x21,0x03,ValueStateValues[value],0x00,focusspeed)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')
    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On' :  b'\x01\x56\x01\x01',
            'Off' : b'\x01\x56\x01\x00',
            }

        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeStateNames = {
            b'\x01' : 'On',
            b'\x00' : 'Off',
           }

        FreezeCmdString = b'\x00\x56\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeStateNames[res[3:4]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Open' :  0x01, 
            'Close' : 0x02 
        }

        Irisspeed = qualifier['Speed'] 
        if Irisspeed == 'Normal' or Irisspeed == 'Fast':
                if value == 'Stop':
                    IrisCmdString = pack('>BBBB',0x01,0x2F,0x01,0x00)
                    self.__SetHelper('Iris', IrisCmdString, value, qualifier,3)
                else:
                    if Irisspeed is 'Normal':
                        IrisCmdString = pack('>BBBBBB', 0x01,0x22,0x03,ValueStateValues[value],0x00,0x01)
                    elif Irisspeed is 'Fast':
                        IrisCmdString = pack('>BBBBBB', 0x01,0x22,0x03,ValueStateValues[value],0x00,0x02)
                    self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')
    def SetKeylock(self, value, qualifier):

        KeylockStateValues = {
            'On'  : b'\x01\x80\x01\x01',
            'Off' : b'\x01\x80\x01\x00',
            }

        KeylockCmdString = KeylockStateValues[value]
        self.__SetHelper('Keylock', KeylockCmdString, value, qualifier)

    def UpdateKeylock(self, value, qualifier):

        KeylockStateNames = {
            b'\x01' : 'On',
            b'\x00' : 'Off',
           }

        KeylockCmdString = b'\x00\x80\x00'
        res = self.__UpdateHelper('Keylock', KeylockCmdString, value, qualifier)
        if res:
            try:
                value = KeylockStateNames[res[3:4]]
                self.WriteStatus('Keylock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetLaserMarkerPortable(self, value, qualifier):

        ValueStateValues = {
            'On'     : b'\x01\xA7\x01\x01', 
            'Off'    : b'\x01\xA7\x01\x00', 
            'Adjust' : b'\x01\xA7\x01\x03'
        }

        LaserMarkerPortableCmdString = ValueStateValues[value]
        self.__SetHelper('LaserMarkerPortable', LaserMarkerPortableCmdString, value, qualifier)

    def UpdateLaserMarkerPortable(self, value, qualifier):

        ValueStateValues = {
             b'\x01' : 'On', 
             b'\x00' : 'Off', 
             b'\x03' : 'Adjust'
        }

        LaserMarkerPortableCmdString = b'\x00\xA7\x00'
        res = self.__UpdateHelper('LaserMarkerPortable', LaserMarkerPortableCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('LaserMarkerPortable', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetMainResolution(self, value, qualifier):

        ValueStateValues = {
            'Auto' :     b'\x01\x51\x04\x00\x00\x00\x00', 
            'SVGA/60' :  b'\x01\x51\x04\x00\x00\x3C\x01', 
            'XGA/60' :   b'\x01\x51\x04\x00\x00\x3C\x04', 
            'SXGA/60' :  b'\x01\x51\x04\x00\x00\x3C\x0A', 
            'UXGA/60' :  b'\x01\x51\x04\x00\x00\x3C\x0D', 
            '720p/60' :  b'\x01\x51\x04\x00\x00\x3C\x16', 
            '1080p/30' : b'\x01\x51\x04\x00\x00\x1E\x18', 
            '1080p/60' : b'\x01\x51\x04\x00\x00\x3C\x18', 
            'WUXGA/60' : b'\x01\x51\x04\x00\x00\x3C\x1C', 
            'WXGA*/60' : b'\x01\x51\x04\x00\x00\x3C\x1E'
        }
        
        MainResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('MainResolution', MainResolutionCmdString, value, qualifier)

    def UpdateMainResolution(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00' : 'Auto', 
            b'\x3C\x01' : 'SVGA/60', 
            b'\x3C\x04' : 'XGA/60', 
            b'\x3C\x0A' : 'SXGA/60', 
            b'\x3C\x0D' : 'UXGA/60', 
            b'\x3C\x16' : '720p/60', 
            b'\x1E\x18' : '1080p/30', 
            b'\x3C\x18' : '1080p/60', 
            b'\x3C\x1C' : 'WUXGA/60', 
            b'\x3C\x1E' : 'WXGA*/60'
        }

        MainResolutionCmdString = b'\x00\x51\x00'
        res = self.__UpdateHelper('MainResolution', MainResolutionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:7]]
                self.WriteStatus('MainResolution', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetMemoryRecall(self, value, qualifier):

        if 1 <= int(value) <= 9:
            MemoryRecallCmdString = pack('>BBBB',0x01,0x91,0x01,int(value))
            self.__SetHelper('MemoryRecall', MemoryRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMemoryRecall')
    def SetMemorySave(self, value, qualifier):

        if 1 <= int(value) <= 9:
            MemorySaveCmdString = pack('>BBBB',0x01,0x92,0x01,int(value))
            self.__SetHelper('MemorySave', MemorySaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMemorySave')
    def SetMenuControl(self, value, qualifier):

        ValueStateValues = {
            'Up' :    b'\x01\x99\x01\x02', 
            'Down' :  b'\x01\x99\x01\x08', 
            'Left' :  b'\x01\x99\x01\x04', 
            'Right' : b'\x01\x99\x01\x06', 
            'Enter' : b'\x01\x99\x01\x05', 
            'Help' :  b'\x01\x99\x01\x10', 
            'Reset' : b'\x01\x99\x01\x90'
        }

        MenuControlCmdString = ValueStateValues[value]
        self.__SetHelper('MenuControl', MenuControlCmdString, value, qualifier)
    def SetMenuOnOff(self, value, qualifier):

        ValueStateValues = {
            'Menu Off' :         b'\x01\x98\x01\x00', 
            'Standard Menu On' : b'\x01\x98\x01\x03', 
            'Extra Menu On' :    b'\x01\x98\x01\x04', 
            'Memory Menu On' :   b'\x01\x98\x01\x05', 
            'USB Menu On' :      b'\x01\x98\x01\x06'
        }

        MenuOnOffCmdString = ValueStateValues[value]
        if value != 'Memory Menu On' or value != 'USB Menu On':
            self.__SetHelper('MenuOnOff', MenuOnOffCmdString, value, qualifier)

    def UpdateMenuOnOff(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Menu Off', 
            b'\x01' : 'Standard Menu On', 
            b'\x02' : 'Extra Menu On', 
            b'\x03' : 'View Menu'
        }

        MenuOnOffCmdString = b'\x00\x98\x00'
        res = self.__UpdateHelper('MenuOnOff', MenuOnOffCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('MenuOnOff', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'On' :  b'\x01\x5D\x01\x01', 
            'Off' : b'\x01\x5D\x01\x00'
        }

        PIPCmdString = ValueStateValues[value]
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        PIPCmdString = b'\x00\x5D\x00'
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('PIP', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'PIP' :          b'\x01\x1F\x01\x00', 
            'Side by Side' : b'\x01\x1F\x01\x01'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'PIP', 
            b'\x01' : 'Side by Side'
        }

        PIPModeCmdString = b'\x00\x1F\x00'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPosNegBlue(self, value, qualifier):

        ValueStateValues = {
            'Positive On' : b'\x01\x54\x01\x00', 
            'Negative On' : b'\x01\x54\x01\x01', 
            'Blue On' :     b'\x01\x54\x01\x02'
        }

        PosNegBlueCmdString = ValueStateValues[value]
        self.__SetHelper('PosNegBlue', PosNegBlueCmdString, value, qualifier)

    def UpdatePosNegBlue(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Positive On', 
            b'\x01' : 'Negative On', 
            b'\x02' : 'Blue On'
        }

        PosNegBlueCmdString = b'\x00\x54\x00'
        res = self.__UpdateHelper('PosNegBlue', PosNegBlueCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('PosNegBlue', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : b'\x01\x30\x01\x01',
            'Off' : b'\x01\x30\x01\x00',
            }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            b'\x01' : 'On',
            b'\x00' : 'Off',
           }

        PowerCmdString = b'\x00\x30\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateNames[res[3:4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 3:
            PresetRecallCmdString = pack('>BBBB',0x01,0x40,0x01,int(value))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetStore(self, value, qualifier):

        if 1 <= int(value) <= 3:
            PresetStoreCmdString = pack('>BBBB',0x01,0x41,0x01,int(value))
            self.__SetHelper('PresetStore', PresetStoreCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetStore')
    def SetSnapshot(self, value, qualifier):

        SnapshotCmdString = b'\x01\x95\x01\x00'
        self.__SetHelper('Snapshot', SnapshotCmdString, value, qualifier)
    def SetSource(self, value, qualifier):

        ValueStateValues = {
            'Live' : b'\x01\x9E\x01\x00', 
            'Mem' :  b'\x01\x9E\x01\x01', 
            'USB' :  b'\x01\x9E\x01\x02', 
            'Net' :  b'\x01\x9E\x01\x05'
        }

        SourceCmdString = ValueStateValues[value]
        self.__SetHelper('Source', SourceCmdString, value, qualifier)

    def UpdateSource(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Live', 
            b'\x01' : 'Mem', 
            b'\x02' : 'USB', 
            b'\x05' : 'Net'
        }

        SourceCmdString = b'\x00\x9E\x00'
        res = self.__UpdateHelper('Source', SourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Source', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetStreamingMode(self, value, qualifier):

        ValueStateValues = {
            'Off' :        b'\x01\x75\x01\x00', 
            'Auto' :       b'\x01\x75\x01\x01', 
            'Continuous' : b'\x01\x75\x01\x02', 
        }

        StreamingModeCmdString = ValueStateValues[value]
        self.__SetHelper('StreamingMode', StreamingModeCmdString, value, qualifier)

    def UpdateStreamingMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Off', 
            b'\x01' : 'Auto', 
            b'\x02' : 'Continuous', 
        }

        StreamingModeCmdString = b'\x00\x75\x00'
        res = self.__UpdateHelper('StreamingMode', StreamingModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('StreamingMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetVideoPlayback(self, value, qualifier):

     
        videospeed = int(qualifier['Speed'])
        if 1 <= videospeed <= 15:
            if value == 'Fast Forward Stop':
                VideoPlaybackCmdString = b'\x01\x99\x02\x01\x00'
            elif value == 'Pause/Resume':
                VideoPlaybackCmdString = b'\x01\x99\x01\x91'
            else:
                VideoPlaybackCmdString = pack('>5B',0x01,0x99,0x02,0x01,videospeed)
            self.__SetHelper('VideoPlayback', VideoPlaybackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoPlayback')
    def SetVideoRecording(self, value, qualifier):

        ValueStateValues = {
            'Stop Recording' :  b'\x09\x03\x01\x01\x00', 
            'Start Recording' : b'\x09\x03\x01\x01\x01', 
            'Pause/Resume' :    b'\x09\x03\x01\x01\x02'
        }

        VideoRecordingCmdString = ValueStateValues[value]
        self.__SetHelper('VideoRecording', VideoRecordingCmdString, value, qualifier)

    def UpdateVideoRecording(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Stop Recording', 
            b'\x01' : 'Start Recording', 
            b'\x02' : 'Pause/Resume'
        }

        VideoRecordingCmdString = b'\x08\x03\x01\x00'
        res = self.__UpdateHelper('VideoRecording', VideoRecordingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('VideoRecording', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetWhiteBalance(self, value, qualifier):

        WhiteBalanceCmdString = b'\x01\x65\x01\x10'
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Wide' : 0x01, 
            'Tele' : 0x00, 
        }

        zoomspeed = int(qualifier['Speed'])

        if 1 <= zoomspeed <= 15:
            if value == 'Stop':
                ZoomCmdString = pack('>BBBBBB',0x01,0x20,0x03,0x00,0x00,0x00)
            else:
                ZoomCmdString = pack('>BBBBBB',0x01,0x20,0x03,ValueStateValues[value],0x00,zoomspeed)

            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')
    def __CheckResponseForErrors(self, sourceCmdName, response):

        
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.SetHelper)
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command , res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.UpdateHelper)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command , res)          
            

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

