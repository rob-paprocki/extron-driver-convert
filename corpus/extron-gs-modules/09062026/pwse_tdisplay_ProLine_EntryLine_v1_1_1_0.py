from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

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
            'Pro Line': self.pwse_39_2065_Pro,
            'Entry Line': self.pwse_39_2065_Entry,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'BluRayDVD': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PCPower': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteFunctions': {'Status': {}},
            'Touch': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x40\x07(\x01\x48|\x02\x49|\x03\x4A)\xDD\xEE\xFF'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x82\x01(\x00\x83|\x01\x84)\xDD\xEE\xFF'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x40\x00(\x01\x41|\x00\x40)\xDD\xEE\xFF'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x34\x03(\x01\x38|\x00\x37)\xDD\xEE\xFF'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x81([\x03\x04\x0B\x06\x07\x05\x02\x08\x0A\x0C]\x00[\x84\x85\x8C\x87\x88\x86\x83\x89\x8B\x8D])\xDD\xEE\xFF'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x80(\x00\x00\x80|\x01\x00\x81)\xDD\xEE\xFF'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x83([\x00\x01\x02\x03]\x00[\x84\x85\x83\x86])\xDD\xEE\xFF'), self.__MatchPCPower, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x40\x12([\x00\x01][\x52\x53])\xDD\xEE\xFF'), self.__MatchTouch, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x82\x00([\x00-\xFF])[\x00-\xFF]\xDD\xEE\xFF'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x35\x03(\x01\x39|\x00\x38)\xDD\xEE\xFF'), self.__MatchVideoMute, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': b'\xAA\xBB\xCC\x08\x00\x00\x08\xDD\xEE\xFF',
            '4:3': b'\xAA\xBB\xCC\x08\x01\x00\x09\xDD\xEE\xFF',
            'PTP': b'\xAA\xBB\xCC\x08\x07\x00\x0F\xDD\xEE\xFF',
            'Auto': b'\xAA\xBB\xCC\x08\x04\x00\x0C\xDD\xEE\xFF'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xAA\xBB\xCC\x39\x07\x00\x40\xDD\xEE\xFF'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x02\x49': '16:9',
            '\x01\x48': '4:3',
            '\x03\x4A': 'PTP',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x03\x01\x00\x04\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x03\x01\x01\x05\xDD\xEE\xFF'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\xAA\xBB\xCC\x03\x03\x00\x06\xDD\xEE\xFF'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x00\x83': 'On',
            b'\x01\x84': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetBluRayDVD(self, value, qualifier):

        ValueStateValues = {
            'Play/Pause': b'\xAA\xBB\xCC\x04\x00\x00\x04\xDD\xEE\xFF',
            'Pause': b'\xAA\xBB\xCC\x04\x01\x00\x05\xDD\xEE\xFF',
            'Stop': b'\xAA\xBB\xCC\x04\x02\x00\x06\xDD\xEE\xFF',
            'Fast Forward': b'\xAA\xBB\xCC\x04\x03\x00\x07\xDD\xEE\xFF',
            'Fast Reverse': b'\xAA\xBB\xCC\x04\x04\x00\x08\xDD\xEE\xFF',
            'Previous Chapter': b'\xAA\xBB\xCC\x04\x05\x00\x09\xDD\xEE\xFF',
            'Next Chapter': b'\xAA\xBB\xCC\x04\x06\x00\x0A\xDD\xEE\xFF',
            '01': b'\xAA\xBB\xCC\x04\x07\x00\x0B\xDD\xEE\xFF',
            '02': b'\xAA\xBB\xCC\x04\x08\x00\x0C\xDD\xEE\xFF',
            '03': b'\xAA\xBB\xCC\x04\x09\x00\x0D\xDD\xEE\xFF',
            '04': b'\xAA\xBB\xCC\x04\x0A\x00\x0E\xDD\xEE\xFF',
            '05': b'\xAA\xBB\xCC\x04\x0B\x00\x0F\xDD\xEE\xFF',
            '06': b'\xAA\xBB\xCC\x04\x0C\x00\x10\xDD\xEE\xFF',
            '07': b'\xAA\xBB\xCC\x04\x0D\x00\x11\xDD\xEE\xFF',
            '08': b'\xAA\xBB\xCC\x04\x0E\x00\x12\xDD\xEE\xFF',
            '09': b'\xAA\xBB\xCC\x04\x0F\x00\x13\xDD\xEE\xFF',
            '00': b'\xAA\xBB\xCC\x04\x10\x00\x14\xDD\xEE\xFF',
            'Return': b'\xAA\xBB\xCC\x04\x12\x00\x16\xDD\xEE\xFF',
            'Eject': b'\xAA\xBB\xCC\x04\x13\x00\x17\xDD\xEE\xFF',
            'A>B': b'\xAA\xBB\xCC\x04\x14\x00\x18\xDD\xEE\xFF',
            'Zoom': b'\xAA\xBB\xCC\x04\x15\x00\x19\xDD\xEE\xFF',
            'Subtitle': b'\xAA\xBB\xCC\x04\x16\x00\x1A\xDD\xEE\xFF',
            'Display': b'\xAA\xBB\xCC\x04\x17\x00\x1B\xDD\xEE\xFF',
            'Audio': b'\xAA\xBB\xCC\x04\x18\x00\x1C\xDD\xEE\xFF',
            'Angle': b'\xAA\xBB\xCC\x04\x19\x00\x1D\xDD\xEE\xFF',
            'Menu': b'\xAA\xBB\xCC\x04\x1A\x00\x1E\xDD\xEE\xFF',
            'Title': b'\xAA\xBB\xCC\x04\x1B\x00\x1F\xDD\xEE\xFF',
            'Up': b'\xAA\xBB\xCC\x04\x1C\x00\x20\xDD\xEE\xFF',
            'Down': b'\xAA\xBB\xCC\x04\x1D\x00\x21\xDD\xEE\xFF',
            'Left': b'\xAA\xBB\xCC\x04\x1E\x00\x22\xDD\xEE\xFF',
            'Right': b'\xAA\xBB\xCC\x04\x1F\x00\x23\xDD\xEE\xFF',
            'Enter': b'\xAA\xBB\xCC\x04\x20\x00\x24\xDD\xEE\xFF',
            'GoTo': b'\xAA\xBB\xCC\x04\x21\x00\x25\xDD\xEE\xFF',
            'Repeat': b'\xAA\xBB\xCC\x04\x22\x00\x26\xDD\xEE\xFF',
            'Setup': b'\xAA\xBB\xCC\x04\x23\x00\x27\xDD\xEE\xFF',
            'Device': b'\xAA\xBB\xCC\x04\x24\x00\x28\xDD\xEE\xFF',
            'Program': b'\xAA\xBB\xCC\x04\x25\x00\x29\xDD\xEE\xFF',
            'Card': b'\xAA\xBB\xCC\x04\x26\x00\x2A\xDD\xEE\xFF'
        }

        BluRayDVDCmdString = ValueStateValues[value]
        self.__SetHelper('BluRayDVD', BluRayDVDCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x38\x04\x01\x3D\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x38\x04\x00\x3C\xDD\xEE\xFF'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = b'\xAA\xBB\xCC\x39\x00\x00\x39\xDD\xEE\xFF'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '\x01\x41': 'On',
            '\x00\x40': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\xAA\xBB\xCC\x07\x1C\x00\x23\xDD\xEE\xFF'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = b'\xAA\xBB\xCC\x34\x02\x00\x36\xDD\xEE\xFF'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '\x01\x38': 'On',
            '\x00\x37': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputNameValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xAA\xBB\xCC\x02\x00\x00\x02\xDD\xEE\xFF'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\xAA\xBB\xCC\x07\x1B\x00\x22\xDD\xEE\xFF',
            '1': b'\xAA\xBB\xCC\x07\x00\x00\x07\xDD\xEE\xFF',
            '2': b'\xAA\xBB\xCC\x07\x10\x00\x17\xDD\xEE\xFF',
            '3': b'\xAA\xBB\xCC\x07\x11\x00\x18\xDD\xEE\xFF',
            '4': b'\xAA\xBB\xCC\x07\x13\x00\x1A\xDD\xEE\xFF',
            '5': b'\xAA\xBB\xCC\x07\x14\x00\x1B\xDD\xEE\xFF',
            '6': b'\xAA\xBB\xCC\x07\x15\x00\x1C\xDD\xEE\xFF',
            '7': b'\xAA\xBB\xCC\x07\x17\x00\x1E\xDD\xEE\xFF',
            '8': b'\xAA\xBB\xCC\x07\x18\x00\x1F\xDD\xEE\xFF',
            '9': b'\xAA\xBB\xCC\x07\x19\x00\x20\xDD\xEE\xFF'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xAA\xBB\xCC\x07\x0D\x00\x14\xDD\xEE\xFF',
            'Up': b'\xAA\xBB\xCC\x07\x47\x00\x4E\xDD\xEE\xFF',
            'Down': b'\xAA\xBB\xCC\x07\x4D\x00\x54\xDD\xEE\xFF',
            'Left': b'\xAA\xBB\xCC\x07\x49\x00\x50\xDD\xEE\xFF',
            'Right': b'\xAA\xBB\xCC\x07\x4B\x00\x52\xDD\xEE\xFF',
            'Enter': b'\xAA\xBB\xCC\x07\x4A\x00\x51\xDD\xEE\xFF',
            'Back / Escape': b'\xAA\xBB\xCC\x07\x0A\x00\x11\xDD\xEE\xFF'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x01\x00\x00\x01\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x01\x01\x00\x02\xDD\xEE\xFF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xAA\xBB\xCC\x01\x02\x00\x03\xDD\xEE\xFF'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x00\x00\x80': 'On',
            b'\x01\x00\x81': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetPCPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x09\x01\x00\x0A\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x09\x00\x00\x09\xDD\xEE\xFF',
        }

        PCPowerCmdString = ValueStateValues[value]
        self.__SetHelper('PCPower', PCPowerCmdString, value, qualifier)

    def UpdatePCPower(self, value, qualifier):

        PCPowerCmdString = b'\xAA\xBB\xCC\x09\x02\x00\x0B\xDD\xEE\xFF'
        self.__UpdateHelper('PCPower', PCPowerCmdString, value, qualifier)

    def __MatchPCPower(self, match, tag):

        ValueStateValues = {
            b'\x00\x00\x83': 'On',
            b'\x01\x00\x84': 'Off',
            b'\x02\x00\x85': 'Sleep',
            b'\x03\x00\x86': 'Hibernate'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PCPower', value, None)

    def SetRemoteFunctions(self, value, qualifier):

        ValueStateValues = {
            'WIN': b'\xAA\xBB\xCC\x07\x0B\x00\x12\xDD\xEE\xFF',
            'Space': b'\xAA\xBB\xCC\x07\x46\x00\x4D\xDD\xEE\xFF',
            'Alt+Tab': b'\xAA\xBB\xCC\x07\x1D\x00\x24\xDD\xEE\xFF',
            'Alt+F4': b'\xAA\xBB\xCC\x07\x1F\x00\x26\xDD\xEE\xFF',
            'Display': b'\xAA\xBB\xCC\x07\x4C\x00\x53\xDD\xEE\xFF',
            'Home': b'\xAA\xBB\xCC\x07\x48\x00\x4F\xDD\xEE\xFF',
            'Backspace': b'\xAA\xBB\xCC\x07\x40\x00\x47\xDD\xEE\xFF',
            'PageUp': b'\xAA\xBB\xCC\x07\x42\x00\x49\xDD\xEE\xFF',
            'PageDown': b'\xAA\xBB\xCC\x07\x0F\x00\x16\xDD\xEE\xFF',
            'F1': b'\xAA\xBB\xCC\x07\x45\x00\x4C\xDD\xEE\xFF',
            'F2': b'\xAA\xBB\xCC\x07\x12\x00\x19\xDD\xEE\xFF',
            'F3': b'\xAA\xBB\xCC\x07\x51\x00\x58\xDD\xEE\xFF',
            'F4': b'\xAA\xBB\xCC\x07\x5B\x00\x62\xDD\xEE\xFF',
            'F5': b'\xAA\xBB\xCC\x07\x44\x00\x4B\xDD\xEE\xFF',
            'F6': b'\xAA\xBB\xCC\x07\x50\x00\x57\xDD\xEE\xFF',
            'F7': b'\xAA\xBB\xCC\x07\x43\x00\x4A\xDD\xEE\xFF',
            'F8': b'\xAA\xBB\xCC\x07\x1A\x00\x21\xDD\xEE\xFF',
            'F9': b'\xAA\xBB\xCC\x07\x04\x00\x0B\xDD\xEE\xFF',
            'F10': b'\xAA\xBB\xCC\x07\x59\x00\x60\xDD\xEE\xFF',
            'F11': b'\xAA\xBB\xCC\x07\x57\x00\x5E\xDD\xEE\xFF',
            'F12': b'\xAA\xBB\xCC\x07\x08\x00\x0F\xDD\xEE\xFF',
            'Shift+F10': b'\xAA\xBB\xCC\x07\x16\x00\x1D\xDD\xEE\xFF',
            'Red': b'\xAA\xBB\xCC\x07\x5C\x00\x63\xDD\xEE\xFF',
            'Green': b'\xAA\xBB\xCC\x07\x5D\x00\x64\xDD\xEE\xFF',
            'Yellow': b'\xAA\xBB\xCC\x07\x5E\x00\x65\xDD\xEE\xFF',
            'Blue': b'\xAA\xBB\xCC\x07\x5F\x00\x66\xDD\xEE\xFF'
        }

        RemoteFunctionsCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteFunctions', RemoteFunctionsCmdString, value, qualifier)

    def SetTouch(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x38\x07\x01\x40\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x38\x07\x00\x3F\xDD\xEE\xFF'
        }

        TouchCmdString = ValueStateValues[value]
        self.__SetHelper('Touch', TouchCmdString, value, qualifier)

    def UpdateTouch(self, value, qualifier):

        TouchCmdString = b'\xAA\xBB\xCC\x39\x12\x00\x4B\xDD\xEE\xFF'
        self.__UpdateHelper('Touch', TouchCmdString, value, qualifier)

    def __MatchTouch(self, match, tag):

        ValueStateValues = {
            '\x01\x53': 'On',
            '\x00\x52': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Touch', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\xAA\xBB\xCC\x07\x4E\x00\x55\xDD\xEE\xFF'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\xAA\xBB\xCC\x35\x02\x00\x37\xDD\xEE\xFF'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '\x01\x39': 'On',
            '\x00\x38': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            checksum = 0x03 + value
            VolumeCmdString = pack('>10B', 0xAA, 0xBB, 0xCC, 0x03, 0x00, value, checksum, 0xDD, 0xEE, 0xFF)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xAA\xBB\xCC\x03\x02\x00\x05\xDD\xEE\xFF'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = match.group(1)[0]
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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        

    def pwse_39_2065_Pro(self):
        
        self.InputNameValues = {
            'AV'      : b'\xAA\xBB\xCC\x02\x02\x00\x04\xDD\xEE\xFF', 
            'VGA 1'   : b'\xAA\xBB\xCC\x02\x03\x00\x05\xDD\xEE\xFF', 
            'VGA 2'   : b'\xAA\xBB\xCC\x02\x04\x00\x06\xDD\xEE\xFF', 
            'VGA 3'   : b'\xAA\xBB\xCC\x02\x0B\x00\x0D\xDD\xEE\xFF', 
            'HDMI 1'  : b'\xAA\xBB\xCC\x02\x06\x00\x08\xDD\xEE\xFF', 
            'HDMI 2'  : b'\xAA\xBB\xCC\x02\x07\x00\x09\xDD\xEE\xFF', 
            'HDMI 3'  : b'\xAA\xBB\xCC\x02\x05\x00\x07\xDD\xEE\xFF', 
            'PC'      : b'\xAA\xBB\xCC\x02\x08\x00\x0A\xDD\xEE\xFF', 
            'Android' : b'\xAA\xBB\xCC\x02\x0A\x00\x0C\xDD\xEE\xFF', 
            'Blu-ray' : b'\xAA\xBB\xCC\x02\x0C\x00\x0E\xDD\xEE\xFF'
        }
        
        self.InputStateValues = {
            b'\x02\x00\x83' : 'AV', 
            b'\x03\x00\x84' : 'VGA 1', 
            b'\x04\x00\x85' : 'VGA 2', 
            b'\x0B\x00\x8C' : 'VGA 3', 
            b'\x06\x00\x87' : 'HDMI 1', 
            b'\x07\x00\x88' : 'HDMI 2', 
            b'\x05\x00\x86' : 'HDMI 3', 
            b'\x08\x00\x89' : 'PC', 
            b'\x0A\x00\x8B' : 'Android', 
            b'\x0C\x00\x8D' : 'Blu-ray'
        }
        
    def pwse_39_2065_Entry(self):
        
        self.InputNameValues = {
            'AV'      : b'\xAA\xBB\xCC\x02\x02\x00\x04\xDD\xEE\xFF', 
            'VGA 1'   : b'\xAA\xBB\xCC\x02\x03\x00\x05\xDD\xEE\xFF', 
            'VGA 2'   : b'\xAA\xBB\xCC\x02\x04\x00\x06\xDD\xEE\xFF', 
            'VGA 3'   : b'\xAA\xBB\xCC\x02\x0B\x00\x0D\xDD\xEE\xFF', 
            'HDMI 1'  : b'\xAA\xBB\xCC\x02\x06\x00\x08\xDD\xEE\xFF', 
            'HDMI 2'  : b'\xAA\xBB\xCC\x02\x07\x00\x09\xDD\xEE\xFF', 
            'HDMI 3'  : b'\xAA\xBB\xCC\x02\x05\x00\x07\xDD\xEE\xFF', 
            'PC'      : b'\xAA\xBB\xCC\x02\x08\x00\x0A\xDD\xEE\xFF', 
        }
        
        self.InputStateValues = {
            b'\x02\x00\x83' : 'AV', 
            b'\x03\x00\x84' : 'VGA 1', 
            b'\x04\x00\x85' : 'VGA 2', 
            b'\x0B\x00\x8C' : 'VGA 3', 
            b'\x06\x00\x87' : 'HDMI 1', 
            b'\x07\x00\x88' : 'HDMI 2', 
            b'\x05\x00\x86' : 'HDMI 3', 
            b'\x08\x00\x89' : 'PC', 
        }        
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
        
        # check incoming data if it matched any expected data from device module
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