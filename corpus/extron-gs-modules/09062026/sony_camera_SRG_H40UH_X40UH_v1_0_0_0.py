from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
            'AutoExposure': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Gain': { 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AutoExposureRegex = re.compile(b'\x90\x50(?P<value>\x00|\x03|\x0A|\x0B)\xFF')
            self.AutoFocusRegex = re.compile(b'\x90\x50(?P<value>\x02|\x03)\xFF')
            self.BacklightRegex = re.compile(b'\x90\x50(?P<value>\x02|\x03)\xFF')
            self.PowerRegex = re.compile(b'\x90\x50(?P<value>\x02|\x03)\xFF')

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto':        b'\x00',
            'Manual':           b'\x03',
            'Shutter Priority': b'\x0A',
            'Iris Priority':    b'\x0B'
            }

        if value in ValueStateValues:
            AutoExposureCmdString = b'\x81\x01\x04\x39' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        AutoExposureCmdString = b'\x81\x09\x04\x39\xFF'
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x00': 'Full Auto',
                    b'\x03': 'Manual',
                    b'\x0A': 'Shutter Priority',
                    b'\x0B': 'Iris Priority'
                    }

                valueMatch = self.AutoExposureRegex.match(res)
                value = ValueStateValues[valueMatch.group('value')]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x02',
            'Off': b'\x03'
            }

        if value in ValueStateValues:
            AutoFocusCmdString = b'\x81\x01\x04\x38' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = b'\x81\x09\x04\x38\xFF'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x02': 'On',
                    b'\x03': 'Off'
                    }

                valueMatch = self.AutoFocusRegex.match(res)
                value = ValueStateValues[valueMatch.group('value')]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x02',
            'Off': b'\x03'
            }

        if value in ValueStateValues:
            BacklightCmdString =  b'\x81\x01\x04\x33' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        BacklightCmdString = b'\x81\x09\x04\x33\xFF'
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x02': 'On',
                    b'\x03': 'Off'
                    }

                valueMatch = self.BacklightRegex.match(res)
                value = ValueStateValues[valueMatch.group('value')]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        focus_speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Stop': 00,
            'Far':  32,
            'Near': 48 
            }

        if value == 'Stop':
            FocusCmdString = b'\x81\x01\x04\x08\x00\xFF'
        elif 0 <= focus_speed <= 7 and value in ValueStateValues:
            FocusCmdString = b'\x81\x01\x04\x08' + (ValueStateValues[value] + focus_speed).to_bytes(1, 'big') + b'\xFF'
        else:
            self.Discard('Invalid Command for SetFocus')
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x00',
            'Up':    b'\x02',
            'Down':  b'\x03'
            }

        if value in ValueStateValues:
            GainCmdString = b'\x81\x01\x04\x0C' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x00',
            'Up':    b'\x02',
            'Down':  b'\x03'
            }

        if value in ValueStateValues:
            IrisCmdString = b'\x81\x01\x04\x0B' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up':         b'\x03\x01',
            'Down':       b'\x03\x02',
            'Left':       b'\x01\x03',
            'Right':      b'\x02\x03',
            'Up Left':    b'\x01\x01',
            'Up Right':   b'\x02\x01',
            'Down Left':  b'\x01\x02',
            'Down Right': b'\x02\x02',
            'Stop':       b'\x03\x03',
            'Home':       b'\x04',
            'Reset':      b'\x05'
            }

        if value == 'Home' or value == 'Reset':
            PanTiltCmdString = b'\x81\x01\x06' + ValueStateValues[value] + b'\xFF'
        elif 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 23 and value in ValueStateValues:
            PanTiltCmdString = b'\x81\x01\x06\x01' + pan_speed.to_bytes(1, 'big') + tilt_speed.to_bytes(1, 'big') + ValueStateValues[value] + b'\xFF' 
        else:
            self.Discard('Invalid Command for SetPanTilt')
            
        self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x02', 
            'Off': b'\x03'
            }

        if value in ValueStateValues:
            PowerCmdString = b'\x81\x01\x04\x00' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x81\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x02': 'On',
                    b'\x03': 'Off'
                    }

                valueMatch = self.PowerRegex.match(res)
                value = ValueStateValues[valueMatch.group('value')]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 64:
            PresetRecallCmdString = b'\x81\x01\x04\x3F\x02' + (int(value) - 1).to_bytes(1, 'big') + b'\xFF'
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 64:
            PresetSaveCmdString = b'\x81\x01\x04\x3F\x01' + (int(value) - 1).to_bytes(1, 'big') + b'\xFF'
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x00',
            'Up':    b'\x02',
            'Down':  b'\x03'
            }

        if value in ValueStateValues:
            ShutterCmdString = b'\x81\x01\x04\x0A' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetZoom(self, value, qualifier):

        zoom_speed = int(qualifier['Speed'])
        ValueStateValues = {
            'Stop': 00,
            'Tele': 32,
            'Wide': 48 
            }

        if value == 'Stop':
            ZoomCmdString = b'\x81\x01\x04\x07\x00\xFF'
        elif 0 <= zoom_speed <= 7 and value in ValueStateValues:
            ZoomCmdString = b'\x81\x01\x04\x07' + (ValueStateValues[value] + zoom_speed).to_bytes(1, 'big') + b'\xFF'
        else:
            self.Discard('Invalid Command for SetZoom')
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag = b'\xFF')
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag = b'\xFF')
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
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Gain': { 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

        self.start_sequence = False
        self.previous_sequence = 0
        self.last_sequence_reset = 0

        self.AutoExposureRegex = re.compile(b'\x90\x50(?P<value>\x00|\x03|\x0A|\x0B)\xFF')
        self.AutoFocusRegex = re.compile(b'\x90\x50(?P<value>\x02|\x03)\xFF')
        self.BacklightRegex = re.compile(b'\x90\x50(?P<value>\x02|\x03)\xFF')
        self.PowerRegex = re.compile(b'\x90\x50(?P<value>\x02|\x03)\xFF')

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
    
    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto':        b'\x00',
            'Manual':           b'\x03',
            'Shutter Priority': b'\x0A',
            'Iris Priority':    b'\x0B'
            }

        if value in ValueStateValues:
            AutoExposureCmdString = self.set_header(b'\x81\x01\x04\x39' + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        AutoExposureCmdString = self.get_header(b'\x81\x09\x04\x39\xFF')
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x00': 'Full Auto',
                    b'\x03': 'Manual',
                    b'\x0A': 'Shutter Priority',
                    b'\x0B': 'Iris Priority'
                    }

                valueMatch = self.AutoExposureRegex.match(res)
                value = ValueStateValues[valueMatch.group('value')]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x02',
            'Off': b'\x03'
            }

        if value in ValueStateValues:
            AutoFocusCmdString = self.set_header(b'\x81\x01\x04\x38' + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = self.get_header(b'\x81\x09\x04\x38\xFF')
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x02': 'On',
                    b'\x03': 'Off'
                    }

                valueMatch = self.AutoFocusRegex.match(res)
                value = ValueStateValues[valueMatch.group('value')]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x02',
            'Off': b'\x03'
            }

        if value in ValueStateValues:
            BacklightCmdString = self.set_header(b'\x81\x01\x04\x33' + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')
            
    def UpdateBacklight(self, value, qualifier):

        BacklightCmdString = self.get_header(b'\x81\x09\x04\x33\xFF')
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x02': 'On',
                    b'\x03': 'Off'
                    }

                valueMatch = self.BacklightRegex.match(res)
                value = ValueStateValues[valueMatch.group('value')]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        focus_speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Stop': 00,
            'Far':  32,
            'Near': 48
            }

        if value == 'Stop':
            FocusCmdString = self.set_header(b'\x81\x01\x04\x08\x00\xFF')
        elif 0 <= focus_speed <= 7 and value in ValueStateValues:
            FocusCmdString =  self.set_header(b'\x81\x01\x04\x08' + (ValueStateValues[value] + focus_speed).to_bytes(1, 'big') + b'\xFF')
        else:
            self.Discard('Invalid Command for SetFocus')
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x00',
            'Up':    b'\x02',
            'Down':  b'\x03'
            }

        if value in ValueStateValues:
            GainCmdString = self.set_header(b'\x81\x01\x04\x0C' + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x00',
            'Up':    b'\x02',
            'Down':  b'\x03'
            }

        if value in ValueStateValues:
            IrisCmdString = self.set_header(b'\x81\x01\x04\x0B' + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up':         b'\x03\x01',
            'Down':       b'\x03\x02',
            'Left':       b'\x01\x03',
            'Right':      b'\x02\x03',
            'Up Left':    b'\x01\x01',
            'Up Right':   b'\x02\x01',
            'Down Left':  b'\x01\x02',
            'Down Right': b'\x02\x02',
            'Stop':       b'\x03\x03',
            'Home':       b'\x04',
            'Reset':      b'\x05'
            }

        if value == 'Home' or value == 'Reset':
            PanTiltCmdString = self.set_header(b'\x81\x01\x06' + ValueStateValues[value] + b'\xFF')
        elif 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 23 and value in ValueStateValues:
            PanTiltCmdString = self.set_header(b'\x81\x01\x06\x01' + pan_speed.to_bytes(1, 'big') + tilt_speed.to_bytes(1, 'big') + ValueStateValues[value] + b'\xFF')
        else:
            self.Discard('Invalid Command for SetPanTilt')

        self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)

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
                value = ValueStateValues[valueMatch.group('value')]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 64:
            PresetRecallCmdString = self.set_header(b'\x81\x01\x04\x3F\x02' + (int(value) - 1).to_bytes(1, 'big') + b'\xFF')
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 64:
            PresetSaveCmdString = self.set_header(b'\x81\x01\x04\x3F\x01' + (int(value) - 1).to_bytes(1, 'big') + b'\xFF')
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x00',
            'Up':    b'\x02',
            'Down':  b'\x03'
            }

        if value in ValueStateValues:
            ShutterCmdString = self.set_header(b'\x81\x01\x04\x0A' + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetZoom(self, value, qualifier):

        zoom_speed = int(qualifier['Speed'])
        ValueStateValues = {
            'Stop': 00,
            'Tele': 32,
            'Wide': 48
            }

        if value == 'Stop':
            ZoomCmdString = self.set_header(b'\x81\x01\x04\x07\x00\xFF')
        elif 0 <= zoom_speed <= 7 and value in ValueStateValues:
            ZoomCmdString = self.set_header(b'\x81\x01\x04\x07' + (ValueStateValues[value] + zoom_speed).to_bytes(1, 'big') + b'\xFF')
        else:
            self.Discard('Invalid Command for SetZoom')
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

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