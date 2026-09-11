from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
        self.Models = {}
        self._DeviceID = 1


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'IRRemote': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'PIPSize': { 'Status': {}},
            'PIPSwap': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoWall': { 'Status': {}},
            'VideoWallMode': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x15(\x05|\x06|\x0B|\x01|\x18|\x10|\x09)[\x00-\xFF]'), self.__MatchAspectRatio, None)         
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x13(\x01|\x00)[\x00-\xFF]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x14(\x14|\x1E|\x18|\x0C|\x08|\x20|\x21|\x1F|\x22)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x36(\x00|\x05)[\x00-\xFF]'), self.__MatchIRRemote, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x70(\x01|\x00)[\x00-\xFF]'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x40(\x14|\x1E|\x18|\x0C|\x08|\x21|\x1F|\x22)[\x00-\xFF]'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x3C(\x01|\x00)[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x43(\x01|\x02|\x04|\x03)[\x00-\xFF]'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x42(\x06|\x08|\x04|\x05|\x09)[\x00-\xFF]'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\\x5C(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x4E([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 254
        elif value == '0':
            self._DeviceID = 255
        elif 1 <= int(value) <= 99:
            self._DeviceID = int(value)
        else:
            self.Error(['Device ID Out of Range'])

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
           'Zoom 1' : 0x05,
           'Zoom 2' : 0x06,
           '4:3' : 0x0B,
           '16:9' : 0x01,
           '4:3 (PC)': 0x18,
           '16:9 (PC)': 0x10,
           'Screen Fit': 0x09
           }

        cks = int(hex(0x15 + self.DeviceID + 0x01 + AspectRatioState[value])[-2:],16)
        AspectRatioCmdString = pack('>BBBBBB',0xAA, 0x15, self.DeviceID, 0x01, AspectRatioState[value], cks)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        cks = int(hex(0x15 + self.DeviceID)[-2:], 16)
        AspectRatioCmdString = pack('>BBBBB', 0xAA, 0x15, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioNames = {
            '\x05' : 'Zoom 1',
            '\x06' : 'Zoom 2',
            '\x0B' : '4:3',
            '\x01' : '16:9',
            '\x18' : '4:3 (PC)',
            '\x10' : '16:9 (PC)',
            '\x09' : 'Screen Fit'
            }
    
        value = AspectRatioNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
           'On' : 0x01,
           'Off' : 0x00
           }

        cks = int(hex(0x13 + self.DeviceID + 0x01 + AudioMuteState[value])[-2:],16)
        AudioMuteCmdString = pack('>BBBBBB', 0xAA, 0x13, self.DeviceID, 0x01, AudioMuteState[value], cks)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        cks = int(hex(0x13 + self.DeviceID)[-2:],16)
        AudioMuteCmdString = pack('>BBBBB', 0xAA, 0x13, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteNames = {
            '\x01' : 'On',
            '\x00' : 'Off'
            }
    
        value = AudioMuteNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        cks = int(hex(0x3D + self.DeviceID + 0x01)[-2:],16)
        AutoImageCmdString = pack('>BBBBBB', 0xAA, 0x3D, self.DeviceID, 0x01, 0x00, cks)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'On' : 0x01,
            'Off' : 0x00
            }

        cks = int(hex(0x5D + self.DeviceID + 0x01 + ExecutiveModeState[value])[-2:],16)
        ExecutiveModeCmdString = pack('>BBBBBB', 0xAA, 0x5D, self.DeviceID, 0x01, ExecutiveModeState[value], cks)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        cks = int(hex(0x5D + self.DeviceID)[-2:],16)
        ExecutiveModeCmdString = pack('>BBBBB', 0xAA, 0x5D, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeState = {
            '\x01' : 'On',
            '\x00' : 'Off'
            }

        value = ExecutiveModeState[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)
    
    def SetInput(self, value, qualifier):

        InputState = {
           'PC' : 0x14,
           'BNC' : 0x1E,
           'DVI' : 0x18,
           'AV' : 0x0C,
           'Component' : 0x08,
           'MagicInfo' : 0x20,
           'HDMI' : 0x21,
           }

        cks = int(hex(0x14 + self.DeviceID + 0x01 + InputState[value])[-2:],16)
        InputCmdString = pack('BBBBBB', 0xAA, 0x14, self.DeviceID, 0x01, InputState[value], cks)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        cks = int(hex(0x14 + self.DeviceID)[-2:],16)
        InputCmdString = pack('>BBBBB', 0xAA, 0x14, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
           '\x14' : 'PC',
           '\x1E' : 'BNC',
           '\x18' : 'DVI',
           '\x0C' : 'AV',
           '\x08' : 'Component',
           '\x20' : 'MagicInfo',
           '\x21' : 'HDMI',
           '\x1F' : 'DVI (Video)',
           '\x22' : 'HDMI (PC)'
           }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)
    
    def SetIRRemote(self, value, qualifier):

        IRRemoteState = {
           'Enable' : 0x01,
           'Disable' : 0x00
           }

        cks = int(hex(0x36 + self.DeviceID + 0x01 + IRRemoteState[value])[-2:],16)
        IRRemoteCmdString = pack('>BBBBBB', 0xAA, 0x36, self.DeviceID, 0x01, IRRemoteState[value], cks)
        self.__SetHelper('IRRemote', IRRemoteCmdString, value, qualifier)

    def UpdateIRRemote(self, value, qualifier):

        cks = int(hex(0x36 + self.DeviceID)[-2:],16)
        IRRemoteCmdString = pack('>BBBBB', 0xAA, 0x36, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('IRRemote', IRRemoteCmdString, value, qualifier)

    def __MatchIRRemote(self, match, tag):

        IRRemoteNames = {
            '\x00' : 'Enable',
            '\x05' : 'Disable'
            }
    
        value = IRRemoteNames[match.group(1).decode()]
        self.WriteStatus('IRRemote', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        OSDState = {
           'On' : 0x01,
           'Off' : 0x00
           }

        cks = int(hex(0x70 + self.DeviceID + 0x01 + OSDState[value])[-2:],16)
        OSDCmdString = pack('>BBBBBB', 0xAA, 0x70, self.DeviceID, 0x01, OSDState[value], cks)
        self.__SetHelper('OnScreenDisplay', OSDCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        cks = int(hex(0x70 + self.DeviceID)[-2:],16)
        OSDCmdString = pack('>BBBBB', 0xAA, 0x70, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('OnScreenDisplay', OSDCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        OSDState = {
            '\x01' : 'On',
            '\x00' : 'Off'
            }

        value = OSDState[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPIPInput(self, value, qualifier):

        PIPInputState = {
           'PC' : 0x14,
           'BNC' : 0x1E,
           'DVI' : 0x18,
           'AV' : 0x0C,
           'Component' : 0x08,
           'HDMI' : 0x21,
           }

        cks = int(hex(0x40 + self.DeviceID + 0x01 + PIPInputState[value])[-2:],16)
        PIPInputCmdString = pack('>BBBBBB', 0xAA, 0x40, self.DeviceID, 0x01, PIPInputState[value], cks)
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        cks = int(hex(0x40 + self.DeviceID)[-2:],16)
        PIPInputCmdString = pack('>BBBBB', 0xAA, 0x40, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        PIPInputState = {
           '\x14' : 'PC',
           '\x1E' : 'BNC',
           '\x18' : 'DVI',
           '\x0C' : 'AV',
           '\x08' : 'Component',
           '\x21' : 'HDMI',
           '\x1F' : 'DVI (Video)',
           '\x22' : 'HDMI (PC)'
            }

        value = PIPInputState[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        PIPModeState = {
           'On' : 0x01,
           'Off' : 0x00
           }

        cks = int(hex(0x3C + self.DeviceID + 0x01 + PIPModeState[value])[-2:],16)
        PIPModeCmdString = pack('>BBBBBB', 0xAA, 0x3C, self.DeviceID, 0x01, PIPModeState[value], cks)
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        cks = int(hex(0x3C + self.DeviceID)[-2:],16)
        PIPModeCmdString = pack('>BBBBB', 0xAA, 0x3C, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        PIPModeState = {
           '\x01' : 'On',
           '\x00' : 'Off'
           }

        value = PIPModeState[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        PIPPositionState = {
           'Upper Left' : 0x01,
           'Upper Right' : 0x02,
           'Lower Left' : 0x04,
           'Lower Right' : 0x03
           }

        cks = int(hex(0x43 + self.DeviceID + 0x01 + PIPPositionState[value])[-2:],16)
        PIPPositionCmdString = pack('>BBBBBB', 0xAA, 0x43, self.DeviceID, 0x01, PIPPositionState[value], cks)
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        cks = int(hex(0x43 + self.DeviceID)[-2:],16)
        PIPPositionCmdString = pack('>BBBBB', 0xAA, 0x43, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('PIPInput', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        PIPPositionState = {
            '\x01' : 'Upper Left',
            '\x02' : 'Upper Right',
            '\x04' : 'Lower Left',
            '\x03' : 'Lower Right'
            }

        value = PIPPositionState[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSize(self, value, qualifier):

        PIPSizeState = {
           'Large' : 0x06,
           'Small' : 0x08,
           'Double 1' : 0x04,
           'Double 2' : 0x05,
           'Double 3' : 0x09
           }

        cks = int(hex(0x42 + self.DeviceID + 0x01 + PIPSizeState[value])[-2:],16)
        PIPSizeCmdString = pack('>BBBBBB', 0xAA, 0x42, self.DeviceID, 0x01, PIPSizeState[value], cks)
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        cks = int(hex(0x42 + self.DeviceID)[-2:],16)
        PIPSizeCmdString = pack('>BBBBB', 0xAA, 0x42, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        PIPSizeState = {
           '\x06' : 'Large',
           '\x08' : 'Small',
           '\x04' : 'Double 1',
           '\x05' : 'Double 2',
           '\x09' : 'Double 3'
           }

        value = PIPSizeState[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        cks = int(hex(0x41 + self.DeviceID + 0x01)[-2:],16)
        PIPSwapCmdString = pack('>BBBBBB', 0xAA, 0x41, self.DeviceID, 0x01, 0x00, cks)
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        PowerState = {
           'On' : 0x01,
           'Off' : 0x00
           }

        cks = int(hex(0x11 + self.DeviceID + 0x01 + PowerState[value])[-2:],16)
        PowerCmdString = pack('>BBBBBB', 0xAA, 0x11, self.DeviceID, 0x01, PowerState[value], cks)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        cks = int(hex(0x11 + self.DeviceID)[-2:],16)
        PowerCmdString = pack('>BBBBB', 0xAA, 0x11, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '\x01' : 'On',
            '\x00' : 'Off'
            }


        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoWall(self, value, qualifier):

        VideoWallState = {
            'On'    : 0x01,
            'Off'   : 0x00
            }

        cks = int(hex(0x84 + self.DeviceID + 0x01 + VideoWallState[value])[-2:],16)
        VideoWallCmdString = pack('>BBBBBB', 0xAA, 0x84, self.DeviceID, 0x01, VideoWallState[value], cks)
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        cks = int(hex(0x84 + self.DeviceID)[-2:],16)
        VideoWallCmdString = pack('>BBBBB', 0xAA, 0x84, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        VideoWallState = {
            '\x01': 'On',
            '\x00': 'Off'
            }

        value = VideoWallState[match.group(1).decode()]
        self.WriteStatus('VideoWall', value, None)

    def SetVideoWallMode(self, value, qualifier):

        VideoWallModeState = {
            'Full'      : 0x01,
            'Natural'   : 0x00
            }

        cks = int(hex(0x5C + self.DeviceID + 0x01 + VideoWallModeState[value])[-2:],16)
        VideoWallModeCmdString = pack('>BBBBBB', 0xAA, 0x5C, self.DeviceID, 0x01, VideoWallModeState[value], cks)
        self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):

        cks = int(hex(0x5C + self.DeviceID)[-2:],16)
        VideoWallModeCmdString = pack('>BBBBB', 0xAA, 0x5C, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        VideoWallModeState = {
            '\x01': 'Full',
            '\x00': 'Natural'
        }

        value = VideoWallModeState[match.group(1).decode()]
        self.WriteStatus('VideoWallMode', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            cks = int(hex(0x12 + self.DeviceID + 0x01 + value)[-2:],16)
            VolumeCmdString = pack('>BBBBBB',0xAA, 0x12, self.DeviceID, 0x01, value, cks)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        cks = int(hex(0x12 + self.DeviceID)[-2:],16)
        VolumeCmdString = pack('>BBBBB', 0xAA, 0x12, self.DeviceID, 0x00, cks)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == 254: #Broadcast
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

        DEVICE_ERROR_CODES = {
            b'\x15' : 'AspectRatio',
            b'\x13' : 'AudioMute',
            b'\x3D' : 'AutoImage',
            b'\x5D' : 'ExecutiveMode',
            b'\x14' : 'Input',
            b'\x36' : 'IRRemote',
            b'\x70' : 'OnScreenDisplay',
            b'\x40' : 'PIPInput',
            b'\x3C' : 'PIPMode',
            b'\x43' : 'PIPPosition',
            b'\x42' : 'PIPSize',
            b'\x41' : 'PIPSwap',
            b'\x11' : 'Power',
            b'\x84' : 'VideoWall',
            b'\x5C' : 'VideoWallMode',
            b'\x12' : 'Volume'
            }

        if match.group(1) in DEVICE_ERROR_CODES:
            errorstring = 'Command: {0}, Error Code: {1}'.format(DEVICE_ERROR_CODES[match.group(1)], ord(match.group(2)))
        else:
            errorstring = 'Command: {0}, Error Code: {1}'.format('Unknown', ord(match.group(2)))
        self.Error([errorstring])

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
                result = re.search(regexString, self._ReceiveBuffer)
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

