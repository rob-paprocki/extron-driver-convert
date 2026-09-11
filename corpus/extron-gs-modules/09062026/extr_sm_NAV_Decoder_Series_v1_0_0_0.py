from extronlib.interface import SPInterface
import re
from extronlib.system import Wait
from json import loads

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
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
            'AudioMute': {'Parameters': ['Type'], 'Status': {}},
            'CustomBorderColor': { 'Status': {}},
            'CustomBorderDuration': { 'Status': {}},
            'CustomBorderVisibility': { 'Status': {}},
            'CustomOSD': { 'Status': {}},
            'CustomOSDDuration': { 'Status': {}},
            'CustomOSDLocation': { 'Status': {}},
            'CustomOSDTextCommand': {'Parameters': ['Row'], 'Status': {}},
            'CustomOSDTextStatus': {'Parameters': ['Row'], 'Status': {}},
            'DeviceLocation': { 'Status': {}},
            'DeviceName': { 'Status': {}},
            'DeviceTags': { 'Status': {}},
            'HDCPInputStatus': { 'Status': {}},
            'HotkeySequenceDetection': { 'Parameters': ['Modifier'], 'Status': {}},
            'InputPresetRecall': { 'Status': {}},
            'HDCPOutputStatus': { 'Status': {}},
            'LLDPStatus': {'Parameters': ['Data Type'], 'Status': {}},
            'LLDPStatusEthExt': {'Parameters': ['Data Type'], 'Status':{}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'USBTie': {'Parameters': ['Host Type'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }
        
        self.VerboseDisabled = True

        self.AddMatchString(re.compile(b'Amt([0-2])\*([0-1])\r\n'), self.__MatchAudioMute, 'Set')
        self.AddMatchString(re.compile(b'Amt([0-1])\r\n'), self.__MatchAudioMute, 'SetAll')
        self.AddMatchString(re.compile(b'Amt([0-1]) ([0-1])'), self.__MatchAudioMute, 'Update')
        self.AddMatchString(re.compile(b'WndwB1\*([1-9])\r\n'), self.__MatchCustomBorderColor, None)
        self.AddMatchString(re.compile(b'WndwD1\*(\d{1,3})\r\n'), self.__MatchCustomBorderDuration, None)
        self.AddMatchString(re.compile(b'WndwV1\*([0-1])\r\n'), self.__MatchCustomBorderVisibility, None)
        self.AddMatchString(re.compile(b'WndwV4\*([0-1])\r\n'), self.__MatchCustomOSD, None)
        self.AddMatchString(re.compile(b'WndwD4\*(\d{1,3})\r\n'), self.__MatchCustomOSDDuration, None)
        self.AddMatchString(re.compile(b'WndwL4\*([0-4])\r\n'), self.__MatchCustomOSDLocation, None)
        self.AddMatchString(re.compile(b'TextT4\*([1-2])\*([\w|\W]{0,})\r\n'), self.__MatchCustomOSDTextStatus, None)
        self.AddMatchString(re.compile(b'Dtag (\{"tags":\[[A-Za-z0-9-\, "]+\]\})\r\n'), self.__MatchDeviceTags, None)
        self.AddMatchString(re.compile(b'In([0-9]{1,4}) (All|Vid|Aud)\r\n'), self.__MatchInput, None)
        self.AddMatchString(re.compile(b'HdcpI([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
        self.AddMatchString(re.compile(b'HdcpO([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
        self.AddMatchString(re.compile(b'Hkdm(P|K)(\d{1,2})\r\n|Hkdm(P|K)([A-Za-z])\r\n'), self.__MatchHotkeySequenceDetection, None)
        self.AddMatchString(re.compile(b'(6[01])Stat ({.*})\r\n'), self.__MatchLLDPStatus, None)
        self.AddMatchString(re.compile(b'Inf05\*(.+)\r\n'), self.__MatchDeviceLocation, None)
        self.AddMatchString(re.compile(b'Ipn ([a-zA-z0-9-]+)\r\n'), self.__MatchDeviceName, None)
        self.AddMatchString(re.compile(b'In([0-9]{1,4})([io]) Usb\r\n'), self.__MatchUSBTie, None)
        self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, None)
        self.AddMatchString(re.compile(b'Vol\+{0,1}([0-9]{1,3})\r\n'), self.__MatchVolume, None)
        self.AddMatchString(re.compile(b'VidI([0-1])\*HdcpI([0-2])\*HdcpO([0-2])\*ResI[0-9]{1,4}x[0-9]{1,4}@[0-9.]{1,5}\*AudI([0-1])\*StrmI[0-2]\*Lnk[0-2]\*Dec\r\n'), self.__MatchDecoderInfo, None)
        self.AddMatchString(re.compile(b'Inf35\*([0-2])\r\n'), self.__MatchDecoder2Info, None)
        self.AddMatchString(re.compile(b'E(10|12|13|14|17|22|24|25|28)\r\n'), self.__MatchErrors, None)
        self.AddMatchString(re.compile(b'Vrb3'), self.__MatchVerboseMode, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
    
    def UpdateDeviceLocation(self, value, qualifier):

        self.__UpdateHelper('DeviceLocation', '5i', value, qualifier)
        
    def __MatchDeviceLocation(self, match, tag):
        self.WriteStatus('DeviceLocation', match.group(1).decode(), 
                            None)
    
    def UpdateDeviceName(self, value, qualifier):

        self.__UpdateHelper('DeviceName', 'wCN\r', value, qualifier)

    def __MatchDeviceName(self, match, tag):
        self.WriteStatus('DeviceName', match.group(1).decode(), 
                            None)
        
    def UpdateDeviceTags(self, value, qualifier):

        self.__UpdateHelper('DeviceTags', 'wDTAG\r', value, qualifier)
            
    def __MatchDeviceTags(self, match, qualifier):

        string = match.group(1).decode()
        string = loads(string)
        text = ''
        for strings in string['tags']:
            if text:
                text = text + ', ' + strings
            else:
                text = text + strings            
        self.WriteStatus('DeviceTags', text, None)
                            
    def __MatchDecoderInfo(self, match, qualifier):

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPInputStatus', HDCPStatusState[match.group(2).decode()], None)
        self.WriteStatus('HDCPOutputStatus', HDCPStatusState[match.group(3).decode()], None)

    def __MatchDecoder2Info(self, match, qualifier):

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPInputStatus', HDCPStatusState[match.group(1).decode()], None)
        
    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }

        TypeState = {
            'HDMI': '1',
            'Analog': '2',
            'All': '3'
            }

        type = qualifier['Type']
        if type == 'All':
            self.__SetHelper('AudioMute', '{0}Z'.format(AudioMuteState[value]), value, qualifier)
        else:
            self.__SetHelper('AudioMute', '{0}*{1}Z'.format(TypeState[type], AudioMuteState[value]), value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        self.__UpdateHelper('AudioMute', 'Z', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteName = {
            '1': 'On',
            '0': 'Off',
        }
        
        if tag == 'SetAll':
            mutestate = AudioMuteName[match.group(1).decode()]
            self.WriteStatus('AudioMute', mutestate, {'Type': 'HDMI'})
            self.WriteStatus('AudioMute', mutestate, {'Type': 'Analog'})
            self.WriteStatus('AudioMute', mutestate, {'Type': 'All'})
            
        elif tag == 'Update':
            hdmi = AudioMuteName[match.group(1).decode()]
            analog = AudioMuteName[match.group(2).decode()]
            self.WriteStatus('AudioMute', hdmi, {'Type': 'HDMI'})
            self.WriteStatus('AudioMute', analog, {'Type': 'Analog'})
            if hdmi == analog:
                self.WriteStatus('AudioMute', analog, {'Type': 'All'})
                
            else:
                self.WriteStatus('AudioMute', 'Off', {'Type': 'All'})
                
        else:
            TypeState = {
            '1': 'HDMI',
            '2': 'Analog',
            '3': 'All'
            }
        
            type = TypeState[match.group(1).decode()]
            mutestate = AudioMuteName[match.group(2).decode()]
            self.WriteStatus('AudioMute', mutestate, {'Type': type})
            otherstate = None
            if type == 'HDMI':
                otherstate = self.ReadStatus('AudioMute', {'Type': 'Analog'})
                if otherstate == mutestate:
                    self.WriteStatus('AudioMute', mutestate, {'Type': 'All'})
                    
                else:
                    self.WriteStatus('AudioMute', 'Off', {'Type': 'All'})
                    
            elif type == 'Analog':
                otherstate = self.ReadStatus('AudioMute', {'Type': 'HDMI'})
                if otherstate == mutestate:
                    self.WriteStatus('AudioMute', mutestate, {'Type': 'All'})
                    
                else:
                    self.WriteStatus('AudioMute', 'Off', {'Type': 'All'})                    

    def SetCustomBorderDuration(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 501
            }
        
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CustomBorderDurationCmdString = 'wD1*{0}WNDW\r'.format(value)
            self.__SetHelper('CustomBorderDuration', CustomBorderDurationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCustomBorderDuration')
        
    def UpdateCustomBorderDuration(self, value, qualifier):

        self.__UpdateHelper('CustomBorderDuration', 'wD1WNDW\r', value, qualifier)

    def __MatchCustomBorderDuration(self, match, qualifier):
    
        value = int(match.group(1).decode())
        self.WriteStatus('CustomBorderDuration', value, None)

    def SetCustomBorderColor(self, value, qualifier):

        ColorState = {
            'Yellow': 1,
            'Orange': 2,
            'Red': 3,
            'Blue': 4,
            'Green': 5,
            'Magenta': 6,
            'Teal': 7,
            'White': 8,
            'Black': 9
        }
        
        if value not in ColorState:
            self.Discard('Invalid Command for SetCustomBorderColor')
        else:
            self.__SetHelper('CustomBorderColor', 'wB1*{0}WNDW\r'.format(ColorState[value]), value, qualifier)

    def UpdateCustomBorderColor(self, value, qualifier):

        self.__UpdateHelper('CustomBorderColor', 'wB1WNDW\r', value, qualifier)

    def __MatchCustomBorderColor(self, match, qualifier):

        ColorState = {
            1: 'Yellow',
            2: 'Orange',
            3: 'Red',
            4: 'Blue',
            5: 'Green',
            6: 'Magenta',
            7: 'Teal',
            8: 'White',
            9: 'Black'
        }

        colorstate = ColorState[int(match.group(1).decode())]
        self.WriteStatus('CustomBorderColor', colorstate, None)

    def SetCustomBorderVisibility(self, value, qualifier):

        BorderState = {
            'Visible': 1,
            'Hidden': 0
        }
        
        if value not in BorderState:
            self.Discard('Invalid Command for SetCustomBorderVisibility')
        else:
            self.__SetHelper('CustomBorderVisibility', 'wV1*{0}WNDW\r'.format(BorderState[value]), value, qualifier)

    def UpdateCustomBorderVisibility(self, value, qualifier):

        self.__UpdateHelper('CustomBorderVisibility', 'wV1WNDW\r', value, qualifier)

    def __MatchCustomBorderVisibility(self, match, qualifier):

        BorderState = {
            1:'Visible',
            0:'Hidden'
        }

        borderstate = BorderState[int(match.group(1).decode())]
        self.WriteStatus('CustomBorderVisibility', borderstate, None)

    def SetCustomOSD(self, value, qualifier):

        OSDState = {
            'On': 1,
            'Off': 0
        }
        
        if value not in OSDState:
            self.Discard('Invalid Command for SetCustomOSD')
        else:
            self.__SetHelper('CustomOSD', 'wV4*{0}WNDW\r'.format(OSDState[value]), value, qualifier)

    def UpdateCustomOSD(self, value, qualifier):

        self.__UpdateHelper('CustomOSD', 'wV4WNDW\r', value, qualifier)

    def __MatchCustomOSD(self, match, qualifier):

        VisibilityState = {
            1: 'On',
            0: 'Off'
        }

        value = int(match.group(1).decode())
        self.WriteStatus('CustomOSD', VisibilityState[value], None)

    def SetCustomOSDDuration(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 501
            }
        
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CustomOSDDurationCmdString = 'wD4*{0}WNDW\r'.format(value)
            self.__SetHelper('CustomOSDDuration', CustomOSDDurationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCustomOSDDuration')
        
    def UpdateCustomOSDDuration(self, value, qualifier):

        self.__UpdateHelper('CustomOSDDuration', 'wD4WNDW\r', value, qualifier)

    def __MatchCustomOSDDuration(self, match, qualifier):

        value = int(match.group(1).decode())
        self.WriteStatus('CustomOSDDuration', value, None)

    def SetCustomOSDLocation(self, value, qualifier):

        LocationState = {
            'Top-Left': 1,
            'Top-Right': 2,
            'Bottom-Left': 3,
            'Bottom-Right': 4
        }
        
        if value not in LocationState:
            self.Discard('Invalid Command for SetCustomOSDLocation')
        else:
            self.__SetHelper('CustomOSDLocation', 'wL4*{0}WNDW\r'.format(LocationState[value]), value, qualifier)

    def UpdateCustomOSDLocation(self, value, qualifier):

        self.__UpdateHelper('CustomOSDLocation', 'wL4WNDW\r', value, qualifier)

    def __MatchCustomOSDLocation(self, match, qualifier):
        
        LocationState = {
            1: 'Top-Left',
            2: 'Top-Right',
            3: 'Bottom-Left',
            4: 'Bottom-Right'
        }

        value = int(match.group(1).decode())
        self.WriteStatus('CustomOSDLocation', LocationState[value], None)

    def SetCustomOSDTextCommand(self, value, qualifier):

        line = qualifier['Row']
        if line not in ['1', '2']:
            self.Discard('Invalid Command for SetCustomOSDTextCommand')
        else:
            cmdstring = value
            if cmdstring:
                self.__SetHelper('CustomOSDTextCommand', 'wT4*{0}*{1}TEXT\r'.format(line, cmdstring), value, qualifier)
            else:
                self.__SetHelper('CustomOSDTextCommand', 'wT4*{0}* TEXT\r'.format(line, cmdstring), value, qualifier)
                
    def UpdateCustomOSDTextStatus(self, value, qualifier):

        line = qualifier['Row']
        if line not in ['1', '2']:
            self.Discard('Invalid Command for UpdateCustomOSDTextStatus')
        else:
            self.__UpdateHelper('CustomOSDTextStatus', 'wT4*{0}TEXT\r'.format(line), value, qualifier)

    def __MatchCustomOSDTextStatus(self, match, qualifier):

        line = str(int(match.group(1).decode()))
        text = match.group(2).decode()
        self.WriteStatus('CustomOSDTextStatus', text, {'Row': line})

    def UpdateHDCPInputStatus(self, value, qualifier):

        self.__UpdateHelper('HDCPInputStatus', '35i', value, qualifier)

    
    def __MatchHDCPInputStatus(self, match, tag):

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPInputStatus', HDCPStatusState[match.group(1).decode()], None)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        self.__UpdateHelper('HDCPOutputStatus', 'i', value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPOutputStatus', HDCPStatusState[match.group(1).decode()], None)
        
    def __MatchHotkeySequenceDetection(self, match, tag):
        
        TypeState = {
            'P': 'Ctrl, Ctrl',
            'K': 'Ctrl, Shift',
        }
        modifier = None
        if match.group(1):
            modifier = TypeState[match.group(1).decode()]
            self.WriteStatus('HotkeySequenceDetection', match.group(2).decode(), {'Modifier': modifier})
        else:
            modifier = TypeState[match.group(3).decode()]
            self.WriteStatus('HotkeySequenceDetection', match.group(4).decode(), {'Modifier': modifier})
            
        @Wait(1)
        def ResetState():
            self.WriteStatus('HotkeySequenceDetectionDecoder', 'Waiting for sequence', {'Modifier': modifier})

    def SetInputPresetRecall(self, value, qualifier):

        if int(value) < 0 or int(value) > 16:
            self.Discard('Invalid Command for SetInputPresetRecall')
        else:
            InputPresetRecallCmdString = '\x1bR2*{0}PRST\r'.format(value.zfill(2))
            self.__SetHelper('InputPresetRecall', InputPresetRecallCmdString, value, qualifier)

    def UpdateLLDPStatus(self, value, qualifier):
        self.__UpdateHelper('LLDPStatus', '\x1b60STAT\r', value, qualifier)
        
    def UpdateLLDPStatusEthExt(self, value, qualifier):
        self.__UpdateHelper('LLDPStatusEthExt', '\x1b61STAT\r', value, qualifier)
        
    def __MatchLLDPStatus(self, match, qualifier):
        LANtype = match.group(1).decode()
        value = match.group(2).decode()
        test = loads(value)
        try:
            name = test['neighbors'][0]['System Name']
        except (KeyError, IndexError):
            name = 'N/A'
        try:
            managementaddress = test['neighbors'][0]['Management Address']
        except (KeyError, IndexError):
            managementaddress = 'N/A'
        try:
            PortID = test['neighbors'][0]['Port ID']
        except (KeyError, IndexError):
            PortID = 'N/A'
        try:
            SystemDescription = test['neighbors'][0]['System Description']
        except (KeyError, IndexError):
            SystemDescription = 'N/A'
        try:
            PortVLANID = test['neighbors'][0]['Port VLAN ID']
        except (KeyError, IndexError):
            PortVLANID = 'N/A'
        try:
            ChassisID = test['neighbors'][0]['Chassis ID']
        except (KeyError, IndexError):
            ChassisID = 'N/A'
        try:
            PortDescription = test['neighbors'][0]['Port Description']
        except (KeyError, IndexError):
            PortDescription = 'N/A'
        try:
            SystemCapabilities = test['neighbors'][0]['System Capabilities']
        except (KeyError, IndexError):
            SystemCapabilities = 'N/A'
        try:
            TimetoLive = test['neighbors'][0]['Time to live']
        except (KeyError, IndexError):
            TimetoLive = 'N/A'
        if LANtype == '60':
            try:
                self.WriteStatus('LLDPStatus', name, {'Data Type': 'System Name'})
                self.WriteStatus('LLDPStatus', managementaddress, {'Data Type': 'Management Address'})
                self.WriteStatus('LLDPStatus', PortID, {'Data Type': 'Port ID'})
                self.WriteStatus('LLDPStatus', SystemDescription, {'Data Type': 'System Description'})
                self.WriteStatus('LLDPStatus', PortVLANID, {'Data Type': 'VLAN ID'})
                self.WriteStatus('LLDPStatus', ChassisID, {'Data Type': 'Chassis ID'})
                self.WriteStatus('LLDPStatus', PortDescription, {'Data Type': 'Port Description'})
                self.WriteStatus('LLDPStatus', SystemCapabilities, {'Data Type': 'System Capabilities'})
                self.WriteStatus('LLDPStatus', TimetoLive, {'Data Type': 'Time to Live'})
            except Exception as e:
                pass
        elif LANtype == '61':
            try:
                self.WriteStatus('LLDPStatusEthExt', name, {'Data Type': 'System Name'})
                self.WriteStatus('LLDPStatusEthExt', managementaddress, {'Data Type': 'Management Address'})
                self.WriteStatus('LLDPStatusEthExt', PortID, {'Data Type': 'Port ID'})
                self.WriteStatus('LLDPStatusEthExt', SystemDescription, {'Data Type': 'System Description'})
                self.WriteStatus('LLDPStatusEthExt', PortVLANID, {'Data Type': 'VLAN ID'})
                self.WriteStatus('LLDPStatusEthExt', ChassisID, {'Data Type': 'Chassis ID'})
                self.WriteStatus('LLDPStatusEthExt', PortDescription, {'Data Type': 'Port Description'})
                self.WriteStatus('LLDPStatusEthExt', SystemCapabilities, {'Data Type': 'System Capabilities'})
                self.WriteStatus('LLDPStatusEthExt', TimetoLive, {'Data Type': 'Time to Live'})
            except Exception as e:
                pass
        
    def SetInput(self, value, qualifier):

        TieTypeValues = {
            'Audio/Video': '!',
            'Video': '%',
            'Audio': '$',
        }

        Input = value
        tieType = qualifier['Type']
        InputCmdString = '\x1B{0}{1}\r'.format(Input, TieTypeValues[tieType])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
        
    def UpdateInput(self, value, qualifier):

        TieTypeValues = {
            'Audio/Video': '!',
            'Video': '%',
            'Audio': '$',
        }
        InputCmdString = '{}'.format(TieTypeValues[qualifier['Type']])
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        TieTypeValues = {
            'All': 'Audio/Video',
            'Vid': 'Video',
            'Aud': 'Audio',
        }
        value = int(match.group(1).decode())
        type = TieTypeValues[match.group(2).decode()]
        
        if type == 'Audio/Video':
            self.WriteStatus('Input', value, {'Type': 'Audio'})
            self.WriteStatus('Input', value, {'Type': 'Video'})
        else:
            opp = 'Video' if type == 'Audio' else 'Audio'
            inpt = self.ReadStatus('Input', {'Type': opp})
            if inpt == value:
                self.WriteStatus('Input', value, {'Type': 'Audio/Video'})
        self.WriteStatus('Input', value, {'Type': type})

    def SetVolume(self, value, qualifier):
        
        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }
        
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)
          
    def SetUSBTie(self, value, qualifier):
        
        HostTypeValues = {
            'Input': 'i',
            'Output': 'o'
        }

        HostType = qualifier['Host Type']

        MatrixTieCmdString = 'w{0}{1}^\r'.format(value, HostTypeValues[HostType])
        self.__SetHelper('USBTie', MatrixTieCmdString, value, qualifier)
        
    def UpdateUSBTie(self, value, qualifier):
        
        USBTieCmdString = '^'
        self.__UpdateHelper('USBTie', USBTieCmdString, value, qualifier)

    def __MatchUSBTie(self, match, tag):

        numlookup = {
            'i': 'Input',
            'o': 'Output'
        }
        hostnum = int(match.group(1).decode())
        if hostnum == 0:
            self.WriteStatus('USBTie', hostnum, {'Host Type': 'Output'})
        hosttype = match.group(2).decode()
        self.WriteStatus('USBTie', hostnum, {'Host Type': numlookup[hosttype]})

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
            'Video and Sync' : '2'
        }

        self.__SetHelper('VideoMute', '{0}B'.format(VideoMuteState[value]), value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteName = {
            '0': 'Off',
            '1': 'On',
            '2': 'Video and Sync'
        }
        self.WriteStatus('VideoMute', VideoMuteName[match.group(1).decode()], None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True        
        if self.VerboseDisabled:
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

        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __MatchErrors(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid output number or port number',
            '13': 'Invalid parameter (out of range)',
            '14': 'Command not available for this configuration',
            '17': 'System timed out (caused by direct write of global presets)',
            '21': 'Invalid room number',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found'
        }
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.EchoDisabled = True
        self.VerboseDisabled = True
                
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

class SPIClass(SPInterface, DeviceClass):

    def __init__(self, spd, Model=None):
        SPInterface.__init__(self, spd)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        print('Module: {}'.format(__name__), 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        self.OnDisconnected()

