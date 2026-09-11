from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack

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
            'AutoFocus': {'Parameters': ['Device ID'], 'Status': {}},
            'Backlight': {'Parameters': ['Device ID'], 'Status': {}},
            'Focus': {'Parameters': ['Device ID', 'Focus Speed'], 'Status': {}},
            'Iris': {'Parameters': ['Device ID'], 'Status': {}},
            'PanTilt': {'Parameters': ['Device ID', 'Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetReset': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetSave': {'Parameters': ['Device ID'], 'Status': {}},
            'Zoom': {'Parameters': ['Device ID', 'Zoom Speed'], 'Status': {}},
        }
        
        self.DeviceIDStates = {
            '1': b'\x81',
            '2': b'\x82',
            '3': b'\x83',
            '4': b'\x84',
            '5': b'\x85',
            '6': b'\x86',
            '7': b'\x87'
        }

        self.MatchDeviceID = {
            b'\x90': '1',
            b'\xA0': '2',
            b'\xB0': '3',
            b'\xC0': '4',
            b'\xD0': '5',
            b'\xE0': '6',
            b'\xF0': '7'
        }

    def SetAutoFocus(self, value, qualifier):

        device_id = qualifier['Device ID']

        ValueStateValues = {
            'On':   b'\x02',
            'Off':  b'\x03'
        }

        if device_id in self.DeviceIDStates and value in ValueStateValues:
            AutoFocusCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x04\x38', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        device_id = qualifier['Device ID']

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        if device_id in self.DeviceIDStates:
            AutoFocusCmdString = b''.join([self.DeviceIDStates[device_id], b'\x09\x04\x38\xFF'])
            res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
            if res:
                try:
                    qualifier = {'Device ID': self.MatchDeviceID[res[0:1]]}
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('AutoFocus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Auto Focus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAutoFocus')
                
    def SetBacklight(self, value, qualifier):

        device_id = qualifier['Device ID']

        ValueStateValues = {
            'On':   b'\x02',
            'Off':  b'\x03'
        }

        if device_id in self.DeviceIDStates and value in ValueStateValues:
            BacklightCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x04\x33', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        device_id = qualifier['Device ID']

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        if device_id in self.DeviceIDStates:
            BacklightCmdString = b''.join([self.DeviceIDStates[device_id], b'\x09\x04\x33\xFF'])
            res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
            if res:
                try:
                    qualifier = {'Device ID': self.MatchDeviceID[res[0:1]]}
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('Backlight', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Backlight: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBacklight')

    def SetFocus(self, value, qualifier):

        device_id = qualifier['Device ID']
        focus_speed = qualifier['Focus Speed']

        ValueStateValues = {
            'Stop': 0x00,
            'Far':  0x20,
            'Near': 0x30
        }

        if device_id in self.DeviceIDStates and 0 <= focus_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                focus_speed = b'\x00'
            else:
                focus_speed = pack('>B', ValueStateValues[value] + focus_speed)

            FocusCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x04\x08', focus_speed, b'\xFF'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        device_id = qualifier['Device ID']

        ValueStateValues = {
            'Reset':    b'\x00',
            'Up':       b'\x02',
            'Down':     b'\x03'
        }

        if device_id in self.DeviceIDStates and value in ValueStateValues:
            IrisCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x04\x0B', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        device_id = qualifier['Device ID']
        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']

        ValueStateValues = {
            'Up':           b'\x03\x01',
            'Down':         b'\x03\x02',
            'Left':         b'\x01\x03',
            'Right':        b'\x02\x03',
            'Up Left':      b'\x01\x01',
            'Up Right':     b'\x02\x01',
            'Down Left':    b'\x01\x02',
            'Down Right':   b'\x02\x02',
            'Stop':         b'\x03\x03',
            'Home':         b'\x04',
            'Reset':        b'\x05'
        }

        if device_id in self.DeviceIDStates and 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 20 and value in ValueStateValues:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x06', ValueStateValues[value], b'\xFF'])
            else:
                PanTiltCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x06\x01', pack('>BB', pan_speed, tilt_speed), ValueStateValues[value], b'\xFF'])

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier if value == 'Reset' else 0)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        device_id = qualifier['Device ID']

        ValueStateValues = {
            'On':   b'\x02',
            'Off':  b'\x03'
        }

        if device_id in self.DeviceIDStates and value in ValueStateValues:
            PowerCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x04\x00', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier if value == 'On' else 0)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        device_id = qualifier['Device ID']

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off',
            b'\x04': 'Internal Power Circuit Error'
        }

        if device_id in self.DeviceIDStates:
            PowerCmdString = b''.join([self.DeviceIDStates[device_id], b'\x09\x04\x00\xFF'])
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    qualifier = {'Device ID': self.MatchDeviceID[res[0:1]]}
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        device_id = qualifier['Device ID']

        if device_id in self.DeviceIDStates and 0 <= int(value) <= 254:
            presetByte = pack('>B', int(value))
            PresetRecallCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x04\x3F\x02', presetByte, b'\xFF'])

            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        device_id = qualifier['Device ID']

        if device_id in self.DeviceIDStates and 0 <= int(value) <= 254:
            presetByte = pack('>B', int(value))
            PresetResetCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x04\x3F\x00', presetByte, b'\xFF'])

            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        device_id = qualifier['Device ID']

        if device_id in self.DeviceIDStates and 0 <= int(value) <= 254:
            presetByte = pack('>B', int(value))
            PresetSaveCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x04\x3F\x01', presetByte, b'\xFF'])

            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetZoom(self, value, qualifier):

        device_id = qualifier['Device ID']
        zoom_speed = qualifier['Zoom Speed']

        ValueStateValues = {
            'Stop': 0x00,
            'Tele': 0x20,
            'Wide': 0x30
        }

        if device_id in self.DeviceIDStates and 0 <= zoom_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                zoom_speed = b'\x00'
            else:
                zoom_speed = pack('>B', ValueStateValues[value] + zoom_speed)

            ZoomCmdString = b''.join([self.DeviceIDStates[device_id], b'\x01\x04\x07', zoom_speed, b'\xFF'])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) == 4:
            error_map = {
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
            'AutoFocus': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetReset': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}}
        }

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x02',
            'Off':  b'\x03'
        }

        if value in ValueStateValues:
            AutoFocusCmdString = b''.join([b'\x81\x01\x04\x38', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        AutoFocusCmdString = b'\x81\x09\x04\x38\xFF'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x02',
            'Off':  b'\x03'
        }

        if value in ValueStateValues:
            BacklightCmdString = b''.join([b'\x81\x01\x04\x33', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        BacklightCmdString = b'\x81\x09\x04\x33\xFF'
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        focus_speed = qualifier['Focus Speed']

        ValueStateValues = {
            'Stop': 0x00,
            'Far':  0x20,
            'Near': 0x30
        }

        if 0 <= focus_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                focus_speed = b'\x00'
            else:
                focus_speed = pack('>B', ValueStateValues[value] + focus_speed)

            FocusCmdString = b''.join([b'\x81\x01\x04\x08', focus_speed, b'\xFF'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset':    b'\x00',
            'Up':       b'\x02',
            'Down':     b'\x03'
        }

        if value in ValueStateValues:
            IrisCmdString = b''.join([b'\x81\x01\x04\x0B', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']

        ValueStateValues = {
            'Up':           b'\x03\x01',
            'Down':         b'\x03\x02',
            'Left':         b'\x01\x03',
            'Right':        b'\x02\x03',
            'Up Left':      b'\x01\x01',
            'Up Right':     b'\x02\x01',
            'Down Left':    b'\x01\x02',
            'Down Right':   b'\x02\x02',
            'Stop':         b'\x03\x03',
            'Home':         b'\x04',
            'Reset':        b'\x05'
        }

        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 20 and value in ValueStateValues:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = b''.join([b'\x81\x01\x06', ValueStateValues[value], b'\xFF'])
            else:
                PanTiltCmdString = b''.join([b'\x81\x01\x06\x01', pack('>BB', pan_speed, tilt_speed), ValueStateValues[value], b'\xFF'])

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x02',
            'Off':  b'\x03'
        }

        if value in ValueStateValues:
            PowerCmdString = b''.join([b'\x81\x01\x04\x00', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off',
            b'\x04': 'Internal Power Circuit Error'
        }

        PowerCmdString = b'\x81\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 254:
            presetByte = pack('>B', int(value))
            PresetRecallCmdString = b''.join([b'\x81\x01\x04\x3F\x02', presetByte, b'\xFF'])

            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 0 <= int(value) <= 254:
            presetByte = pack('>B', int(value))
            PresetResetCmdString = b''.join([b'\x81\x01\x04\x3F\x00', presetByte, b'\xFF'])

            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 254:
            presetByte = pack('>B', int(value))
            PresetSaveCmdString = b''.join([b'\x81\x01\x04\x3F\x01', presetByte, b'\xFF'])

            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetZoom(self, value, qualifier):

        zoom_speed = qualifier['Zoom Speed']

        ValueStateValues = {
            'Stop': 0x00,
            'Tele': 0x20,
            'Wide': 0x30
        }

        if 0 <= zoom_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                zoom_speed = b'\x00'
            else:
                zoom_speed = pack('>B', ValueStateValues[value] + zoom_speed)

            ZoomCmdString = b''.join([b'\x81\x01\x04\x07', zoom_speed, b'\xFF'])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) == 4:
            error_map = {
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
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

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()