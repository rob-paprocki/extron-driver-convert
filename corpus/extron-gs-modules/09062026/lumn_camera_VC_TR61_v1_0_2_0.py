# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
import time

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
        self._DeviceID = 0x81
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutoFraming': { 'Status': {}},
            'AutoTracking': { 'Status': {}},
            'AutoTrackingBodySize': { 'Status': {}},
            'AutoTrackingHeadPosition': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'FramingPeopleCount': { 'Status': {}},
            'Gain': { 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetReset': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'TargetLostReaction': { 'Status': {}},
            'TrackingModes': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
            }
        
        self.start_sequence = False
        self.previous_sequence = 0
        self.last_sequence_reset = 0

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
            self.previous_sequence = (self.previous_sequence + 1) & 0xFFFFFFFF

        return pack('>I', self.previous_sequence)

    def set_header(self, commandstring):
        if self.ConnectionType == 'Serial':
            return commandstring
        else:
            return b'\x01\x00\x00' + pack('B', len(commandstring)) + self.next_sequence() + commandstring

    def get_header(self, commandstring):
        if self.ConnectionType == 'Serial':
            return commandstring
        else:
            return b'\x01\x10\x00' + pack('B', len(commandstring)) + self.next_sequence() + commandstring

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto':        0x00,
            'Manual':           0x03,
            'Shutter Priority': 0x0A,
            'Iris Priority':    0x0B,
            'White Board':      0x5F
        }

        if value in ValueStateValues:
            AutoExposureCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        AutoExposureCmdString = self.get_header(pack('>5B', self._DeviceID, 0x09, 0x04, 0x39, 0xFF))
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x00: 'Full Auto',
                    0x03: 'Manual',
                    0x0A: 'Shutter Priority',
                    0x0B: 'Iris Priority',
                    0x5F: 'White Board'
                    }

                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            AutoFocusCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = self.get_header(pack('>5B', self._DeviceID, 0x09, 0x04, 0x38, 0xFF))
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                        0x02: 'On',
                        0x03: 'Off'
                    }

                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetAutoFraming(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            AutoFramingCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x0B, 0x04, 0x02, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoFraming', AutoFramingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFraming')

    def SetAutoTracking(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            AutoTrackingCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x0B, 0x00, 0x00, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoTracking', AutoTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTracking')

    def SetAutoTrackingBodySize(self, value, qualifier):

        ValueStateValues = {
            'Full':     0x00,
            'Upper':    0x01
        }

        if value in ValueStateValues:
            AutoTrackingBodySizeCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x0B, 0x02, 0x01, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoTrackingBodySize', AutoTrackingBodySizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTrackingBodySize')

    def UpdateAutoTrackingBodySize(self, value, qualifier):

        AutoTrackingBodySizeCmdString = self.get_header(pack('>6B', self._DeviceID, 0x09, 0x0B, 0x02, 0x01, 0xFF))
        res = self.__UpdateHelper('AutoTrackingBodySize', AutoTrackingBodySizeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x00: 'Full',
                    0x01: 'Upper'
                    }
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoTrackingBodySize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Tracking Body Size: Invalid/unexpected response'])

    def SetAutoTrackingHeadPosition(self, value, qualifier):

        ValueStateValues = {
            'Low': 0x00,
            'Medium': 0x01,
            'High': 0x02
            }

        if value in ValueStateValues:
            AutoTrackingHeadPositionCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x0B, 0x00, 0x05, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoTrackingHeadPosition', AutoTrackingHeadPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTrackingHeadPosition')

    def UpdateAutoTrackingHeadPosition(self, value, qualifier):

        AutoTrackingHeadPositionCmdString = self.get_header(pack('>6B', self._DeviceID, 0x09, 0x0B, 0x00, 0x05, 0xFF))
        res = self.__UpdateHelper('AutoTrackingHeadPosition', AutoTrackingHeadPositionCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x00: 'Low',
                    0x01: 'Medium',
                    0x02: 'High'
                    }
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoTrackingHeadPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Tracking Head Position: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Far':  0x20,
            'Near': 0x30,
            'Stop': 0x00
        }

        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            FocusCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x08, speed, 0xFF))
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def UpdateFramingPeopleCount(self, value, qualifier):

        FramingPeopleCountCmdString = self.get_header(pack('>6B', self._DeviceID, 0x09, 0x0B, 0x04, 0x01, 0xFF))
        res = self.__UpdateHelper('FramingPeopleCount', FramingPeopleCountCmdString, value, qualifier)
        if res:
            try:
                value = int(''.join("{:X}".format(b) for b in res[-5:-1]), 16)
                if(0 <= value <= 65535):
                    self.WriteStatus('FramingPeopleCount', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Framing People Count: Invalid/unexpected response'])

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        if value in ValueStateValues:
            GainCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF))
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        if value in ValueStateValues:
            IrisCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF))
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up':           0x0301,
            'Down':         0x0302,
            'Left':         0x0103,
            'Right':        0x0203,
            'Up Left':      0x0101,
            'Up Right':     0x0201,
            'Down Left':    0x0102,
            'Down Right':   0x0202,
            'Stop':         0x0303,
            'Home':         0x04,
            'Reset':        0x05
        }

        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 24 and value in ValueStateValues:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = self.set_header(pack('>5B', self._DeviceID, 0x01, 0x06, ValueStateValues[value], 0xFF))
            else:
                PanTiltCmdString = self.set_header(pack('>6BHB', self._DeviceID, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF))

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            PowerCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF))
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.get_header(pack('>5B', self._DeviceID, 0x09, 0x04, 0x00, 0xFF))
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02: 'On',
                    0x03: 'Off'
                    }

                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            PresetRecallCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x02, int(value) - 1, 0xFF))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 1 <= int(value) <= 128:
            PresetResetCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x00, int(value) - 1, 0xFF))
            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            PresetSaveCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, int(value) - 1, 0xFF))
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        if value in ValueStateValues:
            ShutterCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF))
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetTargetLostReaction(self, value, qualifier):

        ValueStateValues = {
            'Center and Wide': 0x00,
            'Last Position': 0x01,
            'Start Position': 0x02
            }

        if value in ValueStateValues:
            TargetLostReactionCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x0B, 0x00, 0x04, ValueStateValues[value], 0xFF))
            self.__SetHelper('TargetLostReaction', TargetLostReactionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTargetLostReaction')

    def UpdateTargetLostReaction(self, value, qualifier):

        TargetLostReactionCmdString = self.get_header(pack('>6B', self._DeviceID, 0x09, 0x0B, 0x00, 0x04, 0xFF))
        res = self.__UpdateHelper('TargetLostReaction', TargetLostReactionCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x00: 'Center and Wide',
                    0x01: 'Last Position',
                    0x02: 'Start Position'
                    }

                value = ValueStateValues[res[2]]
                self.WriteStatus('TargetLostReaction', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Target Lost Reaction: Invalid/unexpected response'])

    def SetTrackingModes(self, value, qualifier):

        ValueStateValues = {
            'Everywhere': 0x00,
            'Stage': 0x01,
            'Partition': 0x02,
            'Auto Framing': 0x03,
            'Partition Framing': 0x04,
            'Center Stage': 0x05
            }

        if value in ValueStateValues:
            TrackingModesCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x0B, 0x00, 0x01, ValueStateValues[value], 0xFF))
            self.__SetHelper('TrackingModes', TrackingModesCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingModes')

    def UpdateTrackingModes(self, value, qualifier):

        TrackingModesCmdString = self.get_header(pack('>6B', self._DeviceID, 0x09, 0x0B, 0x00, 0x01, 0xFF))
        res = self.__UpdateHelper('TrackingModes', TrackingModesCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x00: 'Everywhere',
                    0x01: 'Stage',
                    0x02: 'Partition',
                    0x03: 'Auto Framing',
                    0x04: 'Partition Framing',
                    0x05: 'Center Stage'
                    }

                value = ValueStateValues[res[2]]
                self.WriteStatus('TrackingModes', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Tracking Modes: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }

        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            ZoomCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x07, speed, 0xFF))
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if self.ConnectionType != 'Serial' and len(response) > 8:
            response = response[8:]

        if response and len(response) >= 4 and response[1] not in (0x60, 0x61, 0x62):
            return response
        else:
            errors = {
                0x02: 'Syntax Error',
                0x03: 'Command Buffer Full',
                0x04: 'Command Cancelled',
                0x05: 'No Socket',
                0x41: 'Command Not Executable'
            }

            address, errorbyte, errorcode, terminator = unpack('>4B', response)
            self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, errors.get(errorcode, 'Unknown Error'))])
            return b''

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
                if self.ConnectionType != 'Serial':
                    self.start_sequence = False

                return ''
            else:
                if self.ConnectionType != 'Serial':
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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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