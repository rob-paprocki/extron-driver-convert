# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re
from struct import pack, unpack
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoCalibration': {'Parameters':['Device ID'], 'Status': {}},
            'Calibrate': {'Parameters':['Device ID'], 'Status': {}},
            'MappingMode': {'Parameters':['Device ID'], 'Status': {}},
            'PanTilt': {'Parameters':['Device ID','Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': {'Parameters':['Device ID'], 'Status': {}},
            'PresetRecall': {'Parameters':['Device ID'], 'Status': {}},
            'PresetSave': {'Parameters':['Device ID'], 'Status': {}}
        }

    def device_id(self, ID):
        return {
            '1':            0x81,
            '2':            0x82,
            '3':            0x83,
            '4':            0x84,
            '5':            0x85,
            '6':            0x86,
            '7':            0x87
        }.get(ID, None)
    
    def SetAutoCalibration(self, value, qualifier):

        ValueStateValues = {
            'On':   0x01,
            'Off':  0x00
            }

        device_id = self.device_id(qualifier['Device ID'])

        if device_id and value in ValueStateValues:
            AutoCalibrationCmdString = pack('>7B', device_id, 0x01, 0x04, 0x3F, ValueStateValues[value], 0x0D, 0xFF)
            self.__SetHelper('AutoCalibration', AutoCalibrationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoCalibration')

    def SetCalibrate(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])

        if device_id:
            CalibrateCmdString = pack('>7B', device_id, 0x01, 0x04, 0x3F,0x02, 0x12, 0xFF)
            self.__SetHelper('Calibrate', CalibrateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCalibrate')

    def SetMappingMode(self, value, qualifier):

        ValueStateValues = {
            'Split Dual Leg':   0x0A,
            'Single Leg':       0x0B,
            'Combine Dual Leg': 0x0C,
            'Pancake':          0x10
        }

        device_id = self.device_id(qualifier['Device ID'])

        if device_id and value in ValueStateValues:
            MappingModeCmdString = pack('>7B', device_id, 0x01, 0x04, 0x3F, 0x02, ValueStateValues[value], 0xFF)
            self.__SetHelper('MappingMode', MappingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMappingMode')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up':           0x0301,
            'Down':         0x0302,
            'Left':         0x0103,
            'Right':        0x0203,
            'Up Left':      0x0101,
            'Up Right':     0x0201,
            'Down Left':    0x0102,
            'Down Right':   0x0202,
            'Stop':         0x0303
            }

        device_id = self.device_id(qualifier['Device ID'])
        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']

        if device_id and 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 24 and value in ValueStateValues:
            PanTiltCmdString = pack('>5BHB', device_id, 0x01, 0x06, pan_speed, tilt_speed, ValueStateValues[value], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' :  0x02,
            'Off':  0x03
            }

        device_id = self.device_id(qualifier['Device ID'])

        if device_id and value in ValueStateValues:
            PowerCmdString = pack('>6B', device_id, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])

        if device_id:
            PowerCmdString = pack('>5B', device_id, 0x09, 0x04, 0x00, 0xFF)
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    ValueStateValues = {
                        0x02: 'On',
                        0x03: 'Off'
                        }

                    value = ValueStateValues[res[2]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])
        presetNum = int(value)

        if device_id and (1 <= presetNum <= 10 or 21 <= presetNum <= 40):
            PresetRecallCmdString = pack('>7B', device_id, 0x01, 0x04, 0x3F, 0x02, presetNum - 1, 0xFF)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
            
    def SetPresetSave(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])
        presetNum = int(value)

        if device_id and (1 <= presetNum <= 10 or 21 <= presetNum <= 40):
            PresetSaveCmdString = pack('>7B', device_id, 0x01, 0x04, 0x3F, 0x01, presetNum - 1, 0xFF)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) == 4:
            errors = {
                0x01: 'Message Length Error',
                0x02: 'Syntax Error',
                0x03: 'Command Buffer Full',
                0x04: 'Command Cancelled',
                0x05: 'No Socket',
                0x41: 'Command Not Executable'
            }

            address, errorbyte, errorcode, terminator = unpack('>4B', response)
            if errorbyte & 0x60 == 0x60:
                self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, errors.get(errorcode, 'Unknown Error'))])
                return b''

            return response

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
            'AutoCalibration': { 'Status': {}},
            'Calibrate': { 'Status': {}},
            'MappingMode': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            }

        self.start_sequence = False
        self.previous_sequence = 0
        self.last_sequence_reset = 0

        self.PowerRegex = re.compile(b'\x90\x50(\x02|\x03)\xFF')

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
        return b'\x01\x00\x00' + pack('B', len(commandstring)) + self.next_sequence() + commandstring

    def get_header(self, commandstring):
        return b'\x01\x10\x00' + pack('B', len(commandstring)) + self.next_sequence() + commandstring
    
    def SetAutoCalibration(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01',
            'Off':  b'\x00'
            }

        if value in ValueStateValues:
            AutoCalibrationCmdString = self.set_header(b'\x81\x01\x04\x3F' + ValueStateValues[value] + b'\x0D\xFF')
            self.__SetHelper('AutoCalibration', AutoCalibrationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoCalibration')

    def SetCalibrate(self, value, qualifier):

        CalibrateCmdString = self.set_header(b'\x81\x01\x04\x3F\x02\x12\xFF')
        self.__SetHelper('Calibrate', CalibrateCmdString, value, qualifier)

    def SetMappingMode(self, value, qualifier):

        ValueStateValues = {
            'Split Dual Leg':   b'\x0A',
            'Single Leg':       b'\x0B',
            'Combine Dual Leg': b'\x0C',
            'Pancake':          b'\x10'
            }

        if value in ValueStateValues:
            MappingModeCmdString = self.set_header(b'\x81\x01\x04\x3F\x02' + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('MappingMode', MappingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMappingMode')

    def SetPanTilt(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up':           b'\x03\x01',
            'Down':         b'\x03\x02',
            'Left':         b'\x01\x03',
            'Right':        b'\x02\x03',
            'Up Left':      b'\x01\x01',
            'Up Right':     b'\x02\x01',
            'Down Left':    b'\x01\x02',
            'Down Right':   b'\x02\x02',
            'Stop':         b'\x03\x03'
            }

        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 24 and value in ValueStateValues:
            PanTiltCmdString = self.set_header(b'\x81\x01\x06' + pan_speed.to_bytes(1, 'big') + tilt_speed.to_bytes(1, 'big') + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x02',
            'Off': b'\x03'
            }

        if value in ValueStateValues:
            PowerCmdString = self.set_header(b'\x81\x01\x04\x00' + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.get_header(b'\x81\x09\x04\x00\xFF')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x02': 'On',
                    b'\x03': 'Off'
                    }

                valueMatch = self.PowerRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        presetNum = int(value)
        if 1 <= presetNum <= 10 or 21 <= presetNum <= 40:
            PresetRecallCmdString = self.set_header(b'\x81\x01\x04\x3F\x02' + (presetNum - 1).to_bytes(1, 'big') + b'\xFF')
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        presetNum = int(value)
        if 1 <= presetNum <= 10 or 21 <= presetNum <= 40:
            PresetSaveCmdString = self.set_header(b'\x81\x01\x04\x3F\x01' + (presetNum - 1).to_bytes(1, 'big') + b'\xFF')
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if len(response) > 8:
            response = response[8:]
        if response and len(response) == 4:
            error_map = {
                0x01: 'Message Length Error',
                0x02: 'Syntax Error',
                0x03: 'Command Buffer Full',
                0x04: 'Command Cancelled',
                0x05: 'No Socket',
                0x41: 'Command Not Executable',
            }

            address, error_byte, error_code, terminator = unpack('>4B', response)
            if error_byte & 0x60 == 0x60:
                self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, error_map.get(error_code, 'Unknown Error'))])
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model =None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])