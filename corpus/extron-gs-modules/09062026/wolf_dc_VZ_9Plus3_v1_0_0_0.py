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
            'AutoFocus': { 'Status': {}},
            'AutoIris': { 'Status': {}},
            'ColorMode': { 'Status': {}},
            'Detail': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'ImageRecall': { 'Status': {}},
            'ImageRotation': { 'Status': {}},
            'ImageSave': { 'Status': {}},
            'Iris': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Light': { 'Status': {}},
            'OutputResolutionDVI': { 'Status': {}},
            'OutputResolutionVGA': { 'Status': {}},
            'OutputSource': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'PosNegBlue': { 'Status': {}},
            'Power': { 'Status': {}},
            'ShowAllImages': { 'Status': {}},
            'TextEnhancer': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': { 'Status': {}}
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x00\x31\x01(\x00|\x01)'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(b'\x00\x32\x01(\x00|\x01)'), self.__MatchAutoIris, None)
            self.AddMatchString(re.compile(b'\x00\x6D\x01([\x00-\x04])'), self.__MatchColorMode, None)
            self.AddMatchString(re.compile(b'\x00\x53\x01([\x00-\x03])'), self.__MatchDetail, None)
            self.AddMatchString(re.compile(b'\x00\x80\x01(\x00|\x01)'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x00\x56\x01(\x00|\x01)'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\x00\x83\x01([\x00-\x03])'), self.__MatchImageRotation, None)
            self.AddMatchString(re.compile(b'\x00\xA3\x02([\x00-\xFF])([\x00-\xFF])'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\x00\xA0\x01(\x00|\x01)'), self.__MatchLight, None)
            self.AddMatchString(re.compile(b'\x00\x51\x01([\x00-\xFF])'), self.__MatchOutputResolutionDVI, None)
            self.AddMatchString(re.compile(b'\x00\x50\x01([\x00-\xFF])'), self.__MatchOutputResolutionVGA, None)
            self.AddMatchString(re.compile(b'\x00\x57\x01(\x00|\x01)'), self.__MatchOutputSource, None)
            self.AddMatchString(re.compile(b'\x00\x54\x01([\x00-\x02])'), self.__MatchPosNegBlue, None)
            self.AddMatchString(re.compile(b'\x00\x30\x01(\x00|\x01)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x00\x93\x01(\x00|\x01)'), self.__MatchShowAllImages, None)
            self.AddMatchString(re.compile(b'\x00\x85\x01(\x00|\x01)'), self.__MatchTextEnhancer, None)
            self.AddMatchString(re.compile(b'\x00\x86\x01(\x00|\x01)'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x00\x65\x01([\x00-\x02])'), self.__MatchWhiteBalance, None)
            self.AddMatchString(re.compile(b'[\x80-\x8F]'
                                           b'[\x31\x32\x6D\x53\x80\x56\x83\xA3\xA0\x51\x50\x57\x54\x30\x93\x85\x86\x65]'
                                           b'([\x00-\x0A])'), self.__MatchError, None)

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        AutoFocusCmdString = b'\x01\x31\x01'+ValueStateValues[value]
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = b'\x00\x31\x00'
        self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def __MatchAutoFocus(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AutoFocus', value, None)

    def SetAutoIris(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        AutoIrisCmdString = b'\x01\x32\x01'+ValueStateValues[value]
        self.__SetHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def UpdateAutoIris(self, value, qualifier):

        AutoIrisCmdString = b'\x00\x32\x00'
        self.__UpdateHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def __MatchAutoIris(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AutoIris', value, None)

    def SetColorMode(self, value, qualifier):

        ValueStateValues = {
            'Black/White'       : b'\x00', 
            'Presentation'      : b'\x01', 
            'Natural'           : b'\x02', 
            'Video Conference'  : b'\x03', 
            'Manual'            : b'\x04'
        }

        ColorModeCmdString = b'\x01\x6D\x01' + ValueStateValues[value]
        self.__SetHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def UpdateColorMode(self, value, qualifier):

        ColorModeCmdString = b'\x00\x6D\x00'
        self.__UpdateHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def __MatchColorMode(self, match, tag):

        ValueStateValues = {
            b'\x00' : 'Black/White', 
            b'\x01' : 'Presentation', 
            b'\x02' : 'Natural', 
            b'\x03' : 'Video Conference', 
            b'\x04' : 'Manual'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ColorMode', value, None)

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'Off' : b'\x00', 
            'Medium' : b'\x02', 
            'High' : b'\x03'
        }

        DetailCmdString = b'\x01\x53\x01'+ValueStateValues[value]
        self.__SetHelper('Detail', DetailCmdString, value, qualifier)

    def UpdateDetail(self, value, qualifier):

        DetailCmdString = b'\x00\x53\x00'
        self.__UpdateHelper('Detail', DetailCmdString, value, qualifier)

    def __MatchDetail(self, match, tag):

        ValueStateValues = {
            b'\x00' : 'Off', 
            b'\x02' : 'Medium', 
            b'\x03' : 'High'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Detail', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        ExecutiveModeCmdString = b'\x01\x80\x01'+ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = b'\x00\x80\x00'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far'   : b'\x01\x21\x01\x11', 
            'Near'  : b'\x01\x21\x01\x12', 
            'Stop'  : b'\x01\x2F\x01\x00'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        FreezeCmdString = b'\x01\x56\x01'+ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = b'\x00\x56\x00'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Freeze', value, None)

    def SetImageRecall(self, value, qualifier):

        ValueStateValues = {
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03', 
            '4' : b'\x04', 
            '5' : b'\x05', 
            '6' : b'\x06', 
            '7' : b'\x07', 
            '8' : b'\x08', 
            '9' : b'\x09'
        }

        ImageRecallCmdString = b'\x01\x91\x01'+ValueStateValues[value]
        self.__SetHelper('ImageRecall', ImageRecallCmdString, value, qualifier)

    def SetImageRotation(self, value, qualifier):

        ValueStateValues = {
            'Toggle' : b'\x02', 
            'Off' : b'\x00',
        }

        ImageRotationCmdString = b'\x01\x83\x01'+ValueStateValues[value]
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)

    def UpdateImageRotation(self, value, qualifier):

        ImageRotationCmdString = b'\x00\x83\x00'
        self.__UpdateHelper('ImageRotation', ImageRotationCmdString, value, qualifier)

    def __MatchImageRotation(self, match, tag):

        ValueStateValues = {
            b'\x00' : '0', 
            b'\x01' : '-90', 
            b'\x02' : '180', 
            b'\x03' : '90'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ImageRotation', value, None)

    def SetImageSave(self, value, qualifier):

        ValueStateValues = {
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03', 
            '4' : b'\x04', 
            '5' : b'\x05', 
            '6' : b'\x06', 
            '7' : b'\x07', 
            '8' : b'\x08', 
            '9' : b'\x09', 
            'Auto Snapshot' : b'\x10',
            'Erase All' : b'\x20'
        }

        ImageSaveCmdString = b'\x01\x92\x01'+ValueStateValues[value]
        self.__SetHelper('ImageSave', ImageSaveCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Open' : b'\x01\x22\x01\x11', 
            'Close' : b'\x01\x22\x01\x12', 
            'Stop' : b'\x01\x2F\x01\x00'
        }

        IrisCmdString = ValueStateValues[value]
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x00\xA3\x00'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = (match.group(1)[0] * 256) + match.group(2)[0]
        self.WriteStatus('LampUsage', value, None)

    def SetLight(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        LightCmdString = b'\x01\xA0\x01'+ValueStateValues[value]
        self.__SetHelper('Light', LightCmdString, value, qualifier)

    def UpdateLight(self, value, qualifier):

        LightCmdString = b'\x00\xA0\x00'
        self.__UpdateHelper('Light', LightCmdString, value, qualifier)

    def __MatchLight(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Light', value, None)

    def SetOutputResolutionDVI(self, value, qualifier):

        ValueStateValues = {
            'Off' : b'\xFF', 
            'Auto' : b'\x00', 
            '800x600 (60Hz)' : b'\x01', 
            '1024x768 (60Hz)' : b'\x04', 
            '1280x960 (60Hz)' : b'\x08', 
            '1280x1024 (60Hz)' : b'\x0A',
            '1600x1200 (60Hz)' : b'\x0D', 
            '1400x1050 (60Hz)' : b'\x12', 
            '640x480 (60Hz)' : b'\x14', 
            '1280x720 (50Hz)' : b'\x15', 
            '1280x720 (60Hz)' : b'\x16', 
            '1920x1080 (50Hz)' : b'\x17', 
            '1920x1080 (60Hz)' : b'\x18', 
            '1680x1050 (60Hz)' : b'\x1A', 
            '1366x768 (60Hz)' : b'\x1B', 
            '1920x1200 (60Hz)' : b'\x1C', 
            '1440x900 (60Hz)' : b'\x1D', 
            '1280x800 (60Hz)' : b'\x1E', 
            '1920x1080 (30Hz)' : b'\x20'
        }

        OutputResolutionDVICmdString = b'\x01\x51\x01'+ValueStateValues[value]
        self.__SetHelper('OutputResolutionDVI', OutputResolutionDVICmdString, value, qualifier)

    def UpdateOutputResolutionDVI(self, value, qualifier):

        OutputResolutionDVICmdString = b'\x00\x51\x00'
        self.__UpdateHelper('OutputResolutionDVI', OutputResolutionDVICmdString, value, qualifier)

    def __MatchOutputResolutionDVI(self, match, tag):

        ValueStateValues = {
            b'\xFF' : 'Off', 
            b'\x00' : 'Auto', 
            b'\x01' : '800x600 (60Hz)', 
            b'\x04' : '1024x768 (60Hz)', 
            b'\x08' : '1280x960 (60Hz)',
            b'\x0A' : '1280x1024 (60Hz)', 
            b'\x0D' : '1600x1200 (60Hz)', 
            b'\x12' : '1400x1050 (60Hz)', 
            b'\x14' : '640x480 (60Hz)', 
            b'\x15' : '1280x720 (50Hz)', 
            b'\x16' : '1280x720 (60Hz)', 
            b'\x17' : '1920x1080 (50Hz)', 
            b'\x18' : '1920x1080 (60Hz)', 
            b'\x1A' : '1680x1050 (60Hz)', 
            b'\x1B' : '1366x768 (60Hz)', 
            b'\x1C' : '1920x1200 (60Hz)', 
            b'\x1D' : '1440x900 (60Hz)', 
            b'\x1E' : '1280x800 (60Hz)', 
            b'\x20' : '1920x1080 (30Hz)'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('OutputResolutionDVI', value, None)

    def SetOutputResolutionVGA(self, value, qualifier):

        ValueStateValues = {
            'Off' : b'\xFF', 
            'Auto' : b'\x00', 
            '800x600 (60Hz)' : b'\x01', 
            '1024x768 (60Hz)' : b'\x04', 
            '1280x960 (60Hz)' : b'\x08',
            '1280x1024 (60Hz)' : b'\x0A',
            '1600x1200 (60Hz)' : b'\x0D', 
            '1400x1050 (60Hz)' : b'\x12', 
            '640x480 (60Hz)' : b'\x14', 
            '1280x720 (50Hz)' : b'\x15', 
            '1280x720 (60Hz)' : b'\x16', 
            '1920x1080 (50Hz)' : b'\x17', 
            '1920x1080 (60Hz)' : b'\x18', 
            '1680x1050 (60Hz)' : b'\x1A', 
            '1366x768 (60Hz)' : b'\x1B', 
            '1920x1200 (60Hz)' : b'\x1C', 
            '1440x900 (60Hz)' : b'\x1D', 
            '1280x800 (60Hz)' : b'\x1E', 
            '1920x1080 (30Hz)' : b'\x20'
        }

        OutputResolutionVGACmdString = b'\x01\x50\x01'+ValueStateValues[value]
        self.__SetHelper('OutputResolutionVGA', OutputResolutionVGACmdString, value, qualifier)

    def UpdateOutputResolutionVGA(self, value, qualifier):

        OutputResolutionVGACmdString = b'\x00\x50\x00'
        self.__UpdateHelper('OutputResolutionVGA', OutputResolutionVGACmdString, value, qualifier)

    def __MatchOutputResolutionVGA(self, match, tag):

        ValueStateValues = {
            b'\xFF' : 'Off', 
            b'\x00' : 'Auto', 
            b'\x01' : '800x600 (60Hz)', 
            b'\x04' : '1024x768 (60Hz)', 
            b'\x08' : '1280x960 (60Hz)',
            b'\x0A' : '1280x1024 (60Hz)',  
            b'\x0D' : '1600x1200 (60Hz)', 
            b'\x12' : '1400x1050 (60Hz)', 
            b'\x14' : '640x480 (60Hz)', 
            b'\x15' : '1280x720 (50Hz)', 
            b'\x16' : '1280x720 (60Hz)', 
            b'\x17' : '1920x1080 (50Hz)', 
            b'\x18' : '1920x1080 (60Hz)', 
            b'\x1A' : '1680x1050 (60Hz)', 
            b'\x1B' : '1366x768 (60Hz)', 
            b'\x1C' : '1920x1200 (60Hz)', 
            b'\x1D' : '1440x900 (60Hz)', 
            b'\x1E' : '1280x800 (60Hz)', 
            b'\x20' : '1920x1080 (30Hz)'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('OutputResolutionVGA', value, None)

    def SetOutputSource(self, value, qualifier):

        ValueStateValues = {
            'External' : b'\x01', 
            'Internal' : b'\x00'
        }

        OutputSourceCmdString = b'\x01\x57\x01'+ValueStateValues[value]
        self.__SetHelper('OutputSource', OutputSourceCmdString, value, qualifier)

    def UpdateOutputSource(self, value, qualifier):

        OutputSourceCmdString = b'\x00\x57\x00'
        self.__UpdateHelper('OutputSource', OutputSourceCmdString, value, qualifier)

    def __MatchOutputSource(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'External', 
            b'\x00' : 'Internal'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('OutputSource', value, None)

    def SetPosNegBlue(self, value, qualifier):

        ValueStateValues = {
            'Positive' : b'\x00', 
            'Negative' : b'\x01', 
            'Blue' : b'\x02'
        }

        PosNegBlueCmdString = b'\x01\x54\x01'+ValueStateValues[value]
        self.__SetHelper('PosNegBlue', PosNegBlueCmdString, value, qualifier)

    def UpdatePosNegBlue(self, value, qualifier):

        PosNegBlueCmdString = b'\x00\x54\x00'
        self.__UpdateHelper('PosNegBlue', PosNegBlueCmdString, value, qualifier)

    def __MatchPosNegBlue(self, match, tag):

        ValueStateValues = {
            b'\x00' : 'Positive', 
            b'\x01' : 'Negative', 
            b'\x02' : 'Blue'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PosNegBlue', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        PowerCmdString = b'\x01\x30\x01'+ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '\x00\x30\x00'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1' : b'\x01\x40\x01\x01', 
            '2' : b'\x01\x40\x01\x02', 
            '3' : b'\x01\x40\x01\x03', 
            'Factory Preset' : b'\x01\x8F\x01\x00'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03'
        }

        PresetSaveCmdString = b'\x01\x41\x01'+ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetShowAllImages(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        ShowAllImagesCmdString = b'\x01\x93\x01'+ValueStateValues[value]
        self.__SetHelper('ShowAllImages', ShowAllImagesCmdString, value, qualifier)

    def UpdateShowAllImages(self, value, qualifier):

        ShowAllImagesCmdString = b'\x00\x93\x00'
        self.__UpdateHelper('ShowAllImages', ShowAllImagesCmdString, value, qualifier)

    def __MatchShowAllImages(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ShowAllImages', value, None)

    def SetTextEnhancer(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        TextEnhancerCmdString = b'\x01\x85\x01'+ValueStateValues[value]
        self.__SetHelper('TextEnhancer', TextEnhancerCmdString, value, qualifier)

    def UpdateTextEnhancer(self, value, qualifier):

        TextEnhancerCmdString = b'\x00\x85\x00'
        self.__UpdateHelper('TextEnhancer', TextEnhancerCmdString, value, qualifier)

    def __MatchTextEnhancer(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('TextEnhancer', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01', 
            'Off' : b'\x00'
        }

        VideoMuteCmdString = b'\x01\x86\x01'+ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\x00\x86\x00'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('VideoMute', value, None)

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto' : b'\x00', 
            'Manual' : b'\x02', 
            'Perform WB' : b'\x10', 
            'One-Push' : b'\x01'
        }

        WhiteBalanceCmdString = b'\x01\x65\x01'+ValueStateValues[value]
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        WhiteBalanceCmdString = b'\x00\x65\x00'
        self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def __MatchWhiteBalance(self, match, tag):

        ValueStateValues = {
            b'\x00' : 'Auto', 
            b'\x02' : 'Manual',
            b'\x01' : 'One-Push'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('WhiteBalance', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : b'\x01\x20\x01\x12', 
            'Wide' : b'\x01\x20\x01\x11', 
            'Stop' : b'\x01\x2F\x01\x00'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

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

        ErrorList = {
            b'\x01' : 'Time out',
            b'\x02' : 'Invalid Command',
            b'\x03' : 'Invalid Parameter',
            b'\x04' : 'Invalid Length',
            b'\x05' : 'FiFo Full',
            b'\x06' : 'Firmware Update Error',
            b'\x07' : 'Access Denied',
            b'\x08' : 'Auth Required',
            b'\x09' : 'Busy',
            b'\x0A' : 'SIP Required'
            }

        self.Error([ErrorList[match.group(1)]])

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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