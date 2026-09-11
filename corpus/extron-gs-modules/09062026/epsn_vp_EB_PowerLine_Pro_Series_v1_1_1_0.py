from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog

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
        self.Debug = False
        self.Models = {
            'PowerLite Pro G5950': self.epsn_1_213_C,
            'PowerLite Pro G5650W': self.epsn_1_213_C,
            'EB-C450WH': self.epsn_1_213_C,
            'EB-C520XH': self.epsn_1_213_E,
            'PowerLite Pro G5750WU': self.epsn_1_213_B,
            'PowerLite Pro G5450WU': self.epsn_1_213_B,
            'EB-C400WU': self.epsn_1_213_B,
            'EB-C450WU': self.epsn_1_213_B,
            'PowerLite Pro G5900': self.epsn_1_213_A,
            'PowerLite Pro G5600': self.epsn_1_213_A,
            'EB-C520XB': self.epsn_1_213_A,
            'EB-C450XB': self.epsn_1_213_A,
            'EB-700KG': self.epsn_1_213_A,
            'EB-600KG': self.epsn_1_213_A,
            'PowerLite 4200W': self.epsn_1_213_F,
            'EB-G5800': self.epsn_1_213_D,
            'EB-G5500': self.epsn_1_213_D,
            'EB-C520XE': self.epsn_1_213_D,
            'EB-C450XE': self.epsn_1_213_D,
            'PowerLite 4300': self.epsn_1_213_D,
            'PowerLite 4100': self.epsn_1_213_D,
            'EB-G5650W': self.epsn_1_213_C,
            'EB-G5950': self.epsn_1_213_B,
            'EB-G5600': self.epsn_1_213_A,
            'EB-G5900': self.epsn_1_213_A,
            'EB-G5750WU': self.epsn_1_213_B,
            'EB-G5450WU': self.epsn_1_213_B,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'SplitScreen': { 'Status': {}},
            'SplitScreenLeftInput': { 'Status': {}},
            'SplitScreenMode': { 'Status': {}},
            'SplitScreenRightInput': { 'Status': {}},
            'SplitScreenSwap': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'ASPECT=([0-6]0)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'MUTE=(ON|OFF)\r'), self.__MatchAVMute, None)
            self.AddMatchString(compile(b'CCAP=(00|11|12)\r'), self.__MatchClosedCaption, None)
            self.AddMatchString(compile(b'(ERR=([0-1][0-9A-F])\r)'), self.__MatchDeviceStatus, None)
            self.AddMatchString(compile(b'FREEZE=(ON|OFF)\r'), self.__MatchFreeze, None)
            self.AddMatchString(compile(b'SOURCE=(11|14|21|24|30|45|41|42|B1|B4|52|53|1F|2F|BF|A0)\r'), self.__MatchInput, None)
            self.AddMatchString(compile(b'LUMINANCE=(00|01)\r'), self.__MatchLampMode, None)
            self.AddMatchString(compile(b'LAMP=([0-9]{1,4})\r'), self.__MatchLampUsage, None)
            self.AddMatchString(compile(b'PWR=(0[0-5])\r'), self.__MatchPower, None)
            self.AddMatchString(compile(b'VOL=([0-9]{1,3})\r'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'(ERR\r)'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):


        AspectRatioCmdString = 'ASPECT {0}\r'.format(self.AspectRatioStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        value = self.AspectRatioStateNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On':  'ON',
            'Off': 'OFF',
        }

        AVMuteCmdString = 'MUTE {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = 'MUTE?\r'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        ValueStateValues = {
            'ON':  'On',
            'OFF': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': '00',
            'CC1': '11',
            'CC2': '12',
        }

        ClosedCaptionCmdString = 'CCAP {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CCAP?\r'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ValueStateValues = {
            '00': 'Off',
            '11': 'CC1',
            '12': 'CC2',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'ERR?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Fan Error',
            '03': 'Lamp failure at power on',
            '04': 'High internal temperature error',
            '06': 'Lamp error',
            '07': 'Open Lamp cover door error',
            '08': 'Cinema filter error',
            '09': 'Electric dual-layered capacitor is disconnected',
            '0A': 'Auto iris error',
            '0B': 'Subsystem Error',
            '0C': 'Low air flow error',
            '0D': 'Air filter air flow sensor error',
            '0E': 'Power supply unit error (Ballast)',
            '0F': 'Shutter error',
            '10': 'Cooling system error (peltiert element)',
            '11': 'Cooling system error (Pump)',
            '12': 'Static iris error',
            '13': 'Power supply unit error (Disagreement of Ballast)',
            '14': 'Exhaust shutter error',
            '15': 'Obstacle detection error',
            '16': 'IF board discernment error',
        }

        try:
            value = ValueStateValues[match.group(2).decode()]
        except (KeyError, IndexError):
            value = 'Device in unknown error state'
            self.Error(['Device in unknown error state'])
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':  'ON',
            'Off': 'OFF',
        }

        FreezeCmdString = 'FREEZE {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'ON':  'On',
            'OFF': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):


        InputCmdString = 'SOURCE {0}\r'.format(self.InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):


        value = self.InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': '00',
            'Eco':    '01',
        }

        LampModeCmdString = 'LUMINANCE {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'LUMINANCE?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Eco',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'LAMP?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':     '35',
            'Down':   '36',
            'Left':   '37',
            'Right':  '38',
            'Enter':  '16',
            'Menu':   '03',
            'Escape': '05',
        }

        MenuNavigationCmdString = 'KEY {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  'ON',
            'Off': 'OFF',
        }

        PowerCmdString = 'PWR {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off',
            '04': 'Off',
            '05': 'Abnormal Standby',
            '02': 'Warmup',
            '03': 'Cooldown',
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSplitScreen(self, value, qualifier):

        ValueStateValues = {
            'On':  '01',
            'Off': '00',
        }

        SplitScreenCmdString = 'SPS 01 {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SplitScreen', SplitScreenCmdString, value, qualifier)
    def SetSplitScreenLeftInput(self, value, qualifier):

        SplitScreenLeftInputCmdString = 'SPS 03 {0}\r'.format(self.SplitScreenLeftInputModeStateValues[value])
        self.__SetHelper('SplitScreenLeftInput', SplitScreenLeftInputCmdString, value, qualifier)
    def SetSplitScreenMode(self, value, qualifier):

        ValueStateValues = {
            'Size 1': '00',
            'Size 2': '01',
            'Size 3': '02',
        }

        SplitScreenModeCmdString = 'SPS 02 {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SplitScreenMode', SplitScreenModeCmdString, value, qualifier)
    def SetSplitScreenRightInput(self, value, qualifier):

        SplitScreenRightInputCmdString = 'SPS 04 {0}\r'.format(self.SplitScreenRightInputModeStateValues[value])
        self.__SetHelper('SplitScreenRightInput', SplitScreenRightInputCmdString, value, qualifier)
    def SetSplitScreenSwap(self, value, qualifier):

        SplitScreenSwapCmdString = 'SPS 05\r'
        self.__SetHelper('SplitScreenSwap', SplitScreenSwapCmdString, value, qualifier)
    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 20,
        }

        VolumeStateTable = {
            0:  0,
            1:  12,
            2:  24,
            3:  36,
            4:  48,
            5:  60,  # Same scale as in legacy
            6:  73,
            7:  85,
            8:  97,
            9:  109,
            10: 121,
            11: 134,
            12: 146,
            13: 158,
            14: 170,
            15: 182,
            16: 195,
            17: 207,
            18: 219,
            19: 231,
            20: 243,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOL {0}\r'.format(VolumeStateTable[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOL?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(int(match.group(1).decode()) / 12)
        if value > 20:
            value = 20
        self.WriteStatus('Volume', value, None)

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

        self.Error(['An error occurred'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        if self.ConnectionType == 'Tcp':
            self.SetOnConnectedString( None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def epsn_1_213_A(self):

        self.AspectRatioStateValues = {
            'Normal': '00',
            '16:9':   '20',
            '4:3':    '10',
            'Auto':   '30',
            'Native': '60',
        }
        self.AspectRatioStateNames = {
            '00': 'Normal',
            '10': '4:3',
            '20': '16:9',
            '30': 'Auto',
            '60': 'Native',
        }

        self.InputStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'Computer 2 Auto':      '2F',
            'Computer 2 RGB':       '21',
            'Computer 2 Component': '24',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
        }

        self.InputStateNames = {
            '1F': 'Computer 1 Auto',
            '11': 'Computer 1 RGB',
            '14': 'Computer 1 Component',
            '2F': 'Computer 2 Auto',
            '21': 'Computer 2 RGB',
            '24': 'Computer 2 Component',
            'BF': 'BNC Auto',
            'B1': 'BNC RGB',
            'B4': 'BNC Component',
            '30': 'HDMI',
            '41': 'Video 2',
            '45': 'Video 1',
            '42': 'S-Video',
        }

        self.SplitScreenLeftInputModeStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'Computer 2 Auto':      '2F',
            'Computer 2 RGB':       '21',
            'Computer 2 Component': '24',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
        }

        self.SplitScreenRightInputModeStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'Computer 2 Auto':      '2F',
            'Computer 2 RGB':       '21',
            'Computer 2 Component': '24',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
        }




    def epsn_1_213_B(self):  # WXGA/WU

        self.AspectRatioStateValues = {
            'Normal': '00',
            '16:9':   '20',
            'Auto':   '30',
            'Full':   '40',
            'Zoom':   '50',
            'Native': '60',
        }
        self.AspectRatioStateNames = {
            '00': 'Normal',
            '20': '16:9',
            '30': 'Auto',
            '40': 'Full',
            '50': 'Zoom',
            '60': 'Native',
        }

        self.InputStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
            'USB':                  '52',
            'LAN':                  '53',
            'DVI-D':                'A0',
        }

        self.InputStateNames = {
            '1F': 'Computer 1 Auto',
            '11': 'Computer 1 RGB',
            '14': 'Computer 1 Component',
            'BF': 'BNC Auto',
            'B1': 'BNC RGB',
            'B4': 'BNC Component',
            '30': 'HDMI',
            '41': 'Video 2',
            '42': 'S-Video',
            '45': 'Video 1',
            '52': 'USB',
            '53': 'LAN',
            'A0': 'DVI-D',
        }

        self.SplitScreenLeftInputModeStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
            'USB':                  '52',
            'LAN':                  '53',
            'DVI-D':                'A0',
        }

        self.SplitScreenRightInputModeStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
            'USB':                  '52',
            'LAN':                  '53',
            'DVI-D':                'A0',
        }




    def epsn_1_213_C(self):  # WXGA/G5650W G5950 C450WH C520XH

        self.AspectRatioStateValues = {
            'Normal': '00',
            '16:9':   '20',
            'Auto':   '30',
            'Full':   '40',
            'Zoom':   '50',
            'Native': '60',
        }
        self.AspectRatioStateNames = {
            '00': 'Normal',
            '20': '16:9',
            '30': 'Auto',
            '40': 'Full',
            '50': 'Zoom',
            '60': 'Native',
        }

        self.InputStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'Computer 2 Auto':      '2F',
            'Computer 2 RGB':       '21',
            'Computer 2 Component': '24',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
            'USB':                  '52',
            'LAN':                  '53',
        }

        self.InputStateNames = {
            '1F': 'Computer 1 Auto',
            '11': 'Computer 1 RGB',
            '14': 'Computer 1 Component',
            '2F': 'Computer 2 Auto',
            '21': 'Computer 2 RGB',
            '24': 'Computer 2 Component',
            'BF': 'BNC Auto',
            'B1': 'BNC RGB',
            'B4': 'BNC Component',
            '30': 'HDMI',
            '41': 'Video 2',
            '42': 'S-Video',
            '45': 'Video 1',
            '52': 'USB',
            '53': 'LAN',
        }

        self.SplitScreenLeftInputModeStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'Computer 2 Auto':      '2F',
            'Computer 2 RGB':       '21',
            'Computer 2 Component': '24',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
            'USB':                  '52',
            'LAN':                  '53',
        }

        self.SplitScreenRightInputModeStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'Computer 2 Auto':      '2F',
            'Computer 2 RGB':       '21',
            'Computer 2 Component': '24',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
            'USB':                  '52',
            'LAN':                  '53',
        }




    def epsn_1_213_D(self):  # G800/G5500/C520XE

        self.AspectRatioStateValues = {
            'Normal': '00',
            '16:9':   '20',
            '4:3':    '10',
            'Auto':   '30',
            'Native': '60',
        }
        self.AspectRatioStateNames = {
            '00': 'Normal',
            '10': '4:3',
            '20': '16:9',
            '30': 'Auto',
            '60': 'Native',
        }

        self.InputStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'Video 1':              '45',
        }

        self.InputStateNames = {
            '1F': 'Computer 1 Auto',
            '11': 'Computer 1 RGB',
            '14': 'Computer 1 Component',
            'BF': 'BNC Auto',
            'B1': 'BNC RGB',
            'B4': 'BNC Component',
            '45': 'Video 1',
        }




    def epsn_1_213_E(self):  # G5650W G5950 C450WH C520XH

        self.AspectRatioStateValues = {
            'Normal': '00',
            '16:9':   '20',
            '4:3':    '10',
            'Auto':   '30',
            'Native': '60',
        }
        self.AspectRatioStateNames = {
            '00': 'Normal',
            '10': '4:3',
            '20': '16:9',
            '30': 'Auto',
            '60': 'Native',
        }

        self.InputStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'Computer 2 Auto':      '2F',
            'Computer 2 RGB':       '21',
            'Computer 2 Component': '24',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
            'USB':                  '52',
            'LAN':                  '53',
        }

        self.InputStateNames = {
            '1F': 'Computer 1 Auto',
            '11': 'Computer 1 RGB',
            '14': 'Computer 1 Component',
            '2F': 'Computer 2 Auto',
            '21': 'Computer 2 RGB',
            '24': 'Computer 2 Component',
            'BF': 'BNC Auto',
            'B1': 'BNC RGB',
            'B4': 'BNC Component',
            '30': 'HDMI',
            '41': 'Video 2',
            '42': 'S-Video',
            '45': 'Video 1',
            '52': 'USB',
            '53': 'LAN',
        }

        self.SplitScreenLeftInputModeStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'Computer 2 Auto':      '2F',
            'Computer 2 RGB':       '21',
            'Computer 2 Component': '24',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
            'USB':                  '52',
            'LAN':                  '53',
        }

        self.SplitScreenRightInputModeStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'Computer 2 Auto':      '2F',
            'Computer 2 RGB':       '21',
            'Computer 2 Component': '24',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'HDMI':                 '30',
            'Video 1':              '45',
            'Video 2':              '41',
            'S-Video':              '42',
            'USB':                  '52',
            'LAN':                  '53',
        }




    def epsn_1_213_F(self):  # WXGA/G800/G5500/C520XE

        self.AspectRatioStateValues = {
            'Normal': '00',
            '16:9':   '20',
            'Auto':   '30',
            'Full':   '40',
            'Zoom':   '50',
            'Native': '60',
        }
        self.AspectRatioStateNames = {
            '00': 'Normal',
            '20': '16:9',
            '30': 'Auto',
            '40': 'Full',
            '50': 'Zoom',
            '60': 'Native'
        }

        self.InputStateValues = {
            'Computer 1 Auto':      '1F',
            'Computer 1 RGB':       '11',
            'Computer 1 Component': '14',
            'BNC Auto':             'BF',
            'BNC RGB':              'B1',
            'BNC Component':        'B4',
            'Video 1':              '45',
        }

        self.InputStateNames = {
            '1F': 'Computer 1 Auto',
            '11': 'Computer 1 RGB',
            '14': 'Computer 1 Component',
            'BF': 'BNC Auto',
            'B1': 'BNC RGB',
            'B4': 'BNC Component',
            '45': 'Video 1'
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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
