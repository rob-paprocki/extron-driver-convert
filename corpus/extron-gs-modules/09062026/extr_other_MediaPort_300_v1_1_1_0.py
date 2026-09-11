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
            'ActiveLines': {'Status': {}},
            'ActivePixels': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioInputFormatStatus': {'Parameters': ['Input'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'AutoMemory': {'Status': {}},
            'Freeze': {'Status': {}},
            'HDCPAuthentication': {'Status': {}},
            'HDCPMode': {'Status': {}},
            'HDCPNotification': {'Parameters':['Output'], 'Status': {}},
            'HDMILoopFormat': {'Status': {}},
            'InputHDCPStatus': {'Status': {}},
            'InputHDMIGain': {'Parameters':['L/R'], 'Status': {}},
            'InputHDMIMute': {'Parameters':['L/R'], 'Status': {}},
            'InputLineInGain': {'Status': {}},
            'InputLineInMute': {'Status': {}},
            'InputMicLineGain': {'Status': {}},
            'InputMicLineMute': {'Status': {}},
            'InputMicLinePhantomPower': {'Status': {}},
            'InputPreMixerHDMIGain': {'Status': {}},
            'InputPreMixerHDMIMute': {'Status': {}},
            'InputPreMixerLineInGain': {'Status': {}},
            'InputPreMixerLineInMute': {'Status': {}},
            'InputPreMixerMicLineGain': {'Status': {}},
            'InputPreMixerMicLineMute': {'Status': {}},
            'InputPreMixerUSBGain': {'Status': {}},
            'InputPreMixerUSBMute': {'Status': {}},
            'InputUSBGain': {'Parameters':['L/R'], 'Status': {}},
            'InputUSBMute': {'Parameters':['L/R'], 'Status': {}},
            'MixtoFarEndMic': {'Status': {}},
            'MixtoFarEndMicMute': {'Status': {}},
            'MixtoFarEndProgram': {'Status': {}},
            'MixtoFarEndProgramMute': {'Status': {}},
            'NearEndMixPC': {'Status': {}},
            'NearEndMixPCMute': {'Status': {}},
            'NearEndMixProgram': {'Status': {}},
            'NearEndMixProgramMute': {'Status': {}},
            'OutputHDCPStatus': {'Status': {}},
            'OutputLineAttenuation': {'Parameters':['Output'], 'Status': {}},
            'OutputLineMute': {'Parameters':['Output'], 'Status': {}},
            'OutputUSBAttenuation': {'Status': {}},
            'OutputUSBMute': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'ScreenSaverMode': {'Status': {}},
            'ScreenSaverStatus': {'Status': {}},
            'USBHIDHook': {'Status': {}},
            'USBHIDHookLEDStatus': {'Status': {}},
            'USBHIDMuteLEDStatus': {'Status': {}},
            'USBHIDRingLEDStatus': {'Status': {}},
            'USBHostStatus': {'Status': {}},
            'USBStreamingFormat': {'Status': {}},
            'USBTerminalType': {'Status': {}},
            'VerticalRefreshRate': {'Status': {}},
            'VideoMute': {'Parameters':['Output'], 'Status': {}},
            'VideoSendStatus': {'Status': {}},
            'InputSignalStatus': {'Status': {}},
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'SpecV1\*(\d+)\*(\d+)\*\d+\*\d+\r\n'), self.__MatchActiveLines, None)
            self.AddMatchString(re.compile(b'Aspr1\*([12])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'40Stat ([023])\*([01])\r\n'), self.__MatchAudioInputFormatStatus, None)
            self.AddMatchString(re.compile(b'Amem1\*([01])\r\n'), self.__MatchAutoMemory, None)
            self.AddMatchString(re.compile(b'Frz1\*([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'HdcpE1\*([01])\r\n'), self.__MatchHDCPAuthentication, None)
            self.AddMatchString(re.compile(b'HdcpS2\*([0-4])\r\n'), self.__MatchHDCPMode, None)
            self.AddMatchString(re.compile(b'HdcpN([12])\*([012])\r\n'), self.__MatchHDCPNotification, None)
            self.AddMatchString(re.compile(b'Vtpo2\*([0-9])\r\n'), self.__MatchHDMILoopFormat, None)
            self.AddMatchString(re.compile(b'HdcpI1\*([0-2])\r\n'), self.__MatchInputHDCPStatus, None)
            self.AddMatchString(re.compile(b'DsG30000\*(-?\d+)\r\n'), self.__MatchInputHDMIGain, 'Left')
            self.AddMatchString(re.compile(b'DsM30000\*([01])\r\n'), self.__MatchInputHDMIMute, 'Left')
            self.AddMatchString(re.compile(b'DsG30001\*(-?\d+)\r\n'), self.__MatchInputHDMIGain, 'Right')
            self.AddMatchString(re.compile(b'DsM30001\*([01])\r\n'), self.__MatchInputHDMIMute, 'Right')
            self.AddMatchString(re.compile(b'DsG40001\*(-?\d+)\r\n'), self.__MatchInputLineInGain, None)
            self.AddMatchString(re.compile(b'DsM40001\*([01])\r\n'), self.__MatchInputLineInMute, None)
            self.AddMatchString(re.compile(b'DsG30002\*(-?\d+)\r\n'), self.__MatchInputUSBGain, 'Left')
            self.AddMatchString(re.compile(b'DsM30002\*([01])\r\n'), self.__MatchInputUSBMute, 'Left')
            self.AddMatchString(re.compile(b'DsG30003\*(-?\d+)\r\n'), self.__MatchInputUSBGain, 'Right')
            self.AddMatchString(re.compile(b'DsM30003\*([01])\r\n'), self.__MatchInputUSBMute, 'Right')
            self.AddMatchString(re.compile(b'DsG40000\*(-?\d+)\r\n'), self.__MatchInputMicLineGain, None)
            self.AddMatchString(re.compile(b'DsM40000\*([01])\r\n'), self.__MatchInputMicLineMute, None)
            self.AddMatchString(re.compile(b'DsZ40000\*([01])\r\n'), self.__MatchInputMicLinePhantomPower, None)
            self.AddMatchString(re.compile(b'DsG30100\*(-?\d+)\r\n'), self.__MatchInputPreMixerHDMIGain, None)
            self.AddMatchString(re.compile(b'DsM30100\*([01])\r\n'), self.__MatchInputPreMixerHDMIMute, None)
            self.AddMatchString(re.compile(b'DsG40101\*(-?\d+)\r\n'), self.__MatchInputPreMixerLineInGain, None)
            self.AddMatchString(re.compile(b'DsM40101\*([01])\r\n'), self.__MatchInputPreMixerLineInMute, None)
            self.AddMatchString(re.compile(b'DsG40100\*(-?\d+)\r\n'), self.__MatchInputPreMixerMicLineGain, None)
            self.AddMatchString(re.compile(b'DsM40100\*([01])\r\n'), self.__MatchInputPreMixerMicLineMute, None)
            self.AddMatchString(re.compile(b'DsG30102\*(-?\d+)\r\n'), self.__MatchInputPreMixerUSBGain, None)
            self.AddMatchString(re.compile(b'DsM30102\*([01])\r\n'), self.__MatchInputPreMixerUSBMute, None)
            self.AddMatchString(re.compile(b'GrpmD([1-9]|10)\*(-?\d+)'), self.__MatchGroup, None)
            self.AddMatchString(re.compile(b'DsG6000([23])\*(-?\d+)\r\n'), self.__MatchOutputLineAttenuation, None)
            self.AddMatchString(re.compile(b'DsM6000([23])\*([01])\r\n'), self.__MatchOutputLineMute, None)
            self.AddMatchString(re.compile(b'HdcpO2\*([0-2])\r\n'), self.__MatchOutputHDCPStatus, None)
            self.AddMatchString(re.compile(b'SsavM1\*([0-2])\r\n'), self.__MatchScreenSaverMode, None)
            self.AddMatchString(re.compile(b'SsavS1\*([01])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(re.compile(b'UphnH1\*([01])\r\n'), self.__MatchUSBHIDHook, None)
            self.AddMatchString(re.compile(b'UphnK1\*([01])\r\n'), self.__MatchUSBHIDHookLEDStatus, None)
            self.AddMatchString(re.compile(b'UphnM1\*([01])\r\n'), self.__MatchUSBHIDMuteLEDStatus, None)
            self.AddMatchString(re.compile(b'UphnG1\*([01])\r\n'), self.__MatchUSBHIDRingLEDStatus, None)
            self.AddMatchString(re.compile(b'Inf35\*Host([01]) VSend([01]) CommOut[01] CommIn[01] USBStd[0-3]\r\n'), self.__MatchUSBHostStatus, None)
            self.AddMatchString(re.compile(b'Otyp1\*([0123])\r\n'), self.__MatchUSBStreamingFormat, None)
            self.AddMatchString(re.compile(b'UsbcC(\d+)\r\n'), self.__MatchUSBTerminalType, None)
            self.AddMatchString(re.compile(b'Inf0?0?\*Typ[0-2] Vmt([01])\*([012]) Hrt\d+.\d+ Vrt(\d+.\d+)\r\n'), self.__MatchVerticalRefreshRate, None)
            self.AddMatchString(re.compile(b'Vmt([0-2])([ *])([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'In00 ([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'(?<!Uphn)E(\d+)\r\n'), self.__MatchError, None)

            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)   

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False

    def UpdateActiveLines(self, value, qualifier):

        ActiveLinesCmdString = 'wV1spec\r'
        self.__UpdateHelper('ActiveLines', ActiveLinesCmdString, value, qualifier)

    def __MatchActiveLines(self, match, tag):

        self.WriteStatus('ActiveLines', int(match.group(2).decode()), None)
        self.WriteStatus('ActivePixels', int(match.group(1).decode()), None)
        
    def UpdateActivePixels(self, value, qualifier):

        self.UpdateActiveLines(value, qualifier)
        
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill'   : 'w1*1ASPR\r',
            'Follow' : 'w1*2ASPR\r'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = ValueStateValues[value]
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'w1ASPR\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '1' : 'Fill', 
            '2' : 'Follow'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def UpdateAudioInputFormatStatus(self, value, qualifier):

        AudioInputFormatStatusCmdString = 'w40STAT\r'
        self.__UpdateHelper('AudioInputFormatStatus', AudioInputFormatStatusCmdString, value, qualifier)

    def __MatchAudioInputFormatStatus(self, match, tag):

        ValueStateValues = {
            'HDMI' : {
                '0' : 'None',
                '2' : 'LPCM 2-Ch Digital',
                '3' : 'Multi-Channel Digital'
            },
            'USB' : {
                '0' : 'None',
                '1' : 'LPCM 2-Ch'
            }
        }

        self.WriteStatus('AudioInputFormatStatus', ValueStateValues['HDMI'][match.group(1).decode()], {'Input' : 'HDMI'})
        self.WriteStatus('AudioInputFormatStatus', ValueStateValues['USB'][match.group(2).decode()], {'Input' : 'USB'})

    def SetAutoImage(self, value, qualifier):

        ValueStateValues = {
            'Execute' : 'A', 
            'Execute and Fill' : '1*A', 
            'Execute and Follow' : '2*A'
        }

        if value in ValueStateValues:
            AutoImageCmdString = ValueStateValues[value]
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')
            
    def SetAutoMemory(self, value, qualifier):

        ValueStateValues = {
            'On' : 'w1*1AMEM\r', 
            'Off' : 'w1*0AMEM\r'
        }

        if value in ValueStateValues:
            AutoMemoryCmdString = ValueStateValues[value]
            self.__SetHelper('AutoMemory', AutoMemoryCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoMemory')

    def UpdateAutoMemory(self, value, qualifier):

        AutoMemoryCmdString = 'w1AMEM\r'
        self.__UpdateHelper('AutoMemory', AutoMemoryCmdString, value, qualifier)

    def __MatchAutoMemory(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoMemory', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On' : '1*1F', 
            'Off' : '1*0F'
        }

        if value in ValueStateValues:
            FreezeCmdString = ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '1F'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetHDCPAuthentication(self, value, qualifier):

        ValueStateValues = {
            'On' : 'wE1*1HDCP\r', 
            'Off' : 'wE1*0HDCP\r'
        }

        if value in ValueStateValues:
            HDCPAuthenticationCmdString = ValueStateValues[value]
            self.__SetHelper('HDCPAuthentication', HDCPAuthenticationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPAuthentication')

    def UpdateHDCPAuthentication(self, value, qualifier):

        HDCPAuthenticationCmdString = 'wE1HDCP\r'
        self.__UpdateHelper('HDCPAuthentication', HDCPAuthenticationCmdString, value, qualifier)

    def __MatchHDCPAuthentication(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPAuthentication', value, None)

    def SetHDCPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': 'wS2*0HDCP\r',
            'Mode 1' : 'wS2*1HDCP\r', 
            'Mode 2' : 'wS2*2HDCP\r', 
            'Mode 3' : 'wS2*3HDCP\r', 
            'Mode 4' : 'wS2*4HDCP\r'
        }

        if value in ValueStateValues:
            HDCPModeCmdString = ValueStateValues[value]
            self.__SetHelper('HDCPMode', HDCPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPMode')

    def UpdateHDCPMode(self, value, qualifier):

        HDCPModeCmdString = 'wS2HDCP\r'
        self.__UpdateHelper('HDCPMode', HDCPModeCmdString, value, qualifier)

    def __MatchHDCPMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Off',
            '1' : 'Mode 1', 
            '2' : 'Mode 2', 
            '3' : 'Mode 3', 
            '4' : 'Mode 4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPMode', value, None)

    def SetHDCPNotification(self, value, qualifier):

        ValueStateValues = {
            'Black' : '0HDCP\r', 
            'Green' : '1HDCP\r',
            'User Image' : '2HDCP\r'
        }

        outputs = {
            'USB': '1',
            'HDMI Loop': '2'
        }

        if value in ValueStateValues and qualifier['Output'] in outputs:
            HDCPNotificationCmdString = 'wN{0}*{1}HDCP\r\n'.format(outputs[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('HDCPNotification', HDCPNotificationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPNotification')

    def UpdateHDCPNotification(self, value, qualifier):

        outputs = {
            'USB': '1',
            'HDMI Loop': '2'
        }

        if qualifier['Output'] in outputs:
            HDCPNotificationCmdString = 'wN{0}HDCP\r'.format(outputs[qualifier['Output']])
            self.__UpdateHelper('HDCPNotification', HDCPNotificationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPNotification')

    def __MatchHDCPNotification(self, match, tag):

        ValueStateValues = {
            '1' : 'Green', 
            '0' : 'Black',
            '2' : 'User Image'
        }

        outputs = {
            '1': 'USB',
            '2': 'HDMI Loop'
        }

        output = outputs[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPNotification', value, {'Output': output})

    def SetHDMILoopFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto' : '0', 
            'DVI RGB 444' : '1', 
            'RGB 444 Full' : '2', 
            'RGB 444 Limited' : '3',  
            'YUV 444 Limited' : '5', 
            'YUV 422 Limited' : '7',
            'YUV 420 Limited' : '9'
        }

        if value in ValueStateValues:
            HDMILoopFormatCmdString = 'w2*{0}VTPO\r'.format(ValueStateValues[value])
            self.__SetHelper('HDMILoopFormat', HDMILoopFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMILoopFormat')

    def UpdateHDMILoopFormat(self, value, qualifier):

        HDMILoopFormatCmdString = 'w2VTPO\r'
        self.__UpdateHelper('HDMILoopFormat', HDMILoopFormatCmdString, value, qualifier)

    def __MatchHDMILoopFormat(self, match, tag):

        ValueStateValues = {
            '0' : 'Auto', 
            '1' : 'DVI RGB 444', 
            '2' : 'RGB 444 Full', 
            '3' : 'RGB 444 Limited', 
            '4' : 'YUV 444 Full', 
            '5' : 'YUV 444 Limited', 
            '6' : 'YUV 422 Full', 
            '7' : 'YUV 422 Limited',
            '9' : 'YUV 420 Limited'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDMILoopFormat', value, None)

    def UpdateInputHDCPStatus(self, value, qualifier):

        InputHDCPStatusCmdString = 'wI1HDCP\r'
        self.__UpdateHelper('InputHDCPStatus', InputHDCPStatusCmdString, value, qualifier)

    def __MatchInputHDCPStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No active video source detected',
            '1' : 'Source detected but no HDCP is present',
            '2' : 'Video with HDCP detected'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InputHDCPStatus', value, None)

    def SetInputHDMIGain(self, value, qualifier):

        LR = {
            'Left'  :'0',
            'Right' :'1'
        }

        if -18 <= value <= 24 and qualifier['L/R'] in LR:
            CmdString = 'wG3000{0}*{1}AU\r'.format(LR[qualifier['L/R']], round(value*10))
            self.__SetHelper('InputHDMIGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputHDMIGain')

    def UpdateInputHDMIGain(self, value, qualifier):
        LR = {
            'Left'  : '0',
            'Right' : '1'
        }

        if qualifier['L/R'] in LR:
            CmdString = 'wG3000{}AU\r'.format(LR[qualifier['L/R']])
            self.__UpdateHelper('InputHDMIGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputHDMIGain')

    def __MatchInputHDMIGain(self, match, tag):
        self.WriteStatus('InputHDMIGain',  int(match.group(1).decode())/10 , {'L/R':tag} )

    def SetInputHDMIMute(self, value, qualifier):

        LR = {
            'Left'  :'0',
            'Right' :'1'
        }

        States = {
            'On'  :'1',
            'Off' :'0'
        }

        if value in States and qualifier['L/R'] in LR:
            CmdString = 'wM3000{0}*{1}AU\r'.format( LR[qualifier['L/R']] , States[value] )
            self.__SetHelper('InputHDMIMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputHDMIMute')

    def UpdateInputHDMIMute(self, value, qualifier):
        LR = {
            'Left'  : '0',
            'Right' : '1'
        }

        if qualifier['L/R'] in LR:
            CmdString = 'wM3000{}AU\r'.format( LR[qualifier['L/R']] )
            self.__UpdateHelper('InputHDMIMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputHDMIMute')

    def __MatchInputHDMIMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputHDMIMute',  States[match.group(1).decode()] , {'L/R':tag} )

    def SetInputLineInGain(self, value, qualifier):

        if -18 <= value <= 24:
            CmdString = 'wG40001*{0}AU\r'.format(round(value*10))
            self.__SetHelper('InputLineInGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLineInGain')

    def UpdateInputLineInGain(self, value, qualifier):

        CmdString = 'wG40001AU\r'
        self.__UpdateHelper('InputLineInGain', CmdString, value, qualifier)

    def __MatchInputLineInGain(self, match, tag):
        self.WriteStatus('InputLineInGain',  int(match.group(1).decode())/10 , None )

    def SetInputLineInMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM40001*{0}AU\r'.format(States[value])
            self.__SetHelper('InputLineInMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLineInMute')

    def UpdateInputLineInMute(self, value, qualifier):

        CmdString = 'wM40001AU\r'
        self.__UpdateHelper('InputLineInMute', CmdString, value, qualifier)

    def __MatchInputLineInMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputLineInMute', States[match.group(1).decode()], None)

    def SetInputMicLineGain(self, value, qualifier):

        if -18 <= value <= 60:
            CmdString = 'wG40000*{}AU\r'.format(round(value*10))
            self.__SetHelper('InputMicLineGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMicLineGain')

    def UpdateInputMicLineGain(self, value, qualifier):
        self.__UpdateHelper('InputMicLineGain', 'wG40000AU\r' , value, qualifier)

    def __MatchInputMicLineGain(self, match, tag):
        self.WriteStatus('InputMicLineGain', int(match.group(1).decode())/10, None)

    def SetInputMicLineMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM40000*{}AU\r'.format(States[value])
            self.__SetHelper('InputMicLineMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMicLineMute')

    def UpdateInputMicLineMute(self, value, qualifier):
        self.__UpdateHelper('InputMicLineMute', 'wM40000AU\r' , value, qualifier)

    def __MatchInputMicLineMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputMicLineMute',  States[match.group(1).decode()] , None)

    def SetInputMicLinePhantomPower(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wz40000*{}AU\r'.format(States[value])
            self.__SetHelper('InputMicLinePhantomPower', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMicLinePhantomPower')

    def UpdateInputMicLinePhantomPower(self, value, qualifier):
        self.__UpdateHelper('InputMicLinePhantomPower', 'wz40000AU\r' , value, qualifier)

    def __MatchInputMicLinePhantomPower(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputMicLinePhantomPower',  States[match.group(1).decode()] , None)

    def SetInputPreMixerHDMIGain(self, value, qualifier):

        if -100 <= value <= 12:
            CmdString = 'wG30100*{0}AU\rwG30101*{0}AU\r'.format(round(value*10))
            self.__SetHelper('InputPreMixerHDMIGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerHDMIGain')

    def UpdateInputPreMixerHDMIGain(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerHDMIGain', 'wG30100AU\r' , value, qualifier)

    def __MatchInputPreMixerHDMIGain(self, match, tag):
        self.WriteStatus('InputPreMixerHDMIGain',  int(match.group(1).decode())/10 , None)

    def SetInputPreMixerHDMIMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM30100*{0}AU\rwM30101*{0}AU\r'.format(States[value])
            self.__SetHelper('InputPreMixerHDMIMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerHDMIMute')

    def UpdateInputPreMixerHDMIMute(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerHDMIMute', 'wM30100AU\r' , value, qualifier)

    def __MatchInputPreMixerHDMIMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputPreMixerHDMIMute', States[match.group(1).decode()], None)

    def SetInputPreMixerLineInGain(self, value, qualifier):

        if -100 <= value <= 12:
            CmdString = 'wG40101*{0}AU\r'.format(round(value*10))
            self.__SetHelper('InputPreMixerLineInGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerLineInGain')

    def UpdateInputPreMixerLineInGain(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerLineInGain', 'wG40101AU\r' , value, qualifier)

    def __MatchInputPreMixerLineInGain(self, match, tag):
        self.WriteStatus('InputPreMixerLineInGain',  int(match.group(1).decode())/10 , None)

    def SetInputPreMixerLineInMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM40101*{0}AU\r'.format(States[value])
            self.__SetHelper('InputPreMixerLineInMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerLineInMute')

    def UpdateInputPreMixerLineInMute(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerLineInMute', 'wM40101AU\r' , value, qualifier)

    def __MatchInputPreMixerLineInMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputPreMixerLineInMute',  States[match.group(1).decode()] , None)

    def SetInputPreMixerMicLineGain(self, value, qualifier):

        if -100 <= value <= 12:
            CmdString = 'wG40100*{0}AU\r'.format(round(value*10))
            self.__SetHelper('InputPreMixerMicLineGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerMicLineGain')

    def UpdateInputPreMixerMicLineGain(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerMicLineGain', 'wG40100AU\r' , value, qualifier)

    def __MatchInputPreMixerMicLineGain(self, match, tag):
        self.WriteStatus('InputPreMixerMicLineGain',  int(match.group(1).decode())/10 , None)

    def SetInputPreMixerMicLineMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM40100*{0}AU\r'.format(States[value])
            self.__SetHelper('InputPreMixerMicLineMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerMicLineMute')

    def UpdateInputPreMixerMicLineMute(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerMicLineMute', 'wM40100AU\r' , value, qualifier)

    def __MatchInputPreMixerMicLineMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputPreMixerMicLineMute',  States[match.group(1).decode()] , None)

    def SetInputPreMixerUSBGain(self, value, qualifier):

        if -100 <= value <= 12:
            CmdString = 'wG30102*{0}AU\rwG30103*{0}AU\r'.format(round(value*10))
            self.__SetHelper('InputPreMixerUSBGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerUSBGain')

    def UpdateInputPreMixerUSBGain(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerUSBGain', 'wG30102AU\r' , value, qualifier)

    def __MatchInputPreMixerUSBGain(self, match, tag):
        self.WriteStatus('InputPreMixerUSBGain', int(match.group(1).decode())/10, None)

    def SetInputPreMixerUSBMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM30102*{0}AU\rwM30103*{0}AU\r'.format(States[value])
            self.__SetHelper('InputPreMixerUSBMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerUSBMute')

    def UpdateInputPreMixerUSBMute(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerUSBMute', 'wM30102AU\r' , value, qualifier)

    def __MatchInputPreMixerUSBMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputPreMixerUSBMute',  States[match.group(1).decode()] , None)

    def SetInputUSBGain(self, value, qualifier):

        LR = {
            'Left'  : '2',
            'Right' : '3'
        }

        if -100 <= value <= 0 and qualifier['L/R'] in LR:
            CmdString = 'wG3000{0}*{1}AU\r'.format(LR[qualifier['L/R']], round(value*10))
            self.__SetHelper('InputUSBGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputUSBGain')

    def UpdateInputUSBGain(self, value, qualifier):
        LR = {
            'Left'  : '2',
            'Right' : '3'
        }

        if qualifier['L/R'] in LR:
            CmdString = 'wG3000{}AU\r'.format(LR[qualifier['L/R']])
            self.__UpdateHelper('InputUSBGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputUSBGain')

    def __MatchInputUSBGain(self, match, tag):
        self.WriteStatus('InputUSBGain',  int(match.group(1).decode())/10 , {'L/R':tag} )

    def SetInputUSBMute(self, value, qualifier):

        LR = {
            'Left'  : '2',
            'Right' : '3'
        }

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States and qualifier['L/R'] in LR:
            CmdString = 'wM3000{0}*{1}AU\r'.format(LR[qualifier['L/R']], States[value])
            self.__SetHelper('InputUSBMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputUSBMute')

    def UpdateInputUSBMute(self, value, qualifier):
        LR = {
            'Left'  : '2',
            'Right' : '3'
        }

        if qualifier['L/R'] in LR:
            CmdString = 'wM3000{}AU\r'.format(LR[qualifier['L/R']])
            self.__UpdateHelper('InputUSBMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputUSBMute')

    def __MatchInputUSBMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputUSBMute',  States[match.group(1).decode()] , {'L/R':tag} )

    def UpdateOutputHDCPStatus(self, value, qualifier):

        OutputHDCPStatusCmdString = 'wO2HDCP\r'
        self.__UpdateHelper('OutputHDCPStatus', OutputHDCPStatusCmdString, value, qualifier)

    def __MatchOutputHDCPStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No sink detected',
            '1' : 'Non-HDCP compliant sink detected',
            '2' : 'HDCP compliant sink detected'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputHDCPStatus', value, None)

    def SetOutputLineAttenuation(self, value, qualifier):

        output = {
            '1' : '2',
            '2' : '3'
        }
        if -100 <= value <= 0 and qualifier['Output'] in output:
            CmdString = 'wG6000{0}*{1}AU\r'.format(output[qualifier['Output']], round(value*10))
            self.__SetHelper('OutputLineAttenuation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLineAttenuation')

    def UpdateOutputLineAttenuation(self, value, qualifier):
        output = {
            '1' : '2',
            '2' : '3'
        }
        if qualifier['Output'] in output:
            self.__UpdateHelper('OutputLineAttenuation', 'wG6000{0}AU\r'.format(output[qualifier['Output']]) , value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLineAttenuation')

    def __MatchOutputLineAttenuation(self, match, tag):
        output = {
            '2' : '1',
            '3' : '2'
        }
        self.WriteStatus('OutputLineAttenuation', int(match.group(2).decode())/10, {'Output': output[match.group(1).decode()]})

    def SetOutputLineMute(self, value, qualifier):

        output = {
            '1' : '2',
            '2' : '3'
        }
        
        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States and qualifier['Output'] in output:
            CmdString = 'wM6000{0}*{1}AU\r'.format(output[qualifier['Output']], States[value])
            self.__SetHelper('OutputLineMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLineMute')

    def UpdateOutputLineMute(self, value, qualifier):
        output = {
            '1' : '2',
            '2' : '3'
        }
        if qualifier['Output'] in output:
            self.__UpdateHelper('OutputLineMute', 'wM6000{0}AU\r'.format(output[qualifier['Output']]) , value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLineMute')

    def __MatchOutputLineMute(self, match, tag):
        output = {
            '2' : '1',
            '3' : '2'
        }
        
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('OutputLineMute', States[match.group(2).decode()], {'Output': output[match.group(1).decode()]})

    def SetNearEndMixPC(self, value, qualifier):

        if -100 <= value <= 0:
            CmdString = 'wD1*{}GRPM\r'.format(round(value*10))
            self.__SetHelper('NearEndMixPC', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNearEndMixPC')

    def UpdateNearEndMixPC(self, value, qualifier):
        self.__UpdateHelper('NearEndMixPC', 'wD1GRPM\r', value, qualifier)

    def SetNearEndMixPCMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wD2*{}GRPM\r'.format(States[value])
            self.__SetHelper('NearEndMixPCMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNearEndMixPCMute')

    def UpdateNearEndMixPCMute(self, value, qualifier):
        self.__UpdateHelper('NearEndMixPCMute', 'wD2GRPM\r', value, qualifier)

    def SetNearEndMixProgram(self, value, qualifier):

        if -100 <= value <= 0:
            CmdString = 'wD3*{}GRPM\r'.format(round(value*10))
            self.__SetHelper('NearEndMixProgram', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNearEndMixProgram')

    def UpdateNearEndMixProgram(self, value, qualifier):
        self.__UpdateHelper('NearEndMixProgram', 'wD3GRPM\r', value, qualifier)

    def SetNearEndMixProgramMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wD4*{}GRPM\r'.format(States[value])
            self.__SetHelper('NearEndMixProgramMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNearEndMixProgramMute')

    def UpdateNearEndMixProgramMute(self, value, qualifier):
        self.__UpdateHelper('NearEndMixProgramMute', 'wD4GRPM\r', value, qualifier)

    def SetMixtoFarEndMic(self, value, qualifier):

        if -100 <= value <= 0:
            CmdString = 'wD5*{}GRPM\r'.format(round(value*10))
            self.__SetHelper('MixtoFarEndMic', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixtoFarEndMic')

    def UpdateMixtoFarEndMic(self, value, qualifier):
        self.__UpdateHelper('MixtoFarEndMic', 'wD5GRPM\r', value, qualifier)

    def SetMixtoFarEndMicMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wD6*{}GRPM\r'.format(States[value])
            self.__SetHelper('MixtoFarEndMicMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixtoFarEndMicMute')

    def UpdateMixtoFarEndMicMute(self, value, qualifier):
        self.__UpdateHelper('MixtoFarEndMicMute', 'wD6GRPM\r', value, qualifier)

    def SetMixtoFarEndProgram(self, value, qualifier):

        if -100 <= value <= 0:
            CmdString = 'wD7*{}GRPM\r'.format(round(value*10))
            self.__SetHelper('MixtoFarEndProgram', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixtoFarEndProgram')

    def UpdateMixtoFarEndProgram(self, value, qualifier):
        self.__UpdateHelper('MixtoFarEndProgram', 'wD7GRPM\r', value, qualifier)

    def SetMixtoFarEndProgramMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wD8*{}GRPM\r'.format(States[value])
            self.__SetHelper('MixtoFarEndProgramMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixtoFarEndProgramMute')

    def UpdateMixtoFarEndProgramMute(self, value, qualifier):
        self.__UpdateHelper('MixtoFarEndProgramMute', 'wD8GRPM\r', value, qualifier)

    def SetOutputUSBAttenuation(self, value, qualifier):

        if -100 <= value <= 0:
            CmdString = 'wD9*{}GRPM\r'.format(round(value*10))
            self.__SetHelper('OutputUSBAttenuation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputUSBAttenuation')

    def UpdateOutputUSBAttenuation(self, value, qualifier):
        self.__UpdateHelper('OutputUSBAttenuation', 'wD9GRPM\r', value, qualifier)

    def SetOutputUSBMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wD10*{}GRPM\r'.format(States[value])
            self.__SetHelper('OutputUSBMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputUSBMute')

    def UpdateOutputUSBMute(self, value, qualifier):
        self.__UpdateHelper('OutputUSBMute', 'wD10GRPM\r', value, qualifier)

    def __MatchGroup(self, match, tag):

        groupdict = {
            '1' : 'NearEndMixPC',
            '2' : 'NearEndMixPCMute',
            '3' : 'NearEndMixProgram',
            '4' : 'NearEndMixProgramMute',
            '5' : 'MixtoFarEndMic',
            '6' : 'MixtoFarEndMicMute',
            '7' : 'MixtoFarEndProgram',
            '8' : 'MixtoFarEndProgramMute',
            '9' : 'OutputUSBAttenuation',
            '10' : 'OutputUSBMute',
        }
        
        group = str(int(match.group(1)))
        if group in ['2', '4', '6', '8', '10']:
            GroupMuteStateNames = {
                    '1' : 'On',
                    '0' : 'Off'
            }
            value = match.group(2).decode()[-1]
            self.WriteStatus(groupdict[group], GroupMuteStateNames[value], None)
        else: 
            value = int(match.group(2))/10
            self.WriteStatus(groupdict[group], value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetCmdString = '{0}.'.format(int(value))
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetScreenSaverMode(self, value, qualifier):

        ValueStateValues = {
            'Extron Logo' : '0', 
            'Black or Selected User Image' : '1', 
            'Blue with On Screen Display Bug' : '2'
        }

        if value in ValueStateValues:
            ScreenSaverModeCmdString = 'wM1*{0}SSAV\r'.format(ValueStateValues[value])
            self.__SetHelper('ScreenSaverMode', ScreenSaverModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenSaverMode')

    def UpdateScreenSaverMode(self, value, qualifier):

        ScreenSaverModeCmdString = 'wM1SSAV\r'
        self.__UpdateHelper('ScreenSaverMode', ScreenSaverModeCmdString, value, qualifier)

    def __MatchScreenSaverMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Extron Logo', 
            '1' : 'Black or Selected User Image', 
            '2' : 'Blue with On Screen Display Bug'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenSaverMode', value, None)

    def UpdateScreenSaverStatus(self, value, qualifier):

        ScreenSaverStatusCmdString = 'wS1SSAV\r'
        self.__UpdateHelper('ScreenSaverStatus', ScreenSaverStatusCmdString, value, qualifier)

    def __MatchScreenSaverStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenSaverStatus', value, None)

    def SetUSBHIDHook(self, value, qualifier):

        ValueStateValues = {
            'On': 'H1*0',
            'Off': 'H1*1',
            'Reject': 'E1',
            'Flash': 'F1'
            }

        if value in ValueStateValues:
            USBHIDHookCmdString = 'w{}UPHN\r'.format(ValueStateValues[value])
            if value not in ['Reject', 'Flash']:
                self.__SetHelper('USBHIDHook', USBHIDHookCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBHIDHook')

    def UpdateUSBHIDHook(self, value, qualifier):

        USBHIDHookCmdString = 'wH1UPHN\r'
        self.__UpdateHelper('USBHIDHook', USBHIDHookCmdString, value, qualifier)

    def __MatchUSBHIDHook(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBHIDHook', value, None)

    def UpdateUSBHIDHookLEDStatus(self, value, qualifier):

        USBHIDHookLEDStatusCmdString = 'wK1UPHN\r'
        self.__UpdateHelper('USBHIDHookLEDStatus', USBHIDHookLEDStatusCmdString, value, qualifier)

    def __MatchUSBHIDHookLEDStatus(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBHIDHookLEDStatus', value, None)

    def UpdateUSBHIDMuteLEDStatus(self, value, qualifier):

        USBHIDMuteLEDStatusCmdString = 'wM1UPHN\r'
        self.__UpdateHelper('USBHIDMuteLEDStatus', USBHIDMuteLEDStatusCmdString, value, qualifier)

    def __MatchUSBHIDMuteLEDStatus(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBHIDMuteLEDStatus', value, None)

    def UpdateUSBHIDRingLEDStatus(self, value, qualifier):

        USBHIDRingLEDStatusCmdString = 'wG1UPHN\r'
        self.__UpdateHelper('USBHIDRingLEDStatus', USBHIDRingLEDStatusCmdString, value, qualifier)

    def __MatchUSBHIDRingLEDStatus(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBHIDRingLEDStatus', value, None)

    def UpdateVideoSendStatus(self, value, qualifier):

        self.UpdateUSBHostStatus(value, qualifier)

    def UpdateUSBHostStatus(self, value, qualifier):

        USBHostStatusCmdString = '35I\r'
        self.__UpdateHelper('USBHostStatus', USBHostStatusCmdString, value, qualifier)

    def __MatchUSBHostStatus(self, match, tag):

        UsbStateValues = {
            '0' : 'Not Present', 
            '1' : 'Present',
        }

        VideoSendStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = UsbStateValues[match.group(1).decode()]
        self.WriteStatus('USBHostStatus', value, None)

        value = VideoSendStateValues[match.group(2).decode()]
        self.WriteStatus('VideoSendStatus', value, None)

    def UpdateUSBStreamingFormat(self, value, qualifier):

        USBStreamingFormatCmdString = 'w1OTYP\r'
        self.__UpdateHelper('USBStreamingFormat', USBStreamingFormatCmdString, value, qualifier)

    def __MatchUSBStreamingFormat(self, match, tag):

        ValueStateValues = {
            '0' : 'No Active Stream',
            '1' : 'MJPEG', 
            '2' : 'YUY2',
            '3' : 'NV12'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBStreamingFormat', value, None)

    def SetUSBTerminalType(self, value, qualifier):

        ValueStateValues = {
            'No USB enumeration' : '0',
            'Default' : '7', 
            'Echo Cancelling Speakerphone and Webcam' : '8',
            'Non-Echo Cancelling Speakerphone' : '9',
            'Echo Cancelling Speakerphone' : '10',
            'Webcam' : '11'
        }

        if value in ValueStateValues:
            USBTerminalTypeCmdString = 'wC{0}USBC\r'.format(ValueStateValues[value])
            self.__SetHelper('USBTerminalType', USBTerminalTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBTerminalType')

    def UpdateUSBTerminalType(self, value, qualifier):

        USBTerminalTypeCmdString = 'wCUSBC\r'
        self.__UpdateHelper('USBTerminalType', USBTerminalTypeCmdString, value, qualifier)

    def __MatchUSBTerminalType(self, match, tag):

        ValueStateValues = {
            '0' : 'No USB enumeration',
            '7' : 'Default', 
            '8' : 'Echo Cancelling Speakerphone and Webcam',
            '9' : 'Non-Echo Cancelling Speakerphone',
            '10' : 'Echo Cancelling Speakerphone',
            '11' : 'Webcam'
        }

        value = ValueStateValues[str(int(match.group(1).decode()))]
        self.WriteStatus('USBTerminalType', value, None)

    def UpdateVerticalRefreshRate(self, value, qualifier):

        VerticalRefreshRateCmdString = 'I'
        self.__UpdateHelper('VerticalRefreshRate', VerticalRefreshRateCmdString, value, qualifier)
            
    def __MatchVerticalRefreshRate(self, match, tag):
        
        ValueStateValues = {
            '1' : 'Mute Video to Black', 
            '2' : 'Mute Sync and Video', 
            '0' : 'Unmute Video/Sync'
        }
        
        self.WriteStatus('VideoMute', ValueStateValues[match.group(1).decode()], {'Output': 'USB'})
        self.WriteStatus('VideoMute', ValueStateValues[match.group(2).decode()], {'Output': 'HDMI Loop'})
        self.WriteStatus('VerticalRefreshRate', float(match.group(3).decode()), None)
        
    def SetVideoMute(self, value, qualifier):

        OutputStates = {
            'USB' : '1', 
            'HDMI Loop' : '2'
        }

        ValueStateValues = {
            'Mute Video to Black' : '1B', 
            'Mute Sync and Video' : '2B', 
            'Unmute Video/Sync' : '0B'
        }

        if value in ValueStateValues and qualifier['Output'] in OutputStates:
            if qualifier['Output'] != 'USB' or value != 'Mute Sync and Video':
                VideoMuteCmdString = '{0}*{1}'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
                self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVideoMute')
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def __MatchVideoMute(self, match, tag):

        OutputStates = {
            '1' : 'USB',
            '2' : 'HDMI Loop'
        }

        ValueStateValues = {
            '1' : 'Mute Video to Black', 
            '2' : 'Mute Sync and Video', 
            '0' : 'Unmute Video/Sync'
        }

        if match.group(2).decode() == '*':
            group = OutputStates[match.group(1).decode()]
            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('VideoMute', value, {'Output': group})
        else:
            value1 = ValueStateValues[match.group(1).decode()]
            value2 = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('VideoMute', value1, {'Output': 'USB'})
            self.WriteStatus('VideoMute', value2, {'Output': 'HDMI Loop'})

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'Active', 
            '0' : 'Not Active'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InputSignalStatus', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled:
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
        elif self.EchoDisabled:
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
            '01' : 'Invalid Input Number',
            '10' : 'Invalid Command',
            '11' : 'Invalid Preset Number',
            '12' : 'Invalid Output or Port Number',
            '13' : 'Invalid Parameter',
            '14' : 'Invalid Command for this Configuration',
            '17' : 'Invalid Command for this Signal Type',
            '22' : 'Busy',
            '24' : 'Privilege Violation',
            '25' : 'Device Not Present',
            '26' : 'Maximum Number of Connections Exceeded',
            '28' : 'Bad Filename or File Not Found',
            '33' : 'Bad File Type or Size'
        }
         
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES: 
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: E'+ value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True
        self.EchoDisabled = True

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
