from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
import re
import time

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = b'\x81'
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters':['Focus Speed'], 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': {'Parameters':['Zoom Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\x88'
        elif 1 <= int(value) <= 7:
            self._DeviceID = bytes([0x80+int(value)])
        else:
            print('Invalid Device ID Parameter.') 

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto'         : b'\x00', 
            'Manual'            : b'\x03', 
            'Shutter Priority'  : b'\x0A', 
            'Iris Priority'     : b'\x0B'
        }
        if value in ValueStateValues:
            AutoExposureCmdString = b''.join([self._DeviceID, b'\x01\x04\x39', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00  : 'Full Auto', 
            0x03  : 'Manual', 
            0x0A  : 'Shutter Priority', 
            0x0B  : 'Iris Priority'
        }

        AutoExposureCmdString = b''.join([self._DeviceID, b'\x09\x04\x39\xFF'])
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'Auto'      : b'\x02', 
            'Manual'    : b'\x03'
            }

        if value in ValueStateValues:
            AutoFocusCmdString = b''.join([self._DeviceID, b'\x01\x04\x38', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'Auto', 
            0x03 : 'Manual'
        }

        AutoFocusCmdString = b''.join([self._DeviceID, b'\x09\x04\x38\xFF'])
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\x02', 
            'Off'   : b'\x03'
        }

        if value in ValueStateValues:
            BacklightModeCmdString = b''.join([self._DeviceID, b'\x01\x04\x33', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Backlight', BacklightModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def SetFocus(self, value, qualifier):

        FocusConstraints = {
            'Min' : 0, 
            'Max' : 7
        }

        FocusState = {
            'Far'   : 0x20, 
            'Near'  : 0x30,
            'Stop'  : 0x00
        }

        FocusSpeed = int(qualifier['Focus Speed'])
        if FocusConstraints['Min'] <= FocusSpeed <= FocusConstraints['Max'] and value in FocusState:
            if value == 'Stop':
                FocusValue = 0x00
            else:
                FocusValue = FocusSpeed + FocusState[value]
            FocusCmdString = pack('>6B', int.from_bytes(self._DeviceID,"big"), 0x01, 0x04, 0x08, FocusValue, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x02', 
            'Down'  : b'\x03', 
            'Reset' : b'\x00'
        }

        if value in ValueStateValues:
            IrisCmdString = b''.join([self._DeviceID, b'\x01\x04\x0B', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        PanConstraints = {
            'Min' : 1,
            'Max' : 24
        }

        TiltConstraints = {
            'Min' : 1,
            'Max' : 24
        }

        PanTiltState = {
            'Up'            : 0x0301, 
            'Down'          : 0x0302, 
            'Left'          : 0x0103, 
            'Right'         : 0x0203, 
            'Up Left'       : 0x0101, 
            'Up Right'      : 0x0201, 
            'Down Left'     : 0x0102, 
            'Down Right'    : 0x0202, 
            'Stop'          : 0x0303, 
            'Home'          : 0x04, 
            'Reset'         : 0x05
        }
        
        PanSpeed = int(qualifier['Pan Speed'])
        TiltSpeed = int(qualifier['Tilt Speed'])
        if value in PanTiltState and PanConstraints['Min'] <= PanSpeed <= PanConstraints['Max'] and TiltConstraints['Min'] <= TiltSpeed <= TiltConstraints['Max']:
            if value in ('Home', 'Reset'):
                PanTiltCmdString = pack('>5B', int.from_bytes(self._DeviceID,"big"), 0x01, 0x06, PanTiltState[value], 0xFF)
            else:
                PanTiltCmdString = pack('>6BHB', int.from_bytes(self._DeviceID,"big"), 0x01, 0x06, 0x01, PanSpeed, TiltSpeed, PanTiltState[value], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\x02', 
            'Off'   : b'\x03'
        }

        if value in ValueStateValues:
            PowerCmdString = b''.join([self._DeviceID, b'\x01\x04\x00', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerState = {
            b'\x02' : 'On', 
            b'\x03' : 'Off'
            }

        PowerCmdString = b''.join([self._DeviceID, b'\x09\x04\x00\xFF'])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 255:
            PresetRecallCmdString = pack('>7B', int.from_bytes(self._DeviceID,"big"), 0x01, 0x04, 0x3F, 0x02 if 0 <= int(value) <= 127 else 0x12, int(value) if 0 <= int(value) <= 127 else int(value) - 128, 0xFF)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 255:
            PresetSaveCmdString = pack('>7B', int.from_bytes(self._DeviceID,"big"), 0x01, 0x04, 0x3F, 0x01 if 0 <= int(value) <= 127 else 0x11, int(value) if 0 <= int(value) <= 127 else int(value) - 128, 0xFF)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x02', 
            'Down'  : b'\x03', 
            'Reset' : b'\x00'
        }
        if value in ValueStateValues:
            ShutterCmdString = b''.join([self._DeviceID, b'\x01\x04\x0A', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto'              : b'\x00', 
            'Indoor'            : b'\x01', 
            'Outdoor'           : b'\x02', 
            'One Push WB'       : b'\x03', 
            'Auto Tracing WB'   : b'\x04', 
            'Manual'            : b'\x05',
            'Sodium Lamp'       : b'\x0C',
        }

        if value in ValueStateValues:
            WhiteBalanceCmdString = b''.join([self._DeviceID, b'\x01\x04\x35', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWhiteBalance')

    def UpdateWhiteBalance(self, value, qualifier):

        WhiteBalanceState = {
            b'\x00' : 'Auto', 
            b'\x01' : 'Indoor', 
            b'\x02' : 'Outdoor', 
            b'\x03' : 'One Push WB', 
            b'\x04' : 'Auto Tracing WB',
            b'\x05' : 'Manual',
            b'\x0C' : 'Sodium Lamp'
        }

        WhiteBalanceCmdString = b''.join([self._DeviceID, b'\x09\x04\x35\xFF'])
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = WhiteBalanceState[res[2:3]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ZoomConstraints = {
            'Min' : 0,
            'Max' : 7
        }

        ZoomState = {
            'Tele' : 0x20, 
            'Wide' : 0x30
        }

        ZoomSpeed = int(qualifier['Zoom Speed'])
        if ZoomConstraints['Min'] <= ZoomSpeed <= ZoomConstraints['Max']:
            if value == 'Stop':
                ZoomValue = 0x00
            else:
                ZoomValue = ZoomSpeed + ZoomState[value]
            ZoomCmdString = pack('>6B', int.from_bytes(self._DeviceID,"big"), 0x01, 0x04, 0x07, ZoomValue, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorCodes = {
            0x02 : 'Syntax Error',
            0x03 : 'Command Buffer Full',
            0x04 : 'Command Canceled',
            0x05 : 'No Socket',
            0x41 : 'Command Not Executable'
        }

        if response and len(response) == 4:
            address, errorByte, errorCode, terminator = unpack('>4B', response)
            errorByte = errorByte & 0x60
            if errorByte == 0x60:
                self.Error([sourceCmdName + ': ' + ErrorCodes[errorCode]])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == b'\x88':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'\x88':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
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

class DeviceEthernetClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters':['Focus Speed'], 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': {'Parameters':['Zoom Speed'], 'Status': {}},
        }

        self.start_sequence = False
        self.previous_sequence = 0
        self.last_sequence_reset = 0
                        
        self.matchError = re.compile(b'[\x90\xA0\xB0\xC0\xD0\xE0\xF0][\x60-\x62]([\x02-\x05\x41])\xFF')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID= value

    def ResetSequence(self, value, qualifier):
        self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')

    def next_sequence(self):
        if not self.start_sequence:
            ctime = time.monotonic()
            if ctime - self.last_sequence_reset > 10:
                self.last_sequence_reset = ctime
                self.ResetSequence( None, None)
            self.previous_sequence = 1
        else:
            if self.previous_sequence == 0xFFFFFFFF:
                self.previous_sequence = 0
            else:
                self.previous_sequence = self.previous_sequence + 1

        return '{0:08X}'.format(self.previous_sequence)
      
    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto'         : 0x00, 
            'Manual'            : 0x03, 
            'Shutter Priority'  : 0x0A, 
            'Iris Priority'     : 0x0B
        }

        if value in ValueStateValues:
            SeqNum = self.next_sequence()
            AutoExposureCmdString = b'\x01\x00\x00\x06' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF])
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00  : 'Full Auto', 
            0x03  : 'Manual', 
            0x0A  : 'Shutter Priority', 
            0x0B  : 'Iris Priority'
        }

        SeqNum = self.next_sequence()
        AutoExposureCmdString = b'\x01\x10\x00\x05' + bytes.fromhex(SeqNum) + bytes([0x81, 0x09, 0x04, 0x39, 0xFF])
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'Auto'      : 0x02, 
            'Manual'    : 0x03
        }

        if value in ValueStateValues:
            SeqNum = self.next_sequence()
            AutoFocusCmdString = b'\x01\x00\x00\x06' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'Auto', 
            0x03 : 'Manual'
        }

        SeqNum = self.next_sequence()
        AutoFocusCmdString = b'\x01\x10\x00\x05' + bytes.fromhex(SeqNum) + bytes([0x81, 0x09, 0x04, 0x38, 0xFF])
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On'    : 0x02, 
            'Off'   : 0x03
        }

        if value in ValueStateValues:
            SeqNum = self.next_sequence()
            BacklightModeCmdString = b'\x01\x00\x00\x06' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF])
            self.__SetHelper('Backlight', BacklightModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def SetFocus(self, value, qualifier):

        FocusConstraints = {
            'Min' : 0, 
            'Max' : 7
            }

        FocusState = {
            'Far'   : 0x20, 
            'Near'  : 0x30,
            'Stop'  : 0x00
            }

        FocusSpeed = int(qualifier['Focus Speed'])
        if FocusConstraints['Min'] <= FocusSpeed <= FocusConstraints['Max'] and value in FocusState:
            if value == 'Stop':
                FocusValue = 0x00
            else:
                FocusValue = FocusSpeed + FocusState[value]

            SeqNum = self.next_sequence()
            FocusCmdString = b'\x01\x00\x00\x06' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x08, FocusValue, 0xFF])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')
    
    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03, 
            'Reset' : 0x00
        }

        if value in ValueStateValues:
            SeqNum = self.next_sequence()
            IrisCmdString = b'\x01\x00\x00\x06' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF])
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        PanConstraints = {
            'Min' : 1,
            'Max' : 24
        }

        TiltConstraints = {
            'Min' : 1,
            'Max' : 24
        }

        PanTiltState = {
            'Up'            : [0x03, 0x01], 
            'Down'          : [0x03, 0x02], 
            'Left'          : [0x01, 0x03], 
            'Right'         : [0x02, 0x03], 
            'Up Left'       : [0x01, 0x01], 
            'Up Right'      : [0x02, 0x01], 
            'Down Left'     : [0x01, 0x02], 
            'Down Right'    : [0x02, 0x02], 
            'Stop'          : [0x03, 0x03],
            'Home'          : 0x04, 
            'Reset'         : 0x05
        }
        
        PanSpeed = int(qualifier['Pan Speed'])
        TiltSpeed = int(qualifier['Tilt Speed'])
        if value in PanTiltState and PanConstraints['Min'] <= PanSpeed <= PanConstraints['Max'] and TiltConstraints['Min'] <= TiltSpeed <= TiltConstraints['Max']:
            SeqNum = self.next_sequence()
            if value in ('Home', 'Reset'):
                PanTiltCmdString = b'\x01\x00\x00\x05' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x06, PanTiltState[value], 0xFF])
            else:
                PanTiltCmdString = b'\x01\x00\x00\x09' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x06, 0x01, PanSpeed, TiltSpeed, PanTiltState[value][0], PanTiltState[value][1], 0xFF])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : 0x02, 
            'Off'   : 0x03
        }

        if value in ValueStateValues:
            SeqNum = self.next_sequence()
            PowerCmdString = b'\x01\x00\x00\x06' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerState = {
            0x02 : 'On', 
            0x03 : 'Off'
            }

        SeqNum = self.next_sequence()
        PowerCmdString = b'\x01\x10\x00\x05' + bytes.fromhex(SeqNum) + bytes([0x81, 0x09, 0x04, 0x00, 0xFF])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 255:
            SeqNum = self.next_sequence()
            PresetRecallCmdString = b'\x01\x00\x00\x07' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x3F, 0x02 if 0 <= int(value) <= 127 else 0x12, int(value) if 0 <= int(value) <= 127 else int(value) - 128, 0xFF])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 255:
            SeqNum = self.next_sequence()
            PresetSaveCmdString = b'\x01\x00\x00\x07' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x3F, 0x01 if 0 <= int(value) <= 127 else 0x11, int(value) if 0 <= int(value) <= 127 else int(value) - 128, 0xFF])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03, 
            'Reset' : 0x00
        }

        if value in ValueStateValues:
            SeqNum = self.next_sequence()
            ShutterCmdString = b'\x01\x00\x00\x06' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF])
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')
            
    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto'              : 0x00, 
            'Indoor'            : 0x01, 
            'Outdoor'           : 0x02, 
            'One Push WB'       : 0x03, 
            'Auto Tracing WB'   : 0x04, 
            'Manual'            : 0x05,
            'Sodium Lamp'       : 0x0C,
        }

        if value in ValueStateValues:
            SeqNum = self.next_sequence()
            WhiteBalanceCmdString = b'\x01\x00\x00\x06' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x35, ValueStateValues[value], 0xFF])
            self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWhiteBalance')

    def UpdateWhiteBalance(self, value, qualifier):

        WhiteBalanceState = {
            0x00 : 'Auto', 
            0x01 : 'Indoor', 
            0x02 : 'Outdoor', 
            0x03 : 'One Push WB', 
            0x04 : 'Auto Tracing WB',
            0x05 : 'Manual',
            0x0C : 'Sodium Lamp'
        }

        SeqNum = self.next_sequence()
        WhiteBalanceCmdString = b'\x01\x10\x00\x05' + bytes.fromhex(SeqNum) + bytes([0x81, 0x09, 0x04, 0x35, 0xFF])
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = WhiteBalanceState[res[-2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ZoomConstraints = {
            'Min' : 0,
            'Max' : 7
        }

        ZoomState = {
            'Tele' : 0x20, 
            'Wide' : 0x30
        }

        ZoomSpeed = int(qualifier['Zoom Speed'])
        if ZoomConstraints['Min'] <= ZoomSpeed <= ZoomConstraints['Max']:
            if value == 'Stop':
                ZoomValue = 0x00
            else:
                ZoomValue = ZoomSpeed + ZoomState[value]
            SeqNum = self.next_sequence()
            ZoomCmdString = b'\x01\x00\x00\x06' + bytes.fromhex(SeqNum) + bytes([0x81, 0x01, 0x04, 0x07, ZoomValue, 0xFF])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x02': 'Syntax Error',
            b'\x03': 'Command buffer full',
            b'\x04': 'Command cancelled',
            b'\x05': 'No socket (to be cancelled)',
            b'\x41': 'Command not executable'
        }
        
        matchedInfo = re.search(self.matchError, response)
        if matchedInfo:
            self.Error(['{0} : {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[matchedInfo.group(1)])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.start_sequence = False
                return ''
            else:
                self.start_sequence = True
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.start_sequence = False
        self.previous_sequence = 0
        self.last_sequence_reset = 0

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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