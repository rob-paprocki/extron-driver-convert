from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, search

class DeviceClass:

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
        self.devicePassword = '0000'
        self.Debug = False

        self.Models = {
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'InputSelect': {'Status': {}},
            'InputSource': {'Status': {}},
            'InputSourceStatus': {'Parameters':['Input'], 'Status': {}},
            'LampMode': {'Status': {}},
            'LampStatus': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPInput': {'Parameters':['Picture'], 'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Parameters':['Main Picture Size', 'Sub Picture Size'], 'Status': {}},
            'PIPSizeStatus': {'Parameters':['Picture'], 'Status': {}},   
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'PASSWORD:'), self.__MatchPassword, None)

    def __MatchPassword(self, match, tag):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Normal'  : 'CF SCREEN NORMAL\r',
            'Full'    : 'CF SCREEN FULL\r',
            'Wide'    : 'CF SCREEN WIDE\r',
            'True'    : 'CF SCREEN TRUE\r',
            'Zoom'    : 'CF SCREEN ZOOM\r',
            'Natural' : 'CF SCREEN NATURAL\r',
            'Custom'  : 'CF SCREEN CUSTOM\r',
        }

        AspectRatioCmdString = AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier): 

        AspectRatioStateNames = {
            'NO' : 'Normal',
            'FU' : 'Full',
            'WI' : 'Wide',
            'TR' : 'True',
            'ZO' : 'Zoom',
            'NA' : 'Natural',
            'CU' : 'Custom',
        }

        AspectRatioCmdString = 'CR SCREEN\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = AspectRatioStateNames[res[4:6]]
                self.WriteAspectRatio(value,qualifier,'Live')
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On'  : 'CF MUTE ON\r',
            'Off' : 'CF MUTE OFF\r',
            }

        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier): 

        AudioMuteStateNames = {
            'N' : 'On',
            'F' : 'Off',
           }

        AudioMuteCmdString = 'CR MUTE\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = AudioMuteStateNames[res[5]]
                self.WriteAudioMute(value,qualifier,'Live')
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)


    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'RC'   : 'CF KEYDIS RC\r',
            'Key'  : 'CF KEYDIS KEY\r',
            'None' : 'CF KEYDIS NONE\r',
            }

        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier): 

        ExecutiveModeStateNames = {
            'R' : 'RC',
            'K' : 'Key',
            'N' : 'None',
           }

        ExecutiveModeCmdString = 'CR KEYDIS\r'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ExecutiveModeStateNames[res[4]]
                self.WriteExecutiveMode(value,qualifier,'Live')
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdateExecutiveMode')

    def UpdateFilterUsage(self, value, qualifier): 

        FilterUsageCmdString = 'CR FILH\r'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = int(res[4:-1])
                self.WriteFilterUsage(value,qualifier,'Live')
            except (ValueError,IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On'  : 'CF FREEZE ON\r',
            'Off' : 'CF FREEZE OFF\r',
            }

        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeStateNames = {
            'N' : 'On',
            'F' : 'Off',
           }

        FreezeCmdString = 'CR FREEZE\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = FreezeStateNames[res[5]]
                self.WriteFreeze(value,qualifier,'Live')
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInputSelect(self, value, qualifier):

        InputSelectStateValues = {
            '1' : 'CF INPUT 1\r',
            '2' : 'CF INPUT 2\r',
            '3' : 'CF INPUT 3\r',
            '4' : 'CF INPUT 4\r',
            }

        InputSelectCmdString = InputSelectStateValues[value]
        self.__SetHelper('InputSelect', InputSelectCmdString, value, qualifier)

    def UpdateInputSelect(self, value, qualifier): 

        InputSelectStateNames = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
        }
        
        InputSelectCmdString = 'CR INPUT\r'

        res = self.__UpdateHelper('InputSelect', InputSelectCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = InputSelectStateNames[res[4]]
                self.WriteInputSelect(value,qualifier,'Live')
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdateInputSelect')

    def SetInputSource(self, value, qualifier):

        InputSourceStateValues = {
            'Input 1 Digital' : 'CF INPUT1 DIGITAL\r',
            'Input 1 Analog'  : 'CF INPUT1 ANALOG\r',
            'Input 1 SCART'   : 'CF INPUT1 SCART\r',
            'Input 1 HDCP'    : 'CF INPUT1 HDCP\r',
            'Input 1 HDMI'    : 'CF INPUT1 HDMI\r',
            'Input 2 Video'   : 'CF INPUT2 VIDEO\r',
            'Input 2 YPbPr'   : 'CF INPUT2 YPBPR\r',
            'Input 2 YCbCr'   : 'CF INPUT2 YCBCR\r',
            'Input 2 Analog'  : 'CF INPUT2 ANALOG\r',
            'Input 3 Video'   : 'CF INPUT3 VIDEO\r',
            'Input 3 S-Video' : 'CF INPUT3 S-VIDEO\r',
            'Input 3 YPbPr'   : 'CF INPUT3 YPBPR\r',
            'Input 3 YCbCr'   : 'CF INPUT3 YCBCR\r',
            'Input 4 Network' : 'CF INPUT4 NETWORK\r',
            }

        InputSourceCmdString = InputSourceStateValues[value]
        self.__SetHelper('InputSource', InputSourceCmdString, value, qualifier)


    def UpdateInputSourceStatus(self, value, qualifier):

        Input1SourceStateNames = {
            'DIG'   : 'Input 1 Digital',
            'ANA'   : 'Input 1 Analog',
            'SCA'   : 'Input 1 SCART',
            'HDC'   : 'Input 1 HDCP',
            'HDM'   : 'Input 1 HDMI',
           }

        Input2SourceStateNames = {
            'VID' : 'Input 2 Video',
            'YPB' : 'Input 2 YPbPr',
            'ANA' : 'Input 2 Analog'
           }

        Input3SourceStateNames = {            
            'VID'  : 'Input 3 Video',
            'S-V'  : 'Input 3 S-Video',
            'YPB'  : 'Input 3 YPbPr',
           }

        Input4SourceStateNames = {
            'NET' : 'Network'
            }

        Input = qualifier['Input']

        if 1 <= int(Input) <= 4:
            InputSourceStatusCmdString = 'CR SRCINP{0}\r'.format(Input)
            res = self.__UpdateHelper('InputSourceStatus', InputSourceStatusCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    if Input == '1':
                        value = Input1SourceStateNames[res[4:7]]
                    elif Input == '2':
                        value = Input2SourceStateNames[res[4:7]]
                    elif Input == '3':
                        value = Input3SourceStateNames[res[4:7]]
                    elif Input == '4':
                        value = Input4SourceStateNames[res[4:7]]
                    self.WriteInputSourceStatus(value,qualifier,'Live')
                except(KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInputSourceStatus')
        else:
            print('Invalid Command for UpdateInputSourceStatus')

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Normal' : 'CF LAMPMODE NORMAL\r',
            'ECO 1'  : 'CF LAMPMODE ECO1\r',
            'ECO 2'  : 'CF LAMPMODE ECO2\r',
            'Auto'   : 'CF LAMPMODE AUTO\r',
            }

        LampModeCmdString = LampModeStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier): 

        LampModeStateNames = {
            'MAL' : 'Normal',
            'CO1' : 'ECO 1',
            'CO2' : 'ECO 2',
            'UTO' : 'Auto',
           }
        LampModeCmdString = 'CR LAMPMODE\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = LampModeStateNames[res[-4:-1]]
                self.WriteLampMode(value,qualifier,'Live')
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampStatus(self, value, qualifier):

        LampStatusStateNames = {
            'I' : 'On',
            'O' : 'Off',
            'X' : 'Lamp Failure',
           }

        LampStatusCmdString = 'CR LAMPSTS\r'
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = LampStatusStateNames[res[5]]
                self.WriteLampStatus(value,qualifier,'Live')
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdateLampStatus')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'CR LAMPH\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = int(res[4:-1])
                self.WriteLampUsage(value,qualifier,'Live')
            except (ValueError,IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):
        
        MenuNavigationStateValues = {
            'Right'  : 'CF KEYEMU RIGHT\r',
            'Left'   : 'CF KEYEMU LEFT\r',
            'Up'     : 'CF KEYEMU UP\r',
            'Down'   : 'CF KEYEMU DOWN\r',
            'Select' : 'CF KEYEMU SELECT\r'
            }

        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateValues = {
            'On'  : 'CF MENU ON\r',
            'Off' : 'CF MENU OFF\r',
            }

        OnScreenDisplayCmdString = OnScreenDisplayStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier): 

        OperationHoursCmdString = 'CR PROJH\r'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = int(res[4:-1])
                self.WriteOperationHours(value,qualifier,'Live')
            except (ValueError,IndexError):
                print('Invalid/unexpected response for UpdateOperationHours')

    def SetPIP(self, value, qualifier):

        PIPStateValues = {
            'Off'    : 'CF PIP OFF\r',
            'User 1' : 'CF PIP USER1\r',
            'User 2' : 'CF PIP USER2\r',
            'User 3' : 'CF PIP USER3\r',
            'User 4' : 'CF PIP USER4\r',
            'User 5' : 'CF PIP USER5\r',
            }

        PIPCmdString = PIPStateValues[value]
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier): 

        PIPStateNames = {
            'F' : 'Off',
            '1' : 'User 1',
            '2' : 'User 2',
            '3' : 'User 3',
            '4' : 'User 4',
            '5' : 'User 5',
           }

        PIPCmdString = 'CR PIP\r'
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = PIPStateNames[res[-2:-1]]
                self.WritePIP(value,qualifier,'Live')
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdatePIP')

    def SetPIPInput(self, value, qualifier):

        PictureQualifierValues = {
            'Main' : 'MAIN',
            'Sub'  : 'SUB'
            }

        Picture = qualifier['Picture']

        PIPInputStateValues = {
            'Input 1 Digital' : 'CF PIP{0}INP 1 DIGITAL\r',
            'Input 1 Analog'  : 'CF PIP{0}INP 1 ANALOG\r',
            'Input 1 SCART'   : 'CF PIP{0}INP 1 SCART\r',
            'Input 1 HDCP'    : 'CF PIP{0}INP 1 HDCP\r',
            'Input 1 HDMI'    : 'CF PIP{0}INP 1 HDMI\r',
            'Input 2 Video'   : 'CF PIP{0}INP 2 VIDEO\r',
            'Input 2 YPbPr'   : 'CF PIP{0}INP 2 YPBPR\r',
            'Input 2 YCbCr'   : 'CF PIP{0}INP 2 YCBCR\r',
            'Input 2 Analog'  : 'CF PIP{0}INP 2 ANALOG\r',
            'Input 3 Video'   : 'CF PIP{0}INP 3 VIDEO\r',
            'Input 3 S-Video' : 'CF PIP{0}INP 3 S-VIDEO\r',
            'Input 3 YPbPr'   : 'CF PIP{0}INP 3 YPBPR\r',
            'Input 3 YCbCr'   : 'CF PIP{0}INP 3 YCBCR\r',
            }


        if Picture in ['Main', 'Sub']:
            PIPInputCmdString = PIPInputStateValues[value].format(PictureQualifierValues[Picture])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier): 

        PIPInputStateNames1 = {
            'DIG' : 'Input 1 Digital',
            'ANA' : 'Input 1 Analog',
            'SCA' : 'Input 1 SCART',
            'HDC' : 'Input 1 HDCP',
            'HDM' : 'Input 1 HDMI',
            }

        PIPInputStateNames2 = {
            'VID' : 'Input 2 Video',
            'YPB' : 'Input 2 YPbPr',
            'ANA' : 'Input 2 Analog',
            }

        PIPInputStateNames3 = {
            'VID' : 'Input 3 Video',
            'S-V' : 'Input 3 S-Video',
            'YPB' : 'Input 3 YPbPr',
           }


        PictureQualifierValues = {
            'Main' : 'MAIN',
            'Sub'  : 'SUB'
            }

        Picture = qualifier['Picture']

        if Picture in ['Main', 'Sub']:
            PIPInputCmdString = 'CR PIP{0}INP\r'.format(PictureQualifierValues[Picture])
            res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    Input = res[4]
                    if Input == '1':
                        value = PIPInputStateNames1[res[6:9]]
                    elif Input == '2':
                        value = PIPInputStateNames2[res[6:9]] 
                    elif Input == '3':
                        value = PIPInputStateNames3[res[6:9]] 
                    self.WritePIPInput(value,qualifier,'Live')
                except (KeyError,IndexError):
                    print('Invalid/unexpected response for UpdatePIPInput')
        else:
            print('Invalid Command for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        PIPModeStateValues = {
            'PIP'  : 'CF PIPMODE PINP\r',
            'PbyP' : 'CF PIPMODE PBYP\r',
            }

        PIPModeCmdString = PIPModeStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier): 

        PIPModeStateNames = {
            'I' : 'PIP',
            'B' : 'PbyP',
        }

        PIPModeCmdString = 'CR PIPMODE\r'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = PIPModeStateNames[res[5]]
                self.WritePIPMode(value,qualifier,'Live')
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdatePIPMode')

    def SetPIPPosition(self, value, qualifier):

        PIPPositionStateValues = {
            '1' : 'CF PIPPOSITION POS1\r',
            '2' : 'CF PIPPOSITION POS2\r',
            '3' : 'CF PIPPOSITION POS3\r',
            '4' : 'CF PIPPOSITION POS4\r',
            '5' : 'CF PIPPOSITION POS5\r',
            '6' : 'CF PIPPOSITION POS6\r',
            '7' : 'CF PIPPOSITION POS7\r',
            '8' : 'CF PIPPOSITION POS8\r',
            }

        PIPPositionCmdString = PIPPositionStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def SetPIPSize(self, value, qualifier):

        MainSize = qualifier['Main Picture Size']
        SubSize = qualifier['Sub Picture Size']

        if MainSize in ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100'] and SubSize in ['10', '20', '30', '40', '50']: 
            PIPSizeCmdString = 'CF PIPSIZE {0} {1}\r'.format(MainSize, SubSize)
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSizeStatus(self, value, qualifier): 

        PIPSizeStatusStateNames = {
            1  : '10%',
            2  : '20%',
            3  : '30%',
            4  : '40%',
            5  : '50%',
            6  : '60%',
            7  : '70%',
            8  : '80%',
            9  : '90%',
            10 : '100%',
        }
                       
        Picture = qualifier['Picture']
        
        if Picture in ['Main Picture', 'Sub Picture']:
            PIPSizeStatusCmdString = 'CR PIPSIZE\r'
            res = self.__UpdateHelper('PIPSizeStatus', PIPSizeStatusCmdString, value, qualifier)
            if res:
                res = res.decode()
                try:
                    if Picture == 'Main Picture':
                        value = PIPSizeStatusStateNames[int(res[4:6])]
                    elif Picture == 'Sub Picture':
                        value = PIPSizeStatusStateNames[int(res[-4:-2])]
                    self.WritePIPSizeStatus(value,qualifier,'Live')
                except (KeyError,IndexError):
                    print('Invalid/unexpected response for UpdatePIPSizeStatus')
        else:
            print('Invalid Command for UpdatePIPSizeStatus')

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : 'CF POWER ON\r',
            'Off' : 'CF POWER OFF\r'
            }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier): 

        PowerStateNames = {
            '00' : 'On',
            '80' : 'Off',
            '40' : 'Warming Up',
            '20' : 'Cooling Down',
            '10' : 'Power Failure',
            '28' : 'Cooling Down in process due to abnormal temperature',
            '88' : 'Standby after Cooling Down due to abnormal temperature',
            '02' : 'Invalid RS-232C Command',
            '24' : 'Power Save/Cooling Down in process',
            '04' : 'Power Save',
            '21' : 'Cooling Down in process after turned Off due to lamp failure',
            '81' : 'Standby after Cooling Down due to lamp failure',
            '2C' : 'Cooling Down in process after Power Off due to Shutter Management',
            '8C' : 'Standby after Cooling Down due to Shutter management',
        }

        PowerCmdString = 'CR STATUS\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = PowerStateNames[res[4:6]]
                if value in ['On', 'Off', 'Cooling Down', 'Warming Up', 'Invalid RS-232C Command']:
                    if value == 'Invalid RS-232C Command':
                        self.WriteStatus('DeviceStatus', value, qualifier)
                    else:
                        self.WriteStatus('Power', value, qualifier)
                        self.WriteStatus('DeviceStatus', 'Normal', qualifier)
                elif value in ['Power Failure', 'Power Save', 'Standby after Cooling Down due to lamp failure', 'Standby after Cooling Down due to abnormal temperature', 'Standby after Cooling Down due to Shutter management']:    
                    self.WriteStatus('Power', 'Off', qualifier)
                    self.WriteStatus('DeviceStatus', value, qualifier)
                elif value in ['Power Save/Cooling Down in process', 'Cooling Down in process after turned Off due to lamp failure', 'Cooling Down in process due to abnormal temperature', 'Cooling Down in process after Power Off due to Shutter Management']:    
                    self.WriteStatus('Power', 'Cooling Down', qualifier)
                    self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On'  : 'CF VMUTE ON\r',
            'Off' : 'CF VMUTE OFF\r',
            }

        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier): 

        VideoMuteStateNames = {
            'N' : 'On',
            'F' : 'Off',
           }

        VideoMuteCmdString = 'CR VMUTE\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = VideoMuteStateNames[res[5]]
                self.WriteVideoMute(value,qualifier,'Live')
            except (KeyError,IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 63
        }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'CF VOLUME {0:03d}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier): 

        VolumeCmdString = 'CR VOLUME\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = int(res[4:7])
                self.WriteVolume(value,qualifier,'Live')
            except (ValueError,IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '?\r'   : 'Unacceptable Command.',
            '102\r' : 'Directly specified value or values are out of range.',
            '103\r' : 'Command mismatched to Hardware (the command is for Optional function which is not implemented)',
            '201\r' : 'Incremented or decremented value or values are beyond upper or lower limits.',
            '301\r' : 'Not executable due to screen capturing in process. Prompting reissue of the command after a while.',
            '402\r' : 'Not executable due to PIN code in operation. Prompting reissue of the command after a while.',
            '101\r' : 'The function is not available in the selected Mode'
        }   

        if response in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
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
    
    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it was matched with device expectancy. 
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
