from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


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
        self.DeviceID = '1'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'BacklightMode': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Gain': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Shutter': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = pack('B', 0x80 + int(value))

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Automatic Exposure Mode': b'\x00',
            'Manual Control Mode': b'\x03',
            'Shutter Priority Mode': b'\x0A',
            'Iris Priority Mode': b'\x0B',
            'Bright Mode': b'\x0D'
        }

        if value in ValueStateValues:
            AutoExposureCmdString = b''.join([self._DeviceID, b'\x01\x04\x39', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Automatic Exposure Mode',
            b'\x03': 'Manual Control Mode',
            b'\x0A': 'Shutter Priority Mode',
            b'\x0B': 'Iris Priority Mode',
            b'\x0D': 'Bright Mode'
        }

        AutoExposureCmdString = b''.join([self._DeviceID, b'\x09\x04\x39\xFF'])
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x02',
            'Manual': b'\x03'
        }

        if value in ValueStateValues:
            AutoFocusCmdString = b''.join([self._DeviceID, b'\x01\x04\x38', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'Auto',
            b'\x03': 'Manual'
        }

        AutoFocusCmdString = b''.join([self._DeviceID, b'\x09\x04\x38\xFF'])
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02',
            'Off': b'\x03'
        }

        if value in ValueStateValues:
            BacklightModeCmdString = b''.join([self._DeviceID, b'\x01\x04\x33', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklightMode')

    def UpdateBacklightMode(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        BacklightModeCmdString = b''.join([self._DeviceID, b'\x09\x04\x33\xFF'])
        res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('BacklightMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight Mode: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': 0x20,
            'Far': 0x30,
            'Stop': 0x00
        }

        if value in ValueStateValues and 0 <= qualifier['Focus Speed'] <= 7:
            focusString = 0x00 if value == 'Stop' else qualifier['Focus Speed'] + ValueStateValues[value]
            FocusCmdString = b''.join([self._DeviceID, b'\x01\x04\x08', pack('B', focusString), b'\xFF'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x02',
            'Down': b'\x03',
            'Reset': b'\x00'
        }

        if value in ValueStateValues:
            GainCmdString = b''.join([self._DeviceID, b'\x01\x04\x0C', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x02',
            'Down': b'\x03',
            'Reset': b'\x00'
        }

        if value in ValueStateValues:
            IrisCmdString = b''.join([self._DeviceID, b'\x01\x04\x0B', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x03\x01',
            'Down': b'\x03\x02',
            'Left': b'\x01\x03',
            'Right': b'\x02\x03',
            'Up Left': b'\x01\x01',
            'Up Right': b'\x02\x01',
            'Down Left': b'\x01\x02',
            'Down Right': b'\x02\x02',
            'Stop': b'\x03\x03'
        }

        if value in ValueStateValues and 1 <= qualifier['Pan Speed'] <= 63 and 1 <= qualifier['Tilt Speed'] <= 63:
            PanTiltCmdString = b''.join([self._DeviceID, b'\x01\x06\x01', pack('BB', qualifier['Pan Speed'],
                                          qualifier['Tilt Speed']), ValueStateValues[value], b'\xFF'])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02',
            'Off': b'\x03'
        }

        if value in ValueStateValues:
            PowerCmdString = b''.join([self._DeviceID, b'\x01\x04\x00', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        PowerCmdString = b''.join([self._DeviceID, b'\x09\x04\x00\xFF'])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 64:
            PresetRecallCmdString = b''.join([self._DeviceID, b'\x01\x04\x3F\x02', pack('B', int(value) - 1), b'\xFF'])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 64:
            PresetSaveCmdString = b''.join([self._DeviceID, b'\x01\x04\x3F\x01', pack('B', int(value) - 1), b'\xFF'])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x02',
            'Down': b'\x03',
            'Reset': b'\x00'
        }

        if value in ValueStateValues:
            ShutterCmdString = b''.join([self._DeviceID, b'\x01\x04\x0A', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }

        if value in ValueStateValues and 0 <= qualifier['Zoom Speed'] <= 7:
            zoomString = 0x00 if value == 'Stop' else qualifier['Zoom Speed'] + ValueStateValues[value]
            ZoomCmdString = b''.join([self._DeviceID, b'\x01\x04\x07', pack('B', zoomString), b'\xFF'])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) > 3:
            ErrorCodes = {
                b'\x60\x01': 'Message Length Error',
                b'\x61\x01': 'Message Length Error',
                b'\x60\x02': 'Syntax Error',
                b'\x61\x02': 'Syntax Error',
                b'\x60\x03': 'Command Buffer Full',
                b'\x61\x03': 'Command Buffer Full',
                b'\x60\x04': 'Command Cancelled',
                b'\x61\x04': 'Command Cancelled',
                b'\x60\x05': 'No Socket',
                b'\x61\x05': 'No Socket',
                b'\x60\x41': 'Command Not Executable',
                b'\x61\x41': 'Command Not Executable'
            }
            if response[-3:-1] in ErrorCodes:
                self.Error([ErrorCodes[response[-3:-1]]])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
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

