from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack
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
        self._DeviceID = b'\x81'
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutomaticTracking': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Home': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Action'], 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

        self.PrevSequence = 0
        self.StartSequence = 0
        self.LastResetTime = time.monotonic()

    @property
    def DeviceID(self, value):
        return self._DeviceID
        

    @DeviceID.setter
    def DeviceID(self, value):
       if 'Serial' in self.ConnectionType:
            if 1 <= int(value) <= 6:
                self._DeviceID = pack('B', 0x80 + int(value))
            else:
                print('Invalid Device ID Parameter.')

    def ResetSequence(self, value, qualifier):
        self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')

    def inc_sequence_number(self):
        if self.StartSequence == 0:
            ctime = time.monotonic()
            if ctime - self.LastResetTime > 15:
                self.LastResetTime = time.monotonic()
                self.ResetSequence( None, None)
            self.PrevSequence = 1
            sequence = b'\x00\x00\x00\x01'
        else:
            self.PrevSequence = self.PrevSequence + 1 if self.PrevSequence < 4294967295 else 0
            sequence = pack('>L', self.PrevSequence)
        return sequence

    def header_for_set(self, command_string):
        sequence = self.inc_sequence_number()
        command_string = b''.join([b'\x01\x00\x00', pack('B', len(command_string)), sequence, command_string])
        return command_string

    def header_for_get(self, command_string):
        sequence = self.inc_sequence_number()
        command_string = b''.join([b'\x01\x10\x00', pack('B', len(command_string)), sequence, command_string])
        return command_string
    
    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On'                : b'\x38\x02',
            'Off'               : b'\x38\x03',
            'One Push Trigger'  : b'\x18\x01'
        }

        if value in ValueStateValues:
            AutoFocusCmdString = self._DeviceID + b'\x01\x04' + ValueStateValues[value] + b'\xFF'
            if 'Serial' not in self.ConnectionType:
                AutoFocusCmdString = self.header_for_set(AutoFocusCmdString)
                self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On',
            0x03 : 'Off'
        }

        AutoFocusCmdString = self._DeviceID + b'\x09\x04\x38\xFF'
        if 'Serial' not in self.ConnectionType:
            AutoFocusCmdString = self.header_for_get(AutoFocusCmdString)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetAutomaticTracking(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x50',
            'Off' : b'\x51'
        }

        if value in ValueStateValues:
            AutomaticTrackingCmdString = self._DeviceID + b'\x01\x04\x3F\x02' + ValueStateValues[value] + b'\xFF'
            if 'Serial' not in self.ConnectionType:
                AutomaticTrackingCmdString = self.header_for_set(AutomaticTrackingCmdString)
            self.__SetHelper('AutomaticTracking', AutomaticTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomaticTracking')

    def UpdateAutomaticTracking(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On',
            0x03 : 'Off'
        }

        AutomaticTrackingCmdString = self._DeviceID + b'\x09\x08\x01\xFF'
        if 'Serial' not in self.ConnectionType:
            AutomaticTrackingCmdString = self.header_for_get(AutomaticTrackingCmdString)
        res = self.__UpdateHelper('AutomaticTracking', AutomaticTrackingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutomaticTracking', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Automatic Tracking: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far' : 0x20 + qualifier['Speed'],
            'Near': 0x30 + qualifier['Speed'],
            'Stop': 0x00
        }

        if value in ValueStateValues and 0 <= qualifier['Speed'] <= 7:
            FocusCmdString = self._DeviceID + b'\x01\x04\x08' + bytes([ValueStateValues[value]]) + b'\xFF'
            if 'Serial' not in self.ConnectionType:
                FocusCmdString = self.header_for_set(FocusCmdString)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetHome(self, value, qualifier):

        HomeCmdString = self._DeviceID + b'\x01\x06\x04\xFF'
        if 'Serial' not in self.ConnectionType:
            HomeCmdString = self.header_for_set(HomeCmdString)
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu On'   : b'\x01\x10\x01\xFF',
            'Menu Off'  : b'\x01\x10\x03\xFF',
            'Enter'     : b'\x01\x10\x02\xFF',
            'Back'      : b'\x01\x10\x07\xFF',
            'Up'        : b'\x01\x06\x01\x00\x00\x03\x01\xFF',
            'Down'      : b'\x01\x06\x01\x00\x00\x03\x02\xFF',
            'Left'      : b'\x01\x06\x01\x00\x00\x01\x03\xFF',
            'Right'     : b'\x01\x06\x01\x00\x00\x02\x03\xFF',
            'Stop'      : b'\x01\x06\x01\x00\x00\x03\x03\xFF'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = self._DeviceID + ValueStateValues[value]
            if 'Serial' not in self.ConnectionType:
                MenuNavigationCmdString = self.header_for_set(MenuNavigationCmdString)
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x03\x01\xFF',
            'Down'  : b'\x03\x02\xFF',
            'Left'  : b'\x01\x03\xFF',
            'Right' : b'\x02\x03\xFF',
            'Stop'  : b'\x03\x03\xFF'
        }

        if value in ValueStateValues and 1 <= qualifier['Pan Speed'] <= 24 and 1 <= qualifier['Tilt Speed'] <= 20:
            PanTiltCmdString = self._DeviceID + b'\x01\x06\x01' + bytes([qualifier['Pan Speed'], qualifier['Tilt Speed']]) + ValueStateValues[value]
            if 'Serial' not in self.ConnectionType:
                PanTiltCmdString = self.header_for_set(PanTiltCmdString)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02',
            'Off' : b'\x03'
        }

        if value in ValueStateValues:
            PowerCmdString = self._DeviceID + b'\x01\x04\x00' + ValueStateValues[value] + b'\xFF'
            if 'Serial' not in self.ConnectionType:
                PowerCmdString = self.header_for_set(PowerCmdString)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On',
            0x03 : 'Off'
        }

        PowerCmdString = self._DeviceID + b'\x09\x04\x00\xFF'
        if 'Serial' not in self.ConnectionType:
            PowerCmdString = self.header_for_get(PowerCmdString)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save'   : b'\x01',
            'Recall' : b'\x02'
        }

        if 2 <= int(value) <= 255 and qualifier['Action'] in ActionStates:
            PresetCmdString = self._DeviceID + b'\x01\x04\x3F' + ActionStates[qualifier['Action']] + bytes([int(value)]) + b'\xFF'
            if 'Serial' not in self.ConnectionType:
                PresetCmdString = self.header_for_set(PresetCmdString)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 0x20 + qualifier['Speed'],
            'Wide': 0x30 + qualifier['Speed'],
            'Stop': 0x00
        }

        if value in ValueStateValues and 0 <= qualifier['Speed'] <= 7:
            ZoomCmdString = self._DeviceID + b'\x01\x04\x07' + bytes([ValueStateValues[value]]) + b'\xFF'
            if 'Serial' not in self.ConnectionType:
                ZoomCmdString = self.header_for_set(ZoomCmdString)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x02 : 'Syntax Error.',
            0x03 : 'Command Buffer Full.',
            0x04 : 'Command Canceled.',
            0x05 : 'No Socket.',
            0x41 : 'Command Not Executable.'
        }

        if response:
            if 'Serial' not in self.ConnectionType:
                response = response[8:12]
            if len(response) > 3 and response[1] != 0x50:
                self.Error(['Error: {}'.format(DEVICE_ERROR_CODES[response[2]])])
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
                    if 'Serial' not in self.ConnectionType:
                        self.StartSequence = 0
                    return ''
                else:
                    if 'Serial' not in self.ConnectionType:
                        self.StartSequence = 1
                    return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        if 'Serial' not in self.ConnectionType:
            self.ResetSequence( None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.StartSequence = 0

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])