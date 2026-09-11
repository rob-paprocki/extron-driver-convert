from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack

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
        self._DeviceID = 1
        self._GroupID = 0
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Input': { 'Status': {}},
            'IRRemoteControlLock': { 'Status': {}},
            'KeypadLock': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'PIPCommand': {'Parameters': ['Position'], 'Status': {}},
            'PIPInput': {'Parameters': ['Quadrant 2', 'Quadrant 3', 'Quadrant 4'], 'Status': {}},
            'PIPInputQuadrant2Status': { 'Status': {}},
            'PIPInputQuadrant3Status': { 'Status': {}},
            'PIPInputQuadrant4Status': { 'Status': {}},
            'PIPModeStatus': { 'Status': {}},
            'PIPPositionStatus': { 'Status': {}},
            'Power': { 'Status': {}},
            'VolumeAudioOut': { 'Status': {}},
            'VolumeSpeaker': { 'Status': {}}
        }

        self.LenDict = {
            'AspectRatio':             6,
            'AudioMute':               6,
            'Input':                   9,
            'IRRemoteControlLock':     6,
            'KeypadLock':              6,
            'OperationHours':          7,
            'PIPInputQuadrant2Status': 9,
            'PIPInputQuadrant3Status': 9,
            'PIPInputQuadrant4Status': 9,
            'PIPModeStatus':           9,
            'Power':                   6,
            'VolumeAudioOut':          7,
            'VolumeSpeaker':           7
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        try:
            if value == 'Broadcast':
                self._DeviceID = 0
            elif 1 <= int(value) <= 255:
                self._DeviceID = int(value)
            else:
                self.Error(['Device ID Parameter is set to wrong value.'])
        except KeyError:
            self.Error(['Missing Device ID Parameter.'])
        except (ValueError, TypeError):
            self.Error(['Device ID Parameter is the wrong type.'])

    @property
    def GroupID(self):
        return self._GroupID

    @GroupID.setter
    def GroupID(self, value):
        try:
            if value == 'Off':
                self._GroupID = 0
            elif 1 <= int(value) <= 254:
                self._GroupID = int(value)
            else:
                self.Error(['Group ID Parameter is set to wrong value.'])
        except KeyError:
            self.Error(['Missing Group ID Parameter.'])
        except (ValueError, TypeError):
            self.Error(['Group ID Parameter is the wrong type.'])

    @staticmethod
    def cal_chk_sum(command_string):
        chk_sum = 0
        for i in range(0, len(command_string)):
            chk_sum = chk_sum ^ command_string[i]
        return chk_sum.to_bytes(1, 'big')
    
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal (4:3)':  0x00, 
            'Custom':        0x01, 
            'Real (1:1)':    0x02, 
            'Full':          0x03, 
            '21:9':          0x04, 
            'Dynamic':       0x05, 
            '16:9':          0x06,
        }

        if value in ValueStateValues:
            AspectRatioCmdString = pack('5B', 0x06, self._DeviceID, self._GroupID, 0x3A, ValueStateValues[value])
            ChkSum = self.cal_chk_sum(AspectRatioCmdString)
            AspectRatioCmdString = b''.join([AspectRatioCmdString, ChkSum])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Normal (4:3)',
            0x01: 'Custom',
            0x02: 'Real (1:1)',
            0x03: 'Full',
            0x04: '21:9',
            0x05: 'Dynamic',
            0x06: '16:9',
        }

        AspectRatioCmdString = pack('4B', 0x05, self._DeviceID, self._GroupID, 0x3B)
        ChkSum = self.cal_chk_sum(AspectRatioCmdString)
        AspectRatioCmdString = b''.join([AspectRatioCmdString, ChkSum])
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00,
        }

        if value in ValueStateValues:
            AudioMuteCmdString = pack('5B', 0x06, self._DeviceID, self._GroupID, 0x47, ValueStateValues[value])
            ChkSum = self.cal_chk_sum(AudioMuteCmdString)
            AudioMuteCmdString = b''.join([AudioMuteCmdString, ChkSum])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off',
        }

        AudioMuteCmdString = pack('4B', 0x05, self._DeviceID, self._GroupID, 0x46)
        ChkSum = self.cal_chk_sum(AudioMuteCmdString)
        AudioMuteCmdString = b''.join([AudioMuteCmdString, ChkSum])
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = pack('6B', 0x07, self._DeviceID, self._GroupID, 0x70, 0x40, 0x00)
        ChkSum = self.cal_chk_sum(AutoImageCmdString)
        AutoImageCmdString = b''.join([AutoImageCmdString, ChkSum])
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStates = {
            'VGA':          0x05,
            'HDMI 1':       0x0D,
            'HDMI 2':       0x06,
            'HDMI 3':       0x0F,
            'DisplayPort':  0x0A,
            'DVI-D':        0x0E,
            'Media Player': 0x16,
            'Browser':      0x10,
            'SmartCMS':     0x11,
            'PDF Player':   0x17,
            'Card OPS':     0x0B,
            'Custom':       0x18,
        }

        if value in InputStates:
            InputCmdString = pack('8B', 0x09, self._DeviceID, self._GroupID, 0xAC, InputStates[value], 0x09, 0x01, 0x00)
            ChkSum = self.cal_chk_sum(InputCmdString)
            InputCmdString = b''.join([InputCmdString, ChkSum])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputValues = {
            0x05: 'VGA',
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0F: 'HDMI 3',
            0x0A: 'DisplayPort',
            0x0E: 'DVI-D',
            0x16: 'Media Player',
            0x10: 'Browser',
            0x11: 'SmartCMS',
            0x17: 'PDF Player',
            0x0B: 'Card OPS',
            0x18: 'Custom',
        }

        InputCmdString = pack('4B', 0x05, self._DeviceID, self._GroupID, 0xAD)
        ChkSum = self.cal_chk_sum(InputCmdString)
        InputCmdString = b''.join([InputCmdString, ChkSum])
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputValues[res[4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetIRRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            'Unlock all':                      0x01, 
            'Lock all':                        0x02, 
            'Lock all but Power':              0x03, 
            'Lock all but Volume':             0x04, 
            'Primary (Master)':                0x05, 
            'Secondary (Daisy chain PD)':      0x06, 
            'Lock all except Power & Volume':  0x07,
        }

        if value in ValueStateValues:
            IRRemoteControlLockCmdString = pack('5B', 0x06, self._DeviceID, self._GroupID, 0x1C, ValueStateValues[value])
            ChkSum = self.cal_chk_sum(IRRemoteControlLockCmdString)
            IRRemoteControlLockCmdString = b''.join([IRRemoteControlLockCmdString, ChkSum])
            self.__SetHelper('IRRemoteControlLock', IRRemoteControlLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRRemoteControlLock')

    def UpdateIRRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Unlock all', 
            0x02: 'Lock all', 
            0x03: 'Lock all but Power', 
            0x04: 'Lock all but Volume', 
            0x05: 'Primary (Master)', 
            0x06: 'Secondary (Daisy chain PD)', 
            0x07: 'Lock all except Power & Volume',
        }

        IRRemoteControlLockCmdString = pack('4B', 0x05, self._DeviceID, self._GroupID, 0x1D)
        ChkSum = self.cal_chk_sum(IRRemoteControlLockCmdString)
        IRRemoteControlLockCmdString = b''.join([IRRemoteControlLockCmdString, ChkSum])
        res = self.__UpdateHelper('IRRemoteControlLock', IRRemoteControlLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('IRRemoteControlLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Remote Control Lock: Invalid/unexpected response'])

    def SetKeypadLock(self, value, qualifier):

        ValueStateValues = {
            'Unlock all':                     0x01, 
            'Lock all':                       0x02, 
            'Lock all but Power':             0x03, 
            'Lock all but Volume':            0x04, 
            'Lock all except Power & Volume': 0x07,
        }

        if value in ValueStateValues:
            KeypadLockCmdString = pack('5B', 0x06, self._DeviceID, self._GroupID, 0x1A, ValueStateValues[value])
            ChkSum = self.cal_chk_sum(KeypadLockCmdString)
            KeypadLockCmdString = b''.join([KeypadLockCmdString, ChkSum])
            self.__SetHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypadLock')

    def UpdateKeypadLock(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Unlock all', 
            0x02: 'Lock all', 
            0x03: 'Lock all but Power', 
            0x04: 'Lock all but Volume', 
            0x07: 'Lock all except Power & Volume',
        }

        KeypadLockCmdString = pack('4B', 0x05, self._DeviceID, self._GroupID, 0x1B)
        ChkSum = self.cal_chk_sum(KeypadLockCmdString)
        KeypadLockCmdString = b''.join([KeypadLockCmdString, ChkSum])
        res = self.__UpdateHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('KeypadLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Keypad Lock: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = pack('5B', 0x06, self._DeviceID, self._GroupID, 0x0F, 0x02)
        ChkSum = self.cal_chk_sum(OperationHoursCmdString)
        OperationHoursCmdString = b''.join([OperationHoursCmdString, ChkSum])
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>H', res[4:6])[0]
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPIPCommand(self, value, qualifier):

        PositionStates = {
            'Bottom Left':  0x00,
            'Top Left':     0x01,
            'Top Right':    0x02,
            'Bottom Right': 0x03,
            'Center':       0x04,
        }

        ValueStateValues = {
            'Off':              0x00,
            'On':               0x01,
            'Quick Swap':       0x03,
            'PBP 2 Window':     0x04,
            'PBP 3 Window':     0x05,
            'PBP 4 Window':     0x06,
            'PBP 3 Window - 1': 0x07,
            'PBP 3 Window - 2': 0x08,
            'PBP 4 Window - 1': 0x09,
            'SICP (Custom)':    0x0A,
        }

        pip_position = qualifier['Position']
        if value in ValueStateValues and pip_position in PositionStates:
            PIPCommandCmdString = pack('8B', 0x09, self._DeviceID, self._GroupID, 0x3C, ValueStateValues[value],
                                       PositionStates[pip_position], 0x00, 0x00)
            ChkSum = self.cal_chk_sum(PIPCommandCmdString)
            PIPCommandCmdString = b''.join([PIPCommandCmdString, ChkSum])
            self.__SetHelper('PIPCommand', PIPCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPCommand')

    def SetPIPInput(self, value, qualifier):

        InputStates = {
            'VGA':          0x05,
            'HDMI 1':       0x0D,
            'HDMI 2':       0x06,
            'HDMI 3':       0x0F,
            'DisplayPort':  0x0A,
            'DVI-D':        0x0E,
            'Media Player': 0x16,
            'Browser':      0x10,
            'SmartCMS':     0x11,
            'PDF Player':   0x17,
            'Card OPS':     0x0B,
            'Custom':       0x18,
        }

        quad_2 = qualifier['Quadrant 2']
        quad_3 = qualifier['Quadrant 3']
        quad_4 = qualifier['Quadrant 4']
        if all(inp in set(InputStates) for inp in [quad_2, quad_3, quad_4]):
            PIPInputCmdString = pack('8B', 0x09, self._DeviceID, self._GroupID, 0x84, 0xFD,
                                     InputStates[quad_2], InputStates[quad_3], InputStates[quad_4])
            ChkSum = self.cal_chk_sum(PIPInputCmdString)
            PIPInputCmdString = b''.join([PIPInputCmdString, ChkSum])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInputQuadrant2Status(self, value, qualifier):

        InputValues = {
            0x05: 'VGA',
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0F: 'HDMI 3',
            0x0A: 'DisplayPort',
            0x0E: 'DVI-D',
            0x16: 'Media Player',
            0x10: 'Browser',
            0x11: 'SmartCMS',
            0x17: 'PDF Player',
            0x0B: 'Card OPS',
            0x18: 'Custom',
        }

        PIPInputQuadrant2StatusCmdString = pack('4B', 0x05, self._DeviceID, self._GroupID, 0x85)
        ChkSum = self.cal_chk_sum(PIPInputQuadrant2StatusCmdString)
        PIPInputQuadrant2StatusCmdString = b''.join([PIPInputQuadrant2StatusCmdString, ChkSum])
        res = self.__UpdateHelper('PIPInputQuadrant2Status', PIPInputQuadrant2StatusCmdString, value, qualifier)
        if res:
            try:
                value = InputValues[res[5]]
                self.WriteStatus('PIPInputQuadrant2Status', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input Quadrant 2 Status: Invalid/unexpected response'])
            try:
                value = InputValues[res[6]]
                self.WriteStatus('PIPInputQuadrant3Status', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input Quadrant 3 Status: Invalid/unexpected response'])
            try:
                value = InputValues[res[7]]
                self.WriteStatus('PIPInputQuadrant4Status', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input Quadrant 4 Status: Invalid/unexpected response'])

    def UpdatePIPInputQuadrant3Status(self, value, qualifier):

        self.UpdatePIPInputQuadrant2Status(value, qualifier)

    def UpdatePIPInputQuadrant4Status(self, value, qualifier):

        self.UpdatePIPInputQuadrant2Status(value, qualifier)

    def UpdatePIPModeStatus(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Off', 
            0x01: 'On', 
            0x03: 'Quick Swap', 
            0x04: 'PBP 2 Window', 
            0x05: 'PBP 3 Window', 
            0x06: 'PBP 4 Window', 
            0x07: 'PBP 3 Window - 1', 
            0x08: 'PBP 3 Window - 2', 
            0x09: 'PBP 4 Window - 1', 
            0x0A: 'SICP (Custom)',
        }
        
        PIPPositionState = {
            0x00: 'Bottom Left', 
            0x01: 'Top Left', 
            0x02: 'Top Right', 
            0x03: 'Bottom Right', 
            0x04: 'Center',
        }
            
        PIPModeStatusCmdString = pack('4B', 0x05, self._DeviceID, self._GroupID, 0x3D)
        ChkSum = self.cal_chk_sum(PIPModeStatusCmdString)
        PIPModeStatusCmdString = b''.join([PIPModeStatusCmdString, ChkSum])
        res = self.__UpdateHelper('PIPModeStatus', PIPModeStatusCmdString, value, qualifier)
        if res:
            try:
                value = PIPPositionState[res[5]]
                self.WriteStatus('PIPPositionStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position Status: Invalid/unexpected response'])
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('PIPModeStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode Status: Invalid/unexpected response'])

    def UpdatePIPPositionStatus(self, value, qualifier):

        self.UpdatePIPModeStatus(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  0x02, 
            'Off': 0x01,
        }

        if value in ValueStateValues:
            PowerCmdString = pack('5B', 0x06, self._DeviceID, self._GroupID, 0x18, ValueStateValues[value])
            ChkSum = self.cal_chk_sum(PowerCmdString)
            PowerCmdString = b''.join([PowerCmdString, ChkSum])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On', 
            0x01: 'Off',
        }

        PowerCmdString = pack('4B', 0x05, self._DeviceID, self._GroupID, 0x19)
        ChkSum = self.cal_chk_sum(PowerCmdString)
        PowerCmdString = b''.join([PowerCmdString, ChkSum])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolumeAudioOut(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
        }

        spkr_val = self.ReadStatus('VolumeSpeaker', qualifier)
        if spkr_val is None:
            spkr_val = -1 
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 
                ValueConstraints['Min'] <= spkr_val <= ValueConstraints['Max']):
            VolumeAudioOutCmdString = pack('6B', 0x07, self._DeviceID, self._GroupID, 0x44, spkr_val, value)
            ChkSum = self.cal_chk_sum(VolumeAudioOutCmdString)
            VolumeAudioOutCmdString = b''.join([VolumeAudioOutCmdString, ChkSum])
            self.__SetHelper('VolumeAudioOut', VolumeAudioOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolumeAudioOut')

    def UpdateVolumeAudioOut(self, value, qualifier):

        VolumeAudioOutCmdString = pack('4B', 0x05, self._DeviceID, self._GroupID, 0x45)
        ChkSum = self.cal_chk_sum(VolumeAudioOutCmdString)
        VolumeAudioOutCmdString = b''.join([VolumeAudioOutCmdString, ChkSum])
        res = self.__UpdateHelper('VolumeAudioOut', VolumeAudioOutCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5])
                self.WriteStatus('VolumeAudioOut', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume Audio Out: Invalid/unexpected response'])
            try:
                value = int(res[4])
                self.WriteStatus('VolumeSpeaker', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume Speaker: Invalid/unexpected response'])

    def SetVolumeSpeaker(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
        }

        aud_val = self.ReadStatus('VolumeAudioOut', qualifier)
        if aud_val is None:
            aud_val = -1
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 
                ValueConstraints['Min'] <= aud_val <= ValueConstraints['Max']):
            VolumeSpeakerCmdString = pack('6B', 0x07, self._DeviceID, self._GroupID, 0x44, value, aud_val)
            ChkSum = self.cal_chk_sum(VolumeSpeakerCmdString)
            VolumeSpeakerCmdString = b''.join([VolumeSpeakerCmdString, ChkSum])
            self.__SetHelper('VolumeSpeaker', VolumeSpeakerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolumeSpeaker')

    def UpdateVolumeSpeaker(self, value, qualifier):

        self.UpdateVolumeAudioOut(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Not Acknowledge',
            b'\x18': 'Not Available',
        }

        if response[3:4] == b'\x00' and response[4:5] in DEVICE_ERROR_CODES:
            self.Error(['Command: {0}, Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=self.LenDict[command])
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