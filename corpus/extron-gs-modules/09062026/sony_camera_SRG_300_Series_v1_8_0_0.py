from extronlib.interface import EthernetClientInterface, EthernetServerInterfaceEx, SerialInterface
from extronlib.system import Wait, ProgramLog
from extronlib import event
import re, time
from struct import pack, unpack
from collections import deque

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
            'BacklightMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Focus': {'Parameters': ['Device ID', 'Focus Speed'], 'Status': {}},
            'Gain': {'Parameters': ['Device ID'], 'Status': {}},
            'Home': {'Parameters': ['Device ID'], 'Status': {}},
            'InformationDisplay': {'Parameters': ['Device ID'], 'Status': {}},
            'Iris': {'Parameters': ['Device ID'], 'Status': {}},
            'IrisDirect': {'Parameters': ['Device ID', 'XPos', 'YPos'], 'Status': {}},
            'IRReceiver': {'Parameters': ['Device ID'], 'Status': {}},
            'PanTilt': {'Parameters': ['Device ID', 'Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetReset': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetSave': {'Parameters': ['Device ID'], 'Status': {}},
            'ResetPanTilt': {'Parameters': ['Device ID'], 'Status': {}},
            'SetAddress': { 'Status': {}},
            'Zoom': {'Parameters': ['Device ID', 'Zoom Speed'], 'Status': {}},
        }

    def device_id(self, ID):
        return {
            '1':            0x81,
            '2':            0x82,
            '3':            0x83,
            '4':            0x84,
            '5':            0x85,
            '6':            0x86,
            '7':            0x87,
            'Broadcast':    0x88
        }.get(ID, None)

    def SetAutoFocus(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            'On' :  0x02,
            'Off':  0x03
        }

        if device_id and value in ValueStateValues:
            AutoFocusCmdString = pack('>6B', device_id, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        if device_id:
            AutoFocusCmdString = pack('>5B', device_id, 0x09, 0x04, 0x38, 0xFF)
            res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier) 
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('AutoFocus', value, qualifier) 
                except (KeyError, IndexError):
                    self.Error(['Auto Focus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAutoFocus') 

    def SetBacklightMode(self, value, qualifier):  

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            'On' : 0x02,
            'Off': 0x03
        }

        if device_id and value in ValueStateValues:
            BacklightModeCmdString = pack('>6B', device_id, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
            self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightMode')

    def UpdateBacklightMode(self, value, qualifier): 

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        if device_id:
            BacklightModeCmdString = pack('>5B', device_id, 0x09, 0x04, 0x33, 0xFF)
            res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('BacklightMode', value, qualifier) 
                except (KeyError, IndexError):
                    self.Error(['Backlight Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBacklightMode') 

    def SetFocus(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])
        focus_speed = qualifier['Focus Speed']

        ValueStateValues = {
            'Far' : 0x20,
            'Near': 0x30,
            'Stop': 0x00
        }

        if device_id and 0 <= focus_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                focus_speed = 0x00
            else:
                focus_speed += ValueStateValues[value]

            FocusCmdString = pack('>6B', device_id, 0x01, 0x04, 0x08, focus_speed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            'Up':       0x02, 
            'Down':     0x03, 
            'Reset':    0x00
        }

        if device_id and value in ValueStateValues:
            GainCmdString = pack('>6B', device_id, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetHome(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])

        if device_id:
            HomeCmdString = pack('>5B', device_id, 0x01, 0x06, 0x04, 0xFF)
            self.__SetHelper('Home', HomeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHome')

    def SetInformationDisplay(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            'On':   0x02, 
            'Off':  0x03
        }

        if device_id and value in ValueStateValues:
            InformationDisplayCmdString = pack('>7B', device_id, 0x01, 0x7E, 0x01, 0x18, ValueStateValues[value], 0xFF)
            self.__SetHelper('InformationDisplay', InformationDisplayCmdString, value, qualifier)  
        else:
            self.Discard('Invalid Command for SetInformationDisplay')

    def UpdateInformationDisplay(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        if device_id:
            InformationDisplayCmdString = pack('>6B', device_id, 0x09, 0x7E, 0x01, 0x18, 0xFF)
            res = self.__UpdateHelper('InformationDisplay', InformationDisplayCmdString, value, qualifier) 
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('InformationDisplay', value, qualifier) 
                except (KeyError, IndexError):
                    self.Error(['Information Display: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInformationDisplay') 

    def SetIris(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }
        
        if device_id and value in ValueStateValues:
            IrisCmdString = pack('>6B', device_id, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetIrisDirect(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])
        XPos = qualifier['XPos']
        YPos = qualifier['YPos']

        if device_id and 0 <= XPos <= 15 and 0 <= YPos <= 15:
            IrisDirectCmdString = pack('>9B', device_id, 0x01, 0x04, 0x4B, 0x00, 0x00, XPos, YPos, 0xFF)
            self.__SetHelper('IrisDirect', IrisDirectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIrisDirect')

    def SetIRReceiver(self, value, qualifier):  

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if device_id and value in ValueStateValues:
            IRReceiverCmdString = pack('>6B', device_id, 0x01, 0x06, 0x08, ValueStateValues[value], 0xFF)
            self.__SetHelper('IRReceiver', IRReceiverCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRReceiver')

    def SetPanTilt(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])
        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']

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

        if device_id and 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 23 and value in ValueStateValues:
            PanTiltCmdString = pack('>6BHB', device_id, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF) 
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):  

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            'On' :  0x02,
            'Off':  0x03
        }

        if device_id and value in ValueStateValues:
            PowerCmdString = pack('>6B', device_id, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier): 

        device_id = self.device_id(qualifier['Device ID'])

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        if device_id:
            PowerCmdString = pack('>5B', device_id, 0x09, 0x04, 0x00, 0xFF)
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier) 
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetPresetRecall(self, value, qualifier):  

        device_id = self.device_id(qualifier['Device ID'])

        if device_id and 1 <= int(value) <= 16:
            PresetRecallCmdString = pack('>7B', device_id, 0x01, 0x04, 0x3F, 0x02, int(value) - 1, 0xFF)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):  

        device_id = self.device_id(qualifier['Device ID'])

        if device_id and 1 <= int(value) <= 16:
            PresetResetCmdString = pack('>7B', device_id, 0x01, 0x04, 0x3F, 0x00, int(value) - 1, 0xFF)
            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):  

        device_id = self.device_id(qualifier['Device ID'])

        if device_id and 1 <= int(value) <= 16:
            PresetSaveCmdString = pack('>7B', device_id, 0x01, 0x04, 0x3F, 0x01, int(value) - 1, 0xFF)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetResetPanTilt(self, value, qualifier):  

        device_id = self.device_id(qualifier['Device ID'])

        if device_id:
            ResetPanTiltCmdString = pack('>5B', device_id, 0x01, 0x06, 0x05, 0xFF)
            self.__SetHelper('ResetPanTilt', ResetPanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResetPanTilt')

    def SetSetAddress(self, value, qualifier):

        SetAddressCmdString = pack('>4B', 0x88, 0x30, 0x01, 0xFF)
        self.__SetHelper('SetAddress', SetAddressCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        device_id = self.device_id(qualifier['Device ID'])
        zoom_speed = qualifier['Zoom Speed']

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }

        if device_id and 0 <= zoom_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                zoom_speed = 0x00
            else:
                zoom_speed += ValueStateValues[value]

            ZoomCmdString = pack('>6B', device_id, 0x01, 0x04, 0x07, zoom_speed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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

        if self.Unidirectional == 'True' or command == 'SetAddress' or qualifier['Device ID'] == 'Broadcast':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
   
        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast':
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

    Objects = {}

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self._ReceiveBuffer = b''
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'BacklightMode': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Gain': {'Status': {}},
            'Home': {'Status': {}},
            'InformationDisplay': {'Status': {}},
            'Iris': {'Status': {}},
            'IrisDirect': {'Parameters': ['XPos', 'YPos'], 'Status': {}},
            'IRReceiver': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetReset': {'Status': {}},
            'PresetSave': {'Status': {}},
            'ResetPanTilt': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
        }

        self.start_sequence = True
        self.previous_sequence = 0
        self.last_sequence_reset = time.monotonic()

        self.LastCommand = None
        self.cmdBuffer = deque(())
        self.cmdBusy = False

        DeviceEthernetClass.Objects[self.IPAddress] = self
        
    @classmethod
    def StartDataDispatch(cls):
        cls.server = EthernetServerInterfaceEx(52381, 'UDP')

        @event(cls.server, 'ReceiveData')
        def handleData(client, data):
            try:
                Object = cls.Objects[client.IPAddress]
            except KeyError:
                print('Unknown Device: {}'.format(client.IPAddress))
            Object.ReceiveDataHandler(data)

        if cls.server.StartListen() != 'Listening':
            print('Port unavailable: 52381')

    def ResetSequence(self, value, qualifier):

        self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')

    def next_sequence(self):

        if not self.start_sequence:
            ctime = time.monotonic()
            if ctime - self.last_sequence_reset > 10:
                self.last_sequence_reset = ctime
                self.ResetSequence(None, None)

            self.previous_sequence = 1
        else:
            self.previous_sequence = (self.previous_sequence + 1) & 0xFFFFFFFF

        return pack('>I', self.previous_sequence)

    def set_header(self, commandstring):

        return b'\x01\x00\x00' + pack('B', len(commandstring)) + self.next_sequence() + commandstring

    def get_header(self, commandstring):

        return b'\x01\x10\x00' + pack('B', len(commandstring)) + self.next_sequence() + commandstring

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            AutoFocusCmdString = self.set_header(pack('>6B', 0x81, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = self.get_header(pack('>5B', 0x81, 0x09, 0x04, 0x38, 0xFF))
        self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def MatchAutoFocus(self, data, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        try:
            value = ValueStateValues[data[2]]
            self.WriteStatus('AutoFocus', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            BacklightModeCmdString = self.set_header(pack('>6B', 0x81, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF))
            self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightMode')

    def UpdateBacklightMode(self, value, qualifier):

        BacklightModeCmdString = self.get_header(pack('>5B', 0x81, 0x09, 0x04, 0x33, 0xFF))
        self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def MatchBacklightMode(self, data, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        try:
            value = ValueStateValues[data[2]]
            self.WriteStatus('BacklightMode', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['Backlight Mode: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        focus_speed = qualifier['Focus Speed']

        ValueStateValues = {
            'Far': 0x20,
            'Near': 0x30,
            'Stop': 0x00
        }

        if 0 <= focus_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                focus_speed = 0x00
            else:
                focus_speed += ValueStateValues[value]

            FocusCmdString = self.set_header(pack('>6B', 0x81, 0x01, 0x04, 0x08, focus_speed, 0xFF))
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        if value in ValueStateValues:
            GainCmdString = self.set_header(pack('>6B', 0x81, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF))
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetHome(self, value, qualifier):

        HomeCmdString = self.set_header(pack('>5B', 0x81, 0x01, 0x06, 0x04, 0xFF))
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetInformationDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            InformationDisplayCmdString = self.set_header(pack('>7B', 0x81, 0x01, 0x7E, 0x01, 0x18, ValueStateValues[value], 0xFF))
            self.__SetHelper('InformationDisplay', InformationDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInformationDisplay')

    def UpdateInformationDisplay(self, value, qualifier):

        InformationDisplayCmdString = self.get_header(pack('>6B', 0x81, 0x09, 0x7E, 0x01, 0x18, 0xFF))
        self.__UpdateHelper('InformationDisplay', InformationDisplayCmdString, value, qualifier)

    def MatchInformationDisplay(self, data, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        try:
            value = ValueStateValues[data[2]]
            self.WriteStatus('InformationDisplay', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['Information Display: Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        if value in ValueStateValues:
            IrisCmdString = self.set_header(pack('>6B', 0x81, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF))
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetIrisDirect(self, value, qualifier):

        XPos = qualifier['XPos']
        YPos = qualifier['YPos']

        if 0 <= XPos <= 15 and 0 <= YPos <= 15:
            IrisDirectCmdString = self.set_header(pack('>9B', 0x81, 0x01, 0x04, 0x4B, 0x00, 0x00, XPos, YPos, 0xFF))
            self.__SetHelper('IrisDirect', IrisDirectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIrisDirect')

    def SetIRReceiver(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            IRReceiverCmdString = self.set_header(pack('>6B', 0x81, 0x01, 0x06, 0x08, ValueStateValues[value], 0xFF))
            self.__SetHelper('IRReceiver', IRReceiverCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRReceiver')

    def SetPanTilt(self, value, qualifier):

        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']

        ValueStateValues = {
            'Up': 0x0301,
            'Down': 0x0302,
            'Left': 0x0103,
            'Right': 0x0203,
            'Up Left': 0x0101,
            'Up Right': 0x0201,
            'Down Left': 0x0102,
            'Down Right': 0x0202,
            'Stop': 0x0303
        }

        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 23 and value in ValueStateValues:
            PanTiltCmdString = self.set_header(pack('>6BHB', 0x81, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF))
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            PowerCmdString = self.set_header(pack('>6B', 0x81, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF))
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.get_header(pack('>5B', 0x81, 0x09, 0x04, 0x00, 0xFF))
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def MatchPower(self, data, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        try:
            value = ValueStateValues[data[2]]
            self.WriteStatus('Power', value, qualifier)
        except (KeyError, IndexError):
            self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetRecallCmdString = self.set_header(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x02, int(value) - 1, 0xFF))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetResetCmdString = self.set_header(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x00, int(value) - 1, 0xFF))
            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetSaveCmdString = self.set_header(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x01, int(value) - 1, 0xFF))
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetResetPanTilt(self, value, qualifier):

        ResetPanTiltCmdString = self.set_header(pack('>5B', 0x81, 0x01, 0x06, 0x05, 0xFF))
        self.__SetHelper('ResetPanTilt', ResetPanTiltCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        zoom_speed = qualifier['Zoom Speed']

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }

        if 0 <= zoom_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                zoom_speed = 0x00
            else:
                zoom_speed += ValueStateValues[value]

            ZoomCmdString = self.set_header(pack('>6B', 0x81, 0x01, 0x04, 0x07, zoom_speed, 0xFF))
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, response):

        if len(response) > 8:
            response = response[8:]

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
                self.Error(['An error occurred: {}.'.format(errors.get(errorcode, 'Unknown Error'))])
                return ''

            return response

        return ''

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            self.__SendHelper(command, qualifier, commandstring, 'Set')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.__SendHelper(command, qualifier, commandstring, 'Update')

    def __SendHelper(self,command,qualifier=None,commandstring='',messageType=''):

        self.cmdBuffer.append((command,qualifier,commandstring, messageType))
        self.__ProcessSend()

    def __ProcessSend(self):
        '''
        If we are not waiting for a response (self.cmdBusy flag is free (False))
        '''
        if(not self.cmdBusy and len(self.cmdBuffer) > 0):
            self.cmdBusy = True
            #Set cmdWait timer to check for connection loss
            try:
                self._cmdWait.Restart()
            except AttributeError:
                self._cmdWait = Wait(1,self.ResponseCheck)
            try:
                self.LastCommand =  self.cmdBuffer.popleft()
            except:
                self.cmdBusy = False
                self._cmdWait.Cancel()
                self.LastCommand = None
                self.counter = 0
            else:
                try:
                    self.Send(self.LastCommand[2])
                except Exception as e:
                    print(repr(e))
                    

    def ResponseCheck(self):
        '''
        Checks for a response for the last command sent out (Set or Update)
        '''
        if (self.cmdBusy):
            self.cmdBusy = False
            if(self.connectionFlag):
                self.counter += 1
                if (self.counter > self.connectionCounter):
                    self.counter = 0
                    self.OnDisconnected()
            else:
                self.cmdBuffer.clear()

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.cmdBusy = False
        self.ResetSequence(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.start_sequence = False

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

    def ReceiveDataHandler(self, data):
        data = self.__CheckResponseForErrors(data)
        if data:
            if(self.LastCommand):
                command, qualifier, cmdString, messageType = self.LastCommand
                if(self._cmdWait):
                    self._cmdWait.Cancel()
                if messageType == 'Update':
                    try:
                        getattr(self, 'Match%s' % command)(data, qualifier)
                    except AttributeError:
                        print(command, 'does not support Match.')

                # Response recevied. Kill wait and call next command in the buffer
                self.cmdBusy = False
                self.LastCommand = None
                self.counter = 0
                self.__ProcessSend()

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