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
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': {'Parameters':['Group'], 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AutoMemory': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'DigitalInputMode': {'Parameters':['Input'], 'Status': {}},
            'DigitalInputStatus': {'Parameters':['Input'], 'Status': {}},
            'DigitalOutputMode': {'Parameters':['Output'], 'Status': {}},
            'HDCPAuthentication': { 'Status': {}},
            'HDCPMode': { 'Status': {}},
            'HDCPNotification': { 'Status': {}},
            'HDMIInputEDID': { 'Status': {}},
            'HDMILoopFormat': { 'Status': {}},

            'InputHDMIGain': {'Parameters':['L/R'], 'Status': {}},
            'InputHDMIMute': {'Parameters':['L/R'], 'Status': {}},
            'InputLineInGain': {'Parameters':['L/R'], 'Status': {}},
            'InputLineInMute': {'Parameters':['L/R'], 'Status': {}},
            'InputMicLineGain': { 'Status': {}},
            'InputMicLineMute': { 'Status': {}},
            'InputPreMixerHDMIGain': { 'Status': {}},
            'InputPreMixerHDMIMute': { 'Status': {}},
            'InputPreMixerLineInGain': { 'Status': {}},
            'InputPreMixerLineInMute': { 'Status': {}},
            'InputPreMixerUSBCommunicationsGain': { 'Status': {}},
            'InputPreMixerUSBCommunicationsMute': { 'Status': {}},
            'InputPreMixerUSBPlaybackGain': { 'Status': {}},
            'InputPreMixerUSBPlaybackMute': { 'Status': {}},
            'InputUSBCommunicationsGain': {'Parameters':['L/R'], 'Status': {}},
            'InputUSBCommunicationsMute': {'Parameters':['L/R'], 'Status': {}},
            'InputUSBPlaybackGain': {'Parameters':['L/R'], 'Status': {}},
            'InputUSBPlaybackMute': {'Parameters':['L/R'], 'Status': {}},
            'OutputAuxAttenuation': { 'Status': {}},
            'OutputAuxMute': { 'Status': {}},
            'OutputLineAttenuation': { 'Status': {}},
            'OutputLineMute': { 'Status': {}},
            'OutputReferenceAttenuation': { 'Status': {}},
            'OutputReferenceMute': { 'Status': {}},
            'OutputUSBAttenuation': { 'Status': {}},
            'OutputUSBMute': { 'Status': {}},

            'OverscanMode': { 'Status': {}},
            'Preset': {'Parameters':['Preset'], 'Status': {}},
            'ScreenSaverMode': { 'Status': {}},
            'ScreenSaverStatus': { 'Status': {}},
            'USBHostStatus': { 'Status': {}},
            'USBStreamingFormat': { 'Status': {}},
            'USBTerminalType': { 'Status': {}},
            'VideoMute': {'Parameters':['Output'], 'Status': {}},
            'VideoSendStatus': { 'Status': {}},
            'VideoSignalPresence': { 'Status': {}},
            'Volume': {'Parameters':['Group'], 'Status': {}},
        }       

        self.VerboseDisabled = True
        self.EchoDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Aspr1\*([12])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'GrpmD(2|4|6|8|10)\*([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Amem1\*([01])\r\n'), self.__MatchAutoMemory, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Frz([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'Gpit([12])\*(10|[0-9])\r\n'), self.__MatchDigitalInputMode, None)
            self.AddMatchString(re.compile(b'Gpi([12])\*([01])\r\n'), self.__MatchDigitalInputStatus, None)
            self.AddMatchString(re.compile(b'Gpot([12])\*([0-5])\r\n'), self.__MatchDigitalOutputMode, None)
            self.AddMatchString(re.compile(b'HdcpE1\*([01])\r\n'), self.__MatchHDCPAuthentication, None)
            self.AddMatchString(re.compile(b'HdcpS([0-4])\r\n'), self.__MatchHDCPMode, None)
            self.AddMatchString(re.compile(b'HdcpN([01])\r\n'), self.__MatchHDCPNotification, None)
            self.AddMatchString(re.compile(b'EdidA1\*([1-5][0-9])\r\n'), self.__MatchHDMIInputEDID, None)
            self.AddMatchString(re.compile(b'Vtpo2\*([0-7])\r\n'), self.__MatchHDMILoopFormat, None)
            self.AddMatchString(re.compile(b'DsG30000\*(-?\d+)\r\n'), self.__MatchInputUSBPlaybackGain, 'Left')
            self.AddMatchString(re.compile(b'DsM30000\*([01])\r\n'), self.__MatchInputUSBPlaybackMute, 'Left')
            self.AddMatchString(re.compile(b'DsG30001\*(-?\d+)\r\n'), self.__MatchInputUSBPlaybackGain, 'Right')
            self.AddMatchString(re.compile(b'DsM30001\*([01])\r\n'), self.__MatchInputUSBPlaybackMute, 'Right')
            self.AddMatchString(re.compile(b'DsG30002\*(-?\d+)\r\n'), self.__MatchInputHDMIGain, 'Left')
            self.AddMatchString(re.compile(b'DsM30002\*([01])\r\n'), self.__MatchInputHDMIMute, 'Left')
            self.AddMatchString(re.compile(b'DsG30003\*(-?\d+)\r\n'), self.__MatchInputHDMIGain, 'Right')
            self.AddMatchString(re.compile(b'DsM30003\*([01])\r\n'), self.__MatchInputHDMIMute, 'Right')
            self.AddMatchString(re.compile(b'DsG30004\*(-?\d+)\r\n'), self.__MatchInputLineInGain, 'Left')
            self.AddMatchString(re.compile(b'DsM30004\*([01])\r\n'), self.__MatchInputLineInMute, 'Left')
            self.AddMatchString(re.compile(b'DsG30005\*(-?\d+)\r\n'), self.__MatchInputLineInGain, 'Right')
            self.AddMatchString(re.compile(b'DsM30005\*([01])\r\n'), self.__MatchInputLineInMute, 'Right')
            self.AddMatchString(re.compile(b'DsG30006\*(-?\d+)\r\n'), self.__MatchInputUSBCommunicationsGain, 'Left')
            self.AddMatchString(re.compile(b'DsM30006\*([01])\r\n'), self.__MatchInputUSBCommunicationsMute, 'Left')
            self.AddMatchString(re.compile(b'DsG30007\*(-?\d+)\r\n'), self.__MatchInputUSBCommunicationsGain, 'Right')
            self.AddMatchString(re.compile(b'DsM30007\*([01])\r\n'), self.__MatchInputUSBCommunicationsMute, 'Right')
            self.AddMatchString(re.compile(b'DsG40000\*(-?\d+)\r\n'), self.__MatchInputMicLineGain, None)
            self.AddMatchString(re.compile(b'DsM40000\*([01])\r\n'), self.__MatchInputMicLineMute, None)
            self.AddMatchString(re.compile(b'DsG30100\*(-?\d+)\r\n'), self.__MatchInputPreMixerUSBPlaybackGain, None)
            self.AddMatchString(re.compile(b'DsM30100\*([01])\r\n'), self.__MatchInputPreMixerUSBPlaybackMute, None)
            self.AddMatchString(re.compile(b'DsG30102\*(-?\d+)\r\n'), self.__MatchInputPreMixerHDMIGain, None)
            self.AddMatchString(re.compile(b'DsM30102\*([01])\r\n'), self.__MatchInputPreMixerHDMIMute, None)
            self.AddMatchString(re.compile(b'DsG30104\*(-?\d+)\r\n'), self.__MatchInputPreMixerLineInGain, None)
            self.AddMatchString(re.compile(b'DsM30104\*([01])\r\n'), self.__MatchInputPreMixerLineInMute, None)
            self.AddMatchString(re.compile(b'DsG30106\*(-?\d+)\r\n'), self.__MatchInputPreMixerUSBCommunicationsGain, None)
            self.AddMatchString(re.compile(b'DsM30106\*([01])\r\n'), self.__MatchInputPreMixerUSBCommunicationsMute, None)
            self.AddMatchString(re.compile(b'DsG60000\*(-?\d+)\r\n'), self.__MatchOutputUSBAttenuation, None)
            self.AddMatchString(re.compile(b'DsM60000\*([01])\r\n'), self.__MatchOutputUSBMute, None)
            self.AddMatchString(re.compile(b'DsG60002\*(-?\d+)\r\n'), self.__MatchOutputLineAttenuation, None)
            self.AddMatchString(re.compile(b'DsM60002\*([01])\r\n'), self.__MatchOutputLineMute, None)
            self.AddMatchString(re.compile(b'DsG60004\*(-?\d+)\r\n'), self.__MatchOutputReferenceAttenuation, None)
            self.AddMatchString(re.compile(b'DsM60004\*([01])\r\n'), self.__MatchOutputReferenceMute, None)
            self.AddMatchString(re.compile(b'DsG60005\*(-?\d+)\r\n'), self.__MatchOutputAuxAttenuation, None)
            self.AddMatchString(re.compile(b'DsM60005\*([01])\r\n'), self.__MatchOutputAuxMute, None)

            self.AddMatchString(re.compile(b'Oscn1\*([0-2])\r\n'), self.__MatchOverscanMode, None)
            self.AddMatchString(re.compile(b'SsavM([0-2])\r\n'), self.__MatchScreenSaverMode, None)
            self.AddMatchString(re.compile(b'SsavS([01])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(re.compile(b'Host([0-2]) VSend([01]) CommOut[01] CommIn[01] pcPlaybackIn[01] USBStd[0-3]\r\n'), self.__MatchUSBHostStatus, None)
            self.AddMatchString(re.compile(b'Otyp1\*([12])\r\n'), self.__MatchUSBStreamingFormat, None)
            self.AddMatchString(re.compile(b'UsbcC([12])\r\n'), self.__MatchUSBTerminalType, None)
            self.AddMatchString(re.compile(b'Vmt([0-2])([ *])([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'In00 ([01])\r\n'), self.__MatchVideoSignalPresence, None)
            self.AddMatchString(re.compile(b'GrpmD([13579])\*(0|-\d{1,4})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)
            
    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        
    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill' : 'w1*1ASPR\r', 
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

    def SetAudioMute(self, value, qualifier):

        GroupStates = {
            'Program'            : '2', 
            'Mic to Far End'     : '4', 
            'Program to Far End' : '6', 
            'Far End to Ref'     : '8', 
            'Mic to Aux'         : '10'
        }

        ValueStateValues = {
            'On' : 1, 
            'Off' : 0
        }

        if value in ValueStateValues and qualifier['Group'] in GroupStates:
            AudioMuteCmdString = 'wD{0}*{1}GRPM\r'.format(GroupStates[qualifier['Group']], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        GroupStates = {
            'Program'            : '2', 
            'Mic to Far End'     : '4', 
            'Program to Far End' : '6', 
            'Far End to Ref'     : '8', 
            'Mic to Aux'         : '10'
        }

        if qualifier['Group'] in GroupStates:
            AudioMuteCmdString = 'wD{0}GRPM\r'.format(GroupStates[qualifier['Group']])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        GroupStates = {
            '2'  : 'Program', 
            '4'  : 'Mic to Far End', 
            '6'  : 'Program to Far End', 
            '8'  : 'Far End to Ref', 
            '10' : 'Mic to Aux'
        }

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        qualifier = {}
        qualifier['Group'] = GroupStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

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

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On' : '1X', 
            'Off' : '0X'
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
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On' : '1F', 
            'Off' : '0F'
        }

        if value in ValueStateValues:
            FreezeCmdString = ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'F'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetDigitalInputMode(self, value, qualifier):

        ValueStateValues = {
            'Default Off' : '0', 
            'Push to Mute' : '1', 
            'Push to Talk' : '2', 
            'Mic Mute 1' : '3', 
            'Mic Mute 2' : '4', 
            'Mic Mute 3' : '5', 
            'Mic Mute 4' : '6', 
            'Inc Group Master 1' : '7', 
            'Dec Group Master 1' : '8', 
            'Preset Toggle 1' : '9', 
            'Preset Toggle 2' : '10'
        }

        if value in ValueStateValues and qualifier['Input'] in ['1', '2']:
            DigitalInputModeCmdString = 'w{0}*{1}GPIT\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('DigitalInputMode', DigitalInputModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalInputMode')

    def UpdateDigitalInputMode(self, value, qualifier):

        if qualifier['Input'] in ['1', '2']:
            DigitalInputModeCmdString = 'w{0}GPIT\r'.format(qualifier['Input'])
            self.__UpdateHelper('DigitalInputMode', DigitalInputModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDigitalInputMode')

    def __MatchDigitalInputMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Default Off', 
            '1' : 'Push to Mute', 
            '2' : 'Push to Talk', 
            '3' : 'Mic Mute 1', 
            '4' : 'Mic Mute 2', 
            '5' : 'Mic Mute 3', 
            '6' : 'Mic Mute 4', 
            '7' : 'Inc Group Master 1', 
            '8' : 'Dec Group Master 1', 
            '9' : 'Preset Toggle 1', 
            '10' : 'Preset Toggle 2'
        }

        qualifier = {'Input' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DigitalInputMode', value, qualifier)

    def UpdateDigitalInputStatus(self, value, qualifier):

        if qualifier['Input'] in ['1', '2']:
            DigitalInputStatusCmdString = 'w{0}GPI\r'.format(qualifier['Input'])
            self.__UpdateHelper('DigitalInputStatus', DigitalInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDigitalInputStatus')

    def __MatchDigitalInputStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'High', 
            '0' : 'Low'
        }

        qualifier = {'Input' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DigitalInputStatus', value, qualifier)

    def SetDigitalOutputMode(self, value, qualifier):

        ValueStateValues = {
            'Output High' : '0', 
            'Output Low' : '1', 
            'Follow Mute' : '2', 
            'Follow Mute Inverted' : '3', 
            'Blink, Follow Input 1' : '4', 
            'Blink, Follow Input 2' : '5'
        }

        if value in ValueStateValues and qualifier['Output'] in ['1', '2']:
            DigitalOutputModeCmdString = 'w{0}*{1}GPOT\r'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('DigitalOutputMode', DigitalOutputModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalOutputMode')

    def UpdateDigitalOutputMode(self, value, qualifier):

        if qualifier['Output'] in ['1', '2']:
            DigitalOutputModeCmdString = 'w{0}GPOT\r'.format(qualifier['Output'])
            self.__UpdateHelper('DigitalOutputMode', DigitalOutputModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDigitalOutputMode')

    def __MatchDigitalOutputMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Output High', 
            '1' : 'Output Low', 
            '2' : 'Follow Mute', 
            '3' : 'Follow Mute Inverted', 
            '4' : 'Blink, Follow Input 1', 
            '5' : 'Blink, Follow Input 2'
        }

        qualifier = {}
        qualifier['Output'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DigitalOutputMode', value, qualifier)

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
            'Mode 1' : 'wS0HDCP\r', 
            'Mode 2' : 'wS1HDCP\r', 
            'Mode 3' : 'wS2HDCP\r', 
            'Mode 4' : 'wS3HDCP\r'
        }

        if value in ValueStateValues:
            HDCPModeCmdString = ValueStateValues[value]
            self.__SetHelper('HDCPMode', HDCPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPMode')

    def UpdateHDCPMode(self, value, qualifier):

        HDCPModeCmdString = 'wSHDCP\r'
        self.__UpdateHelper('HDCPMode', HDCPModeCmdString, value, qualifier)

    def __MatchHDCPMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Mode 1', 
            '1' : 'Mode 2', 
            '2' : 'Mode 3', 
            '3' : 'Mode 4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPMode', value, None)

    def SetHDCPNotification(self, value, qualifier):

        ValueStateValues = {
            'On' : 'wN1HDCP\r', 
            'Off' : 'wN0HDCP\r'
        }

        if value in ValueStateValues:
            HDCPNotificationCmdString = ValueStateValues[value]
            self.__SetHelper('HDCPNotification', HDCPNotificationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPNotification')

    def UpdateHDCPNotification(self, value, qualifier):

        HDCPNotificationCmdString = 'wNHDCP\r'
        self.__UpdateHelper('HDCPNotification', HDCPNotificationCmdString, value, qualifier)

    def __MatchHDCPNotification(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPNotification', value, None)

    def SetHDMIInputEDID(self, value, qualifier):

        ValueStateValues = {
            '640x480 60Hz'      : '10', '800x600 60Hz'      : '11', '1024x768 60Hz'     : '12', 
            '1280x768 60Hz'     : '13', '1280x800 60Hz'     : '14', '1280x1024 60Hz'    : '15', 
            '1360x768 60Hz'     : '16', '1366x768 60Hz'     : '17', '1440x900 60Hz'     : '18', 
            '1400x1050 60Hz'    : '19', '1600x900 60Hz'     : '20', '1680x1050 60Hz'    : '21', 
            '1600x1200 60Hz'    : '22', '1920x1200 60Hz'    : '23', '480p 59.94Hz'      : '24', 
            '480p 60Hz'         : '25', '576p 50Hz'         : '26', '720p 23.98Hz'      : '27', 
            '720p 24Hz'         : '28', '720p 25Hz'         : '29', '720p 29.97Hz'      : '30', 
            '720p 30Hz'         : '31', '720p 50Hz'         : '32', '720p 59.94Hz'      : '33', 
            '720p 60Hz'         : '34', '1080i 50Hz'        : '35', '1080i 59.94Hz'     : '36', 
            '1080i 60Hz'        : '37', '1080p 23.98Hz'     : '38', '1080p 24Hz'        : '39', 
            '1080p 25Hz'        : '40', '1080p 29.97Hz'     : '41', '1080p 30Hz'        : '42', 
            '1080p 50Hz'        : '43', '1080p 59.94Hz'     : '44', '1080p 60Hz'        : '45', 
            '2048x1080 23.98Hz' : '46', '2048x1080 24Hz'    : '47', '2048x1080 25Hz'    : '48', 
            '2048x1080 29.97Hz' : '49', '2048x1080 30Hz'    : '50', '2048x1080 50Hz'    : '51', 
            '2048x1080 59.94Hz' : '52', '2048x1080 60Hz'    : '53'
        }

        if value in ValueStateValues:
            HDMIInputEDIDCmdString = 'wA1*{0}EDID\r'.format(ValueStateValues[value])
            self.__SetHelper('HDMIInputEDID', HDMIInputEDIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIInputEDID')

    def UpdateHDMIInputEDID(self, value, qualifier):

        HDMIInputEDIDCmdString = 'wA1EDID\r'
        self.__UpdateHelper('HDMIInputEDID', HDMIInputEDIDCmdString, value, qualifier)

    def __MatchHDMIInputEDID(self, match, tag):

        ValueStateValues = {
            '10' : '640x480 60Hz',      '11' : '800x600 60Hz',      '12' : '1024x768 60Hz', 
            '13' : '1280x768 60Hz',     '14' : '1280x800 60Hz',     '15' : '1280x1024 60Hz', 
            '16' : '1360x768 60Hz',     '17' : '1366x768 60Hz',     '18' : '1440x900 60Hz', 
            '19' : '1400x1050 60Hz',    '20' : '1600x900 60Hz',     '21' : '1680x1050 60Hz', 
            '22' : '1600x1200 60Hz',    '23' : '1920x1200 60Hz',    '24' : '480p 59.94Hz', 
            '25' : '480p 60Hz',         '26' : '576p 50Hz',         '27' : '720p 23.98Hz', 
            '28' : '720p 24Hz',         '29' : '720p 25Hz',         '30' : '720p 29.97Hz', 
            '31' : '720p 30Hz',         '32' : '720p 50Hz',         '33' : '720p 59.94Hz', 
            '34' : '720p 60Hz',         '35' : '1080i 50Hz',        '36' : '1080i 59.94Hz', 
            '37' : '1080i 60Hz',        '38' : '1080p 23.98Hz',     '39' : '1080p 24Hz', 
            '40' : '1080p 25Hz',        '41' : '1080p 29.97Hz',     '42' : '1080p 30Hz', 
            '43' : '1080p 50Hz',        '44' : '1080p 59.94Hz',     '45' : '1080p 60Hz', 
            '46' : '2048x1080 23.98Hz', '47' : '2048x1080 24Hz',    '48' : '2048x1080 25Hz', 
            '49' : '2048x1080 29.97Hz', '50' : '2048x1080 30Hz',    '51' : '2048x1080 50Hz', 
            '52' : '2048x1080 59.94Hz', '53' : '2048x1080 60Hz'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDMIInputEDID', value, None)

    def SetHDMILoopFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto' : '0', 
            'DVI RGB 444' : '1', 
            'RGB 444 Full' : '2', 
            'RGB 444 Limited' : '3', 
            'YUV 444 Full' : '4', 
            'YUV 444 Limited' : '5', 
            'YUV 422 Full' : '6', 
            'YUV 422 Limited' : '7'
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
            '7' : 'YUV 422 Limited'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDMILoopFormat', value, None)

    def SetInputHDMIGain(self, value, qualifier):

        LR = {
            'Left'  :'2',
            'Right' :'3'
        }

        if -18 <= value <= 24 and qualifier['L/R'] in LR:
            CmdString = 'wG3000{0}*{1}AU\r'.format(LR[qualifier['L/R']], round(value*10))
            self.__SetHelper('InputHDMIGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputHDMIGain')

    def UpdateInputHDMIGain(self, value, qualifier):
        LR = {
            'Left'  : '2',
            'Right' : '3'
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
            'Left'  :'2',
            'Right' :'3'
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
            'Left'  : '2',
            'Right' : '3'
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

        LR = {
            'Left'  : '4',
            'Right' : '5'
        }

        if -18 <= value <= 24 and qualifier['L/R'] in LR:
            CmdString = 'wG3000{0}*{1}AU\r'.format(LR[qualifier['L/R']], round(value*10))
            self.__SetHelper('InputLineInGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLineInGain')

    def UpdateInputLineInGain(self, value, qualifier):
        LR = {
            'Left'  : '4',
            'Right' : '5'
        }

        if qualifier['L/R'] in LR:
            CmdString = 'wG3000{}AU\r'.format(LR[qualifier['L/R']])
            self.__UpdateHelper('InputLineInGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLineInGain')

    def __MatchInputLineInGain(self, match, tag):
        self.WriteStatus('InputLineInGain',  int(match.group(1).decode())/10 , {'L/R':tag} )

    def SetInputLineInMute(self, value, qualifier):

        LR = {
            'Left'  : '4',
            'Right' : '5'
        }

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States and qualifier['L/R'] in LR:
            CmdString = 'wM3000{0}*{1}AU\r'.format(LR[qualifier['L/R']], States[value])
            self.__SetHelper('InputLineInMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLineInMute')

    def UpdateInputLineInMute(self, value, qualifier):
        LR = {
            'Left'  : '4',
            'Right' : '5'
        }

        if qualifier['L/R'] in LR:
            CmdString = 'wM3000{}AU\r'.format(LR[qualifier['L/R']])
            self.__UpdateHelper('InputLineInMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLineInMute')

    def __MatchInputLineInMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputLineInMute', States[match.group(1).decode()], {'L/R':tag})

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

    def SetInputPreMixerHDMIGain(self, value, qualifier):

        if -100 <= value <= 12:
            CmdString = 'wG30102*{0}AU\rwG30103*{0}AU\r'.format(round(value*10))
            self.__SetHelper('InputPreMixerHDMIGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerHDMIGain')

    def UpdateInputPreMixerHDMIGain(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerHDMIGain', 'wG30102AU\r' , value, qualifier)

    def __MatchInputPreMixerHDMIGain(self, match, tag):
        self.WriteStatus('InputPreMixerHDMIGain',  int(match.group(1).decode())/10 , None)

    def SetInputPreMixerHDMIMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM30102*{0}AU\rwM30103*{0}AU\r'.format(States[value])
            self.__SetHelper('InputPreMixerHDMIMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerHDMIMute')

    def UpdateInputPreMixerHDMIMute(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerHDMIMute', 'wM30102AU\r' , value, qualifier)

    def __MatchInputPreMixerHDMIMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputPreMixerHDMIMute', States[match.group(1).decode()], None)

    def SetInputPreMixerLineInGain(self, value, qualifier):

        if -100 <= value <= 12:
            CmdString = 'wG30104*{0}AU\rwG30105*{0}AU\r'.format(round(value*10))
            self.__SetHelper('InputPreMixerLineInGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerLineInGain')

    def UpdateInputPreMixerLineInGain(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerLineInGain', 'wG30104AU\r' , value, qualifier)

    def __MatchInputPreMixerLineInGain(self, match, tag):
        self.WriteStatus('InputPreMixerLineInGain',  int(match.group(1).decode())/10 , None)

    def SetInputPreMixerLineInMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM30104*{0}AU\rwM30105*{0}AU\r'.format(States[value])
            self.__SetHelper('InputPreMixerLineInMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerLineInMute')

    def UpdateInputPreMixerLineInMute(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerLineInMute', 'wM30104AU\r' , value, qualifier)

    def __MatchInputPreMixerLineInMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputPreMixerLineInMute',  States[match.group(1).decode()] , None)

    def SetInputPreMixerUSBCommunicationsGain(self, value, qualifier):

        if -100 <= value <= 12:
            CmdString = 'wG30106*{0}AU\rwG30107*{0}AU\r'.format(round(value*10))
            self.__SetHelper('InputPreMixerUSBCommunicationsGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerUSBCommunicationsGain')

    def UpdateInputPreMixerUSBCommunicationsGain(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerUSBCommunicationsGain', 'wG30106AU\r' , value, qualifier)

    def __MatchInputPreMixerUSBCommunicationsGain(self, match, tag):
        self.WriteStatus('InputPreMixerUSBCommunicationsGain', int(match.group(1).decode())/10, None)

    def SetInputPreMixerUSBCommunicationsMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM30106*{0}AU\rwM30107*{0}AU\r'.format(States[value])
            self.__SetHelper('InputPreMixerUSBCommunicationsMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerUSBCommunicationsMute')

    def UpdateInputPreMixerUSBCommunicationsMute(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerUSBCommunicationsMute', 'wM30106AU\r' , value, qualifier)

    def __MatchInputPreMixerUSBCommunicationsMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputPreMixerUSBCommunicationsMute',  States[match.group(1).decode()] , None)

    def SetInputPreMixerUSBPlaybackGain(self, value, qualifier):

        if -100 <= value <= 12:
            CmdString = 'wG30100*{0}AU\rwG30101*{0}AU\r'.format(round(value*10))
            self.__SetHelper('InputPreMixerUSBPlaybackGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerUSBPlaybackGain')

    def UpdateInputPreMixerUSBPlaybackGain(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerUSBPlaybackGain', 'wG30100AU\r' , value, qualifier)

    def __MatchInputPreMixerUSBPlaybackGain(self, match, tag):
        self.WriteStatus('InputPreMixerUSBPlaybackGain',  int(match.group(1).decode())/10 , None)

    def SetInputPreMixerUSBPlaybackMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM30100*{0}AU\rwM30101*{0}AU\r'.format(States[value])
            self.__SetHelper('InputPreMixerUSBPlaybackMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPreMixerUSBPlaybackMute')

    def UpdateInputPreMixerUSBPlaybackMute(self, value, qualifier):
        self.__UpdateHelper('InputPreMixerUSBPlaybackMute', 'wM30100AU\r' , value, qualifier)

    def __MatchInputPreMixerUSBPlaybackMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputPreMixerUSBPlaybackMute',  States[match.group(1).decode()] , None)

    def SetInputUSBCommunicationsGain(self, value, qualifier):

        LR = {
            'Left'  : '6',
            'Right' : '7'
        }

        if -100 <= value <= 0 and qualifier['L/R'] in LR:
            CmdString = 'wG3000{0}*{1}AU\r'.format(LR[qualifier['L/R']], round(value*10))
            self.__SetHelper('InputUSBCommunicationsGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputUSBCommunicationsGain')

    def UpdateInputUSBCommunicationsGain(self, value, qualifier):
        LR = {
            'Left'  : '6',
            'Right' : '7'
        }

        if qualifier['L/R'] in LR:
            CmdString = 'wG3000{}AU\r'.format(LR[qualifier['L/R']])
            self.__UpdateHelper('InputUSBCommunicationsGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputUSBCommunicationsGain')

    def __MatchInputUSBCommunicationsGain(self, match, tag):
        self.WriteStatus('InputUSBCommunicationsGain',  int(match.group(1).decode())/10 , {'L/R':tag} )

    def SetInputUSBCommunicationsMute(self, value, qualifier):

        LR = {
            'Left'  : '6',
            'Right' : '7'
        }

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States and qualifier['L/R'] in LR:
            CmdString = 'wM3000{0}*{1}AU\r'.format(LR[qualifier['L/R']], States[value])
            self.__SetHelper('InputUSBCommunicationsMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputUSBCommunicationsMute')

    def UpdateInputUSBCommunicationsMute(self, value, qualifier):
        LR = {
            'Left'  : '6',
            'Right' : '7'
        }

        if qualifier['L/R'] in LR:
            CmdString = 'wM3000{}AU\r'.format(LR[qualifier['L/R']])
            self.__UpdateHelper('InputUSBCommunicationsMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputUSBCommunicationsMute')

    def __MatchInputUSBCommunicationsMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputUSBCommunicationsMute',  States[match.group(1).decode()] , {'L/R':tag} )

    def SetInputUSBPlaybackGain(self, value, qualifier):

        LR = {
            'Left'  : '0',
            'Right' : '1'
        }


        if -100 <= value <= 0 and qualifier['L/R'] in LR:
            CmdString = 'wG3000{0}*{1}AU\r'.format(LR[qualifier['L/R']], round(value*10))
            self.__SetHelper('InputUSBPlaybackGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputUSBPlaybackGain')

    def UpdateInputUSBPlaybackGain(self, value, qualifier):
        LR = {
          'Left':'0',
          'Right':'1'
        }

        if qualifier['L/R'] in LR:
            CmdString = 'wG3000{}AU\r'.format(LR[qualifier['L/R']])
            self.__UpdateHelper('InputUSBPlaybackGain', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputUSBPlaybackGain')

    def __MatchInputUSBPlaybackGain(self, match, tag):
        self.WriteStatus('InputUSBPlaybackGain',  int(match.group(1).decode())/10 , {'L/R':tag} )

    def SetInputUSBPlaybackMute(self, value, qualifier):

        LR = {
            'Left'  : '0',
            'Right' : '1'
        }

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States and qualifier['L/R'] in LR:
            CmdString = 'wM3000{0}*{1}AU\r'.format( LR[qualifier['L/R']] , States[value] )
            self.__SetHelper('InputUSBPlaybackMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputUSBPlaybackMute')

    def UpdateInputUSBPlaybackMute(self, value, qualifier):
        LR = {
            'Left'  : '0',
            'Right' : '1'
        }

        if qualifier['L/R'] in LR:
            CmdString = 'wM3000{}AU\r'.format(LR[qualifier['L/R']])
            self.__UpdateHelper('InputUSBPlaybackMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputUSBPlaybackMute')

    def __MatchInputUSBPlaybackMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('InputUSBPlaybackMute',  States[match.group(1).decode()] , {'L/R':tag} )

    def SetOutputAuxAttenuation(self, value, qualifier):


        if -100 <= value <= 0:
            CmdString = 'wG60005*{0}AU\r'.format(round(value*10))
            self.__SetHelper('OutputAuxAttenuation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAuxAttenuation')

    def UpdateOutputAuxAttenuation(self, value, qualifier):
        self.__UpdateHelper('OutputAuxAttenuation', 'wG60005AU\r', value, qualifier)

    def __MatchOutputAuxAttenuation(self, match, tag):
        self.WriteStatus('OutputAuxAttenuation',  int(match.group(1).decode())/10 , None)

    def SetOutputAuxMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM60005*{0}AU\r'.format(States[value])
            self.__SetHelper('OutputAuxMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAuxMute')

    def UpdateOutputAuxMute(self, value, qualifier):
        self.__UpdateHelper('OutputAuxMute', 'wM60005AU\r' , value, qualifier)

    def __MatchOutputAuxMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('OutputAuxMute',  States[match.group(1).decode()] , None)

    def SetOutputLineAttenuation(self, value, qualifier):

        if -100 <= value <= 0:
            CmdString = 'wG60002*{0}AU\rwG60003*{0}AU\r'.format(round(value*10))
            self.__SetHelper('OutputLineAttenuation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLineAttenuation')

    def UpdateOutputLineAttenuation(self, value, qualifier):
        self.__UpdateHelper('OutputLineAttenuation', 'wG60002AU\r' , value, qualifier)

    def __MatchOutputLineAttenuation(self, match, tag):
        self.WriteStatus('OutputLineAttenuation', int(match.group(1).decode())/10, None)

    def SetOutputLineMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM60002*{0}AU\rwM60003*{0}AU\r'.format(States[value])
            self.__SetHelper('OutputLineMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLineMute')

    def UpdateOutputLineMute(self, value, qualifier):
        self.__UpdateHelper('OutputLineMute', 'wM60002AU\r' , value, qualifier)

    def __MatchOutputLineMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('OutputLineMute', States[match.group(1).decode()], None)

    def SetOutputReferenceAttenuation(self, value, qualifier):


        if -100 <= value <= 0:
            CmdString = 'wG60004*{0}AU\r'.format(round(value * 10))
            self.__SetHelper('OutputReferenceAttenuation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputReferenceAttenuation')

    def UpdateOutputReferenceAttenuation(self, value, qualifier):
        self.__UpdateHelper('OutputReferenceAttenuation', 'wG60004AU\r' , value, qualifier)

    def __MatchOutputReferenceAttenuation(self, match, tag):
        self.WriteStatus('OutputReferenceAttenuation', int(match.group(1).decode())/10, None)

    def SetOutputReferenceMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM60004*{0}AU\r'.format(States[value])
            self.__SetHelper('OutputReferenceMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputReferenceMute')

    def UpdateOutputReferenceMute(self, value, qualifier):
        self.__UpdateHelper('OutputReferenceMute', 'wM60004AU\r' , value, qualifier)

    def __MatchOutputReferenceMute(self, match, tag):
        States = {
            '1'  : 'On',
            '0'  : 'Off'
        }

        self.WriteStatus('OutputReferenceMute', States[match.group(1).decode()], None)

    def SetOutputUSBAttenuation(self, value, qualifier):

        if -100 <= value <= 0:
            CmdString = 'wG60000*{0}AU\rwG60001*{0}AU\r'.format(round(value*10))
            self.__SetHelper('OutputUSBAttenuation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputUSBAttenuation')

    def UpdateOutputUSBAttenuation(self, value, qualifier):
        self.__UpdateHelper('OutputUSBAttenuation', 'wG60000AU\r', value, qualifier)

    def __MatchOutputUSBAttenuation(self, match, tag):
        self.WriteStatus('OutputUSBAttenuation', int(match.group(1).decode())/10, None)

    def SetOutputUSBMute(self, value, qualifier):

        States = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in States:
            CmdString = 'wM60000*{0}AU\rwM60001*{0}AU\r'.format(States[value])
            self.__SetHelper('OutputUSBMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputUSBMute')

    def UpdateOutputUSBMute(self, value, qualifier):
        self.__UpdateHelper('OutputUSBMute', 'wM60000AU\r', value, qualifier)

    def __MatchOutputUSBMute(self, match, tag):
        States = {
            '1' : 'On',
            '0' : 'Off'
        }

        self.WriteStatus('OutputUSBMute', States[match.group(1).decode()], None)

    def SetOverscanMode(self, value, qualifier):

        ValueStateValues = {
            '0%' : 'w1*0OSCN\r', 
            '2.5%' : 'w1*1OSCN\r', 
            '5%' : 'w1*2OSCN\r'
        }

        if value in ValueStateValues:
            OverscanModeCmdString = ValueStateValues[value]
            self.__SetHelper('OverscanMode', OverscanModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOverscanMode')

    def UpdateOverscanMode(self, value, qualifier):

        OverscanModeCmdString = 'w1OSCN\r'
        self.__UpdateHelper('OverscanMode', OverscanModeCmdString, value, qualifier)

    def __MatchOverscanMode(self, match, tag):

        ValueStateValues = {
            '0' : '0%', 
            '1' : '2.5%', 
            '2' : '5%'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OverscanMode', value, None)

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            'Save'   : ',',
            'Recall' : '.',
            'Delete' : ''
        }

        if value in ValueStateValues and 1 <= int(qualifier['Preset']) <= 16:
            if value == 'Delete':
                PresetCmdString = 'wX2*{0:03d}PRST\r'.format(int(qualifier['Preset']))
            else:
                PresetCmdString = '2*{0:03d}{1}'.format(int(qualifier['Preset']), ValueStateValues[value])
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')
    def SetScreenSaverMode(self, value, qualifier):

        ValueStateValues = {
            'Extron Logo' : '0', 
            'User Logo' : '1', 
            'Blue Screen or Bug' : '2'
        }

        if value in ValueStateValues:
            ScreenSaverModeCmdString = 'wM{0}SSAV\r'.format(ValueStateValues[value])
            self.__SetHelper('ScreenSaverMode', ScreenSaverModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenSaverMode')

    def UpdateScreenSaverMode(self, value, qualifier):

        ScreenSaverModeCmdString = 'wMSSAV\r'
        self.__UpdateHelper('ScreenSaverMode', ScreenSaverModeCmdString, value, qualifier)

    def __MatchScreenSaverMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Extron Logo', 
            '1' : 'User Logo', 
            '2' : 'Blue Screen or Bug'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenSaverMode', value, None)

    def UpdateScreenSaverStatus(self, value, qualifier):

        ScreenSaverStatusCmdString = 'wSSSAV\r'
        self.__UpdateHelper('ScreenSaverStatus', ScreenSaverStatusCmdString, value, qualifier)

    def __MatchScreenSaverStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenSaverStatus', value, None)

    def UpdateVideoSendStatus(self, value, qualifier):

        self.UpdateUSBHostStatus(value, qualifier)

    def UpdateUSBHostStatus(self, value, qualifier):

        USBHostStatusCmdString = '35I\r'
        self.__UpdateHelper('USBHostStatus', USBHostStatusCmdString, value, qualifier)

    def __MatchUSBHostStatus(self, match, tag):

        UsbStateValues = {
            '0' : 'Not Present', 
            '1' : 'Present',
            '2' : 'Suspended' # Response not Documented, Found by testing
        }

        VideoSendStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = UsbStateValues[match.group(1).decode()]
        self.WriteStatus('USBHostStatus', value, None)

        value = VideoSendStateValues[match.group(2).decode()]
        self.WriteStatus('VideoSendStatus', value, None)

    def SetUSBStreamingFormat(self, value, qualifier):

        ValueStateValues = {
            'MJPEG 422 Full' : '1', 
            'MJPEG 420 Full' : '2'
        }

        if value in ValueStateValues:
            USBStreamingFormatCmdString = 'w1*{0}OTYP\r'.format(ValueStateValues[value])
            self.__SetHelper('USBStreamingFormat', USBStreamingFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBStreamingFormat')

    def UpdateUSBStreamingFormat(self, value, qualifier):

        USBStreamingFormatCmdString = 'w1OTYP\r'
        self.__UpdateHelper('USBStreamingFormat', USBStreamingFormatCmdString, value, qualifier)

    def __MatchUSBStreamingFormat(self, match, tag):

        ValueStateValues = {
            '1' : 'MJPEG 422 Full', 
            '2' : 'MJPEG 420 Full'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBStreamingFormat', value, None)

    def SetUSBTerminalType(self, value, qualifier):

        ValueStateValues = {
            'Default' : '1', 
            'Echo Cancelling Speakerphone' : '2'
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
            '1' : 'Default', 
            '2' : 'Echo Cancelling Speakerphone'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBTerminalType', value, None)

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

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

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

    def UpdateVideoSignalPresence(self, value, qualifier):


        VideoSignalPresenceCmdString = 'w0LS\r'
        self.__UpdateHelper('VideoSignalPresence', VideoSignalPresenceCmdString, value, qualifier)

    def __MatchVideoSignalPresence(self, match, tag):

        ValueStateValues = {
            '1' : 'Signal', 
            '0' : 'No Signal'
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoSignalPresence', value, None)

    def SetVolume(self, value, qualifier):

        GroupStates = {
            'Program' : '1', 
            'Mic to Far End' : '3', 
            'Program to Far End' : '5', 
            'Far End to Ref' : '7', 
            'Mic to Aux' : '9'
        }

        if -100 <= value <= 0 and qualifier['Group'] in GroupStates:
            VolumeCmdString = 'wD{0}*{1}GRPM\r'.format(GroupStates[qualifier['Group']], int(value*10))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        GroupStates = {
            'Program' : '1', 
            'Mic to Far End' : '3', 
            'Program to Far End' : '5', 
            'Far End to Ref' : '7', 
            'Mic to Aux' : '9'
        }

        if qualifier['Group'] in GroupStates:
            VolumeCmdString = 'wD{0}GRPM\r'.format(GroupStates[qualifier['Group']])
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        GroupStates = {
            '1' : 'Program', 
            '3' : 'Mic to Far End', 
            '5' : 'Program to Far End', 
            '7' : 'Far End to Ref', 
            '9' : 'Mic to Aux'
        }

        qualifier = {'Group' : GroupStates[match.group(1).decode()]}
        value = int(match.group(2).decode()) / 10
        self.WriteStatus('Volume', value, qualifier)

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
            '01' : 'Invalid Input Number',
            '10' : 'Invalid Command',
            '11' : 'Invalid Preset Number',
            '12' : 'Invalid port or output number',
            '13' : 'Invalid Parameter',
            '14' : 'Illegal Command for this Configuration',
            '17' : 'Invalid Command for this Signal Type',
            '22' : 'Busy',
            '24' : 'Privilege Violation',
            '25' : 'Device Not Present',
            '26' : 'Maximum Number of Connections Exceeded',
            '28' : 'Bad Filename/File Not Found',
            '33 ': 'Bad File Type or Size'
        }
         
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES: 
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: '+ match.group(0).decode()])

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
