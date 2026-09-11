# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import struct

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
        self.Models = {
            '55BDL3550Q': self.phil_10_5254_43_50_55_Q,
            '43BDL3550Q': self.phil_10_5254_43_50_55_Q,
            '50BDL3550Q': self.phil_10_5254_43_50_55_Q,
            '65BDL3550Q': self.phil_10_5254_65_75_86_Q,
            '75BDL3550Q': self.phil_10_5254_65_75_86_Q,
            '86BDL3550Q': self.phil_10_5254_65_75_86_Q,
            '32BDL4550D': self.phil_10_5254_D,
            '43BDL4550D': self.phil_10_5254_D,
            '50BDL4550D': self.phil_10_5254_D,
            '55BDL4550D': self.phil_10_5254_D,
            '65BDL4550D': self.phil_10_5254_D,
            '75BDL4550D': self.phil_10_5254_D,
            '86BDL4550D': self.phil_10_5254_D,
            '98BDL4550D': self.phil_10_5254_D,
            '49BDL2105X': self.phil_10_5254_X,
            '55BDL2105X': self.phil_10_5254_X,
            '65BDL6005X': self.phil_10_5254_X,
            '55BDL8007X': self.phil_10_5254_X
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Input': { 'Status': {}},
            'IRRemoteControlLock': { 'Status': {}},
            'KeypadLock': { 'Status': {}},
            'Power': { 'Status': {}},
            'TilingEnableStatus': { 'Status': {}},
            'TilingFrameCompStatus': { 'Status': {}},
            'TilingPositionStatus': { 'Status': {}},
            'TilingSet': {'Parameters':['Enable','Frame comp','Position','H Monitors','V Monitors'], 'Status': {}},
            'TilingVandHMonitorsStatus': {'Parameters':['Type'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': {'Parameters': ['Type'], 'Status': {}}
        }
                        
        self.update_delilen = {
            'AspectRatio':                  6,
            'AudioMute':                    6,
            'Input':                        9,
            'IRRemoteControlLock':          6,
            'KeypadLock':                   6,
            'Power':                        6,
            'TilingEnableStatus':           9,
            'TilingFrameCompStatus':        9,
            'TilingPositionStatus':         9,
            'TilingVandHMonitorsStatus':    9,
            'VideoMute':                    6,
            'Volume':                       7
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 255:
            self._DeviceID = int(value)
        else:
            self.Error(['Invalid Device ID Parameter.'])

    @property
    def GroupID(self):
        return self._GroupID

    @GroupID.setter
    def GroupID(self, value):
        if value == 'Off':
            self._GroupID = 0
        elif 1 <= int(value) <= 254:
            self._GroupID = int(value)
        else:
            self.Error(['Invalid Group ID Parameter.'])

    def checksum(self, string):

        checksum = 0
        for c in string:
            checksum ^= c

        return string + struct.pack('B', checksum)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full':     0x03,
            '4:3':      0x00,
            'Real':     0x02,
            '21:9':     0x04,
            'Custom':   0x01,
            '16:9':     0x06,
        }

        if value in ValueStateValues:
            AspectRatioCmdString = self.checksum(struct.pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x3A, ValueStateValues[value]))
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.checksum(struct.pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x3B))
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x03: 'Full',
                    0x00: '4:3',
                    0x02: 'Real',
                    0x04: '21:9',
                    0x01: 'Custom',
                    0x06: '16:9'
                }
                value = ValueStateValues[res[4]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00
            }

        if value in ValueStateValues:
            AudioMuteCmdString = self.checksum(struct.pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x47, ValueStateValues[value]))
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = self.checksum(struct.pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x46))
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x01: 'On',
                    0x00: 'Off'
                    }

                value = ValueStateValues[res[4]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = self.checksum(struct.pack('>6B', 0x07, self._DeviceID, self._GroupID, 0x70, 0x40, 0x00))
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        if value in self.SetInput_ValueStateValues:
            InputCmdString = self.checksum(struct.pack('>8B', 0x09, self._DeviceID, self._GroupID, 0xAC, self.SetInput_ValueStateValues[value], self.SetInput_ValueStateValues[value], 0x01, 0x00))
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.checksum(struct.pack('>4B', 0x05, self._DeviceID, self._GroupID, 0xAD))
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdateInput_ValueStateValues[res[4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetIRRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            'Unlock All':                       0x01,
            'Lock All':                         0x02,
            'Lock All but Power':               0x03,
            'Lock All but Volume':              0x04,
            'Primary (Master)':                 0x05,
            'Secondary (Daisy Chain PD)':       0x06,
            'Lock All Except Power & Volume':   0x07
        }

        if value in ValueStateValues:
            IRRemoteControlLockCmdString = self.checksum(struct.pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x1C, ValueStateValues[value]))
            self.__SetHelper('IRRemoteControlLock', IRRemoteControlLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRRemoteControlLock')

    def UpdateIRRemoteControlLock(self, value, qualifier):

        IRRemoteControlLockCmdString = self.checksum(struct.pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x1D))
        res = self.__UpdateHelper('IRRemoteControlLock', IRRemoteControlLockCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x01: 'Unlock All',
                    0x02: 'Lock All',
                    0x03: 'Lock All but Power',
                    0x04: 'Lock All but Volume',
                    0x05: 'Primary (Master)',
                    0x06: 'Secondary (Daisy Chain PD)',
                    0x07: 'Lock All Except Power & Volume'
                }
                value = ValueStateValues[res[4]]
                self.WriteStatus('IRRemoteControlLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Remote Control Lock: Invalid/unexpected response'])

    def SetKeypadLock(self, value, qualifier):

        ValueStateValues = {
            'Unlock All':                       0x01,
            'Lock All':                         0x02,
            'Lock All but Power':               0x03,
            'Lock All but Volume':              0x04,
            'Lock All Except Power & Volume':   0x07
        }

        if value in ValueStateValues:
            KeypadLockCmdString = self.checksum(struct.pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x1A, ValueStateValues[value]))
            self.__SetHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypadLock')

    def UpdateKeypadLock(self, value, qualifier):

        KeypadLockCmdString = self.checksum(struct.pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x1B))
        res = self.__UpdateHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x01: 'Unlock All',
                    0x02: 'Lock All',
                    0x03: 'Lock All but Power',
                    0x04: 'Lock All but Volume',
                    0x07: 'Lock All Except Power & Volume'
                }
                value = ValueStateValues[res[4]]
                self.WriteStatus('KeypadLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Keypad Lock: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x01
        }

        if value in ValueStateValues:
            PowerCmdString = self.checksum(struct.pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x18, ValueStateValues[value]))
            self.__SetHelper('Power', PowerCmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.checksum(struct.pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x19))
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02: 'On',
                    0x01: 'Off'
                }
                value = ValueStateValues[res[4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def UpdateTilingEnableStatus(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'Yes',
            0x00 : 'No'
        }

        HVMonitorsStates = {
            1  : '1',
            2  : '2',
            3  : '3',
            4  : '4',
            5  : '5',
            6  : '6',
            7  : '7',
            8  : '8',
            9  : '9',
            10 : '10'
        }

        TilingEnableStatusCmdString = self.checksum(struct.pack('>4B', 5, self._DeviceID, self._GroupID, 0x23))
        res = self.__UpdateHelper('TilingEnableStatus', TilingEnableStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-5]]   #TiltingEnable
                self.WriteStatus('TilingEnableStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Tiling Enable Status: Invalid/unexpected response'])
            try:
                value = ValueStateValues[res[-4]]   #TiltingFramecomp
                self.WriteStatus('TilingFrameCompStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Tiling Frame comp Status: Invalid/unexpected response'])
            try:
                value = str(res[-3])                #TilingPosition
                if 0 < int(value) <= 100:
                    self.WriteStatus('TilingPositionStatus', value, qualifier)
                else:
                    self.Error(['Tiling Position Status: Invalid/unexpected response'])
            except (KeyError, IndexError):
                self.Error(['Tiling Position Status: Invalid/unexpected response'])
            try:                                    #TilingVMonitorsStatus
                VMonitor = (int(int(res[-2])/10))+1
                if VMonitor == 11:
                    VMonitor = 10
                self.WriteStatus('TilingVandHMonitorsStatus', HVMonitorsStates[VMonitor], {'Type' : 'V Monitors'})
            except (KeyError, IndexError):
                self.Error(['Tiling V Monitors Status: Invalid/unexpected response'])
            try:                                    #TilingHMonitorsStatus
                HMonitor = int(res[-2])%10
                if HMonitor == 0 and int(int(res[-2])/10) == 10:
                    HMonitor = 10
                self.WriteStatus('TilingVandHMonitorsStatus', HVMonitorsStates[HMonitor], {'Type' : 'H Monitors'})
            except (KeyError, IndexError):
                self.Error(['Tiling H Monitors Status: Invalid/unexpected response'])

    def UpdateTilingFrameCompStatus(self, value, qualifier):

        self.UpdateTilingEnableStatus(value, qualifier)

    def UpdateTilingPositionStatus(self, value, qualifier):

        self.UpdateTilingEnableStatus(value, qualifier)

    def SetTilingSet(self, value, qualifier):

        FramecompStates = {
            'Yes'                 : 0x01,
            'No'                  : 0x00,
            'Keep Previous Value' : 0x02
        }

        PositionStates = {
            'Keep Previous Value' : 0x00,
        }

        HMonitorsStates = {
            'Keep Previous Value' : 0,
            '1'                   : 1,
            '2'                   : 2,
            '3'                   : 3,
            '4'                   : 4,
            '5'                   : 5,
            '6'                   : 6,
            '7'                   : 7,
            '8'                   : 8,
            '9'                   : 9,
            '10'                  : 10
        }

        VMonitorsStates = {
            'Keep Previous Value' : 0,
            '1'                   : 1,
            '2'                   : 2,
            '3'                   : 3,
            '4'                   : 4,
            '5'                   : 5,
            '6'                   : 6,
            '7'                   : 7,
            '8'                   : 8,
            '9'                   : 9,
            '10'                  : 10
        }

        EnableStateValues = {
            'Yes' : 0x01,
            'No'  : 0x00
        }

        EN = qualifier['Enable']
        FC = qualifier['Frame comp']
        POS = qualifier['Position']
        HM = qualifier['H Monitors']
        VM = qualifier['V Monitors']

        HVM = ((VMonitorsStates[VM]-1) * 10) + HMonitorsStates[HM]
        if HVM == -10:
            HVM = 0x00
        if POS in PositionStates:
            POS = PositionStates[POS]

        if FC in FramecompStates and 0<= int(POS) <=100 and HM in HMonitorsStates and VM in VMonitorsStates and EN in EnableStateValues:
            checksum = 0x09 ^ self._DeviceID ^ self._GroupID ^ 0x22 ^ EnableStateValues[EN] ^ FramecompStates[FC] ^ int(POS) ^ HVM
            TilingSetCmdString = struct.pack('>9B', 9, self._DeviceID, self._GroupID, 0x22,EnableStateValues[EN], FramecompStates[FC], int(POS), HVM & 255, checksum & 255)
            self.__SetHelper('TilingSet', TilingSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilingSet')
    def UpdateTilingVandHMonitorsStatus(self, value, qualifier):

        types = qualifier['Type']
        if types in ['H Monitors', 'V Monitors']:
            self.UpdateTilingEnableStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTilingVandHMonitorsStatus')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00
            }

        if value in ValueStateValues:
            VideoMuteCmdString = self.checksum(struct.pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x72, ValueStateValues[value]))
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = self.checksum(struct.pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x71))
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x01: 'On',
                    0x00: 'Off'
                    }
                
                value = ValueStateValues[res[4]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        TypeStates = [
            'Speaker Out',
            'Audio Out'
        ]
        type_ = qualifier['Type']

        opposite_type = 'Audio Out' if type_ == 'Speaker Out' else 'Speaker Out'
        opposite_volume = self.ReadStatus('Volume', {'Type': opposite_type})

        if opposite_volume is not None and type_ in TypeStates and 0 <= value <= 100 and 0 <= opposite_volume <= 100:
            if type_ == 'Speaker Out':
                VolumeCmdString = self.checksum(struct.pack('>6B', 0x07, self._DeviceID, self._GroupID, 0x44, value, opposite_volume))
            else:
                VolumeCmdString = self.checksum(struct.pack('>6B', 0x07, self._DeviceID, self._GroupID, 0x44, opposite_volume, value))

            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        TypeStates = [
            'Speaker Out',
            'Audio Out'
        ]
        type_ = qualifier['Type']

        if type_ in TypeStates:
            VolumeCmdString = self.checksum(struct.pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x45))
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[4])
                    if 0 <= value <= 100:
                        self.WriteStatus('Volume', value, {'Type': 'Speaker Out'})

                    value = int(res[5])
                    if 0 <= value <= 100:
                        self.WriteStatus('Volume', value, {'Type': 'Audio Out'})
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        error_map = {
            0x15: 'Not Acknowledge (NACK)',
            0x18: 'Not Available (NAV)'
        }

        if len(response) >= 6:
            if response[3] == 0x00 and response[4] in error_map:
                self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, error_map[response[4]])])
                return b''

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=self.update_delilen[command])
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

    def phil_10_5254_43_50_55_Q(self):

        self.SetInput_ValueStateValues = {
            'HDMI 1':       0x0D,
            'HDMI 2':       0x06,
            'DVI-D':        0x0E,
            'VGA':          0x05,
            'USB 1':        0x0C,
            'USB 2':        0x08,
            'OPS':          0x0B,
            'Media Player': 0x16,
            'Browser':      0x10,
            'SmartCMS':     0x11,
            'PDF Player':   0x17,
            'Custom':       0x18,
        }

        self.UpdateInput_ValueStateValues = {
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0E: 'DVI-D',
            0x05: 'VGA',
            0x0C: 'USB 1',
            0x08: 'USB 2',
            0x0B: 'OPS',
            0x16: 'Media Player',
            0x10: 'Browser',
            0x11: 'SmartCMS',
            0x17: 'PDF Player',
            0x18: 'Custom',
        }

    def phil_10_5254_65_75_86_Q(self):

        self.SetInput_ValueStateValues = {
            'HDMI 1':       0x0D,
            'HDMI 2':       0x06,
            'HDMI 3':       0x0F,
            'DVI-D':        0x0E,
            'VGA':          0x05,
            'USB 1':        0x0C,
            'USB 2':        0x08,
            'OPS':          0x0B,
            'Media Player': 0x16,
            'Browser':      0x10,
            'SmartCMS':     0x11,
            'PDF Player':   0x17,
            'Custom':       0x18,
        }

        self.UpdateInput_ValueStateValues = {
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0F: 'HDMI 3',
            0x0E: 'DVI-D',
            0x05: 'VGA',
            0x0C: 'USB 1',
            0x08: 'USB 2',
            0x0B: 'OPS',
            0x16: 'Media Player',
            0x10: 'Browser',
            0x11: 'SmartCMS',
            0x17: 'PDF Player',
            0x18: 'Custom',
        }



    def phil_10_5254_D(self):

        self.SetInput_ValueStateValues = {
            'HDMI 1':       0x0D,
            'HDMI 2':       0x06,
            'HDMI 3':       0x0F,
            'DVI-D':        0x0E,
            'VGA':          0x05,
            'DisplayPort':  0x0A,
            'OPS':          0x0B,
            'Media Player': 0x16,
            'Browser':      0x10,
            'SmartCMS':     0x11,
            'PDF Player':   0x17,
            'Custom':       0x18,
        }

        self.UpdateInput_ValueStateValues = {
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0F: 'HDMI 3',
            0x0E: 'DVI-D',
            0x05: 'VGA',
            0x0A: 'DisplayPort',
            0x0B: 'OPS',
            0x16: 'Media Player',
            0x10: 'Browser',
            0x11: 'SmartCMS',
            0x17: 'PDF Player',
            0x18: 'Custom',
        }

    def phil_10_5254_X(self):

        self.SetInput_ValueStateValues = {
            'HDMI 1':      0x0D,
            'HDMI 2':      0x06,
            'DVI-D':       0x0E,
            'VGA':         0x05,
            'DisplayPort': 0x0A,
            'OPS':         0x0B,
        }

        self.UpdateInput_ValueStateValues = {
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0E: 'DVI-D',
            0x05: 'VGA',
            0x0A: 'DisplayPort',
            0x0B: 'OPS'
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