from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self._DeviceID = 0x81
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Backlight': {'Status': {}},
            'Focus': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'RecallPreset': {'Status': {}},
            'StorePreset': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)
        else:
            print('Invalid DeviceID Parameter. Range is from 1 to 7')

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'On': 0x00,
            'Off': 0x03,
            'Shutter Priority': 0x0A,
            'Iris Priority': 0x0B,
            'Bright Mode': 0x0D
        }

        AutoExposureCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            b'\x50\x00': 'On',
            b'\x50\x03': 'Off',
            b'\x50\x0A': 'Shutter Priority',
            b'\x50\x0B': 'Iris Priority',
            b'\x50\x0D': 'Bright Mode',
        }

        AutoExposureCmdString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:3]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/Unexpected Response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        AutoFocusCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x50\x02': 'On',
            b'\x50\x03': 'Off'
        }

        AutoFocusCmdString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:3]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/Unexpected Response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        BacklightCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            b'\x50\x02': 'On',
            b'\x50\x03': 'Off'
        }

        BacklightCmdString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:3]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/Unexpected Response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 0x02,
            'Near': 0x03,
            'Stop': 0x00
        }

        FocusCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x08, ValueStateValues[value], 0xFF)
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        IrisCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        SpeedStates = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08,
            '9': 0x09,
            '10': 0x0A,
            '11': 0x0B,
            '12': 0x0C,
            '13': 0x0D,
            '14': 0x0E,
            '15': 0x0F,
            '16': 0x10,
            '17': 0x11,
            '18': 0x12,
            '19': 0x13,
            '20': 0x14,
            '21': 0x15,
            '22': 0x16,
            '23': 0x17,
            '24': 0x18
        }

        ValueStateValues = {
            'Up': [0x03, 0x01],
            'Down': [0x03, 0x02],
            'Left': [0x01, 0x03],
            'Right': [0x02, 0x03],
            'Up Left': [0x01, 0x01],
            'Up Right': [0x02, 0x01],
            'Down Left': [0x01, 0x02],
            'Down Right': [0x02, 0x02],
            'Stop': [0x03, 0x03],
            'Home': 0x04,
            'Reset': 0x05
        }

        if value in ['Home', 'Reset']:
            PanTiltCmdString = pack('>BBBBB', self._DeviceID, 0x01, 0x06, ValueStateValues[value], 0xFF)
        else:
            PanTiltCmdString = pack('>BBBBBBBBB', self._DeviceID, 0x01, 0x06, 0x01, SpeedStates[qualifier['Pan Speed']], SpeedStates[qualifier['Tilt Speed']], ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
        self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        PowerCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x50\x02': 'On',
            b'\x50\x03': 'Off'
        }

        PowerCmdString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetRecallPreset(self, value, qualifier):

        ValueStateValues = {
            '0': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05
        }

        RecallPresetCmdString = pack('>BBBBBBB', self._DeviceID, 0x01, 0x04, 0x3F, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)

    def SetStorePreset(self, value, qualifier):

        ValueStateValues = {
            '0': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05
        }

        StorePresetCmdString = pack('>BBBBBBB', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, ValueStateValues[value], 0xFF)
        self.__SetHelper('StorePreset', StorePresetCmdString, value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto': 0x00,
            'Indoor': 0x01,
            'Outdoor': 0x02,
            'One Push': 0x03,
            'Manual': 0x05
        }

        WhiteBalanceCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x35, ValueStateValues[value], 0xFF)
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            b'\x50\x00': 'Auto',
            b'\x50\x04': 'Auto',
            b'\x50\x06': 'Auto',
            b'\x50\x07': 'Auto',
            b'\x50\x01': 'Indoor',
            b'\x50\x02': 'Outdoor',
            b'\x50\x03': 'One Push',
            b'\x50\x05': 'Manual',
            b'\x50\x08': 'Fluorescent'
        }

        WhiteBalanceCmdString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x35, 0xFF)
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:3]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/Unexpected Response'])

    def SetZoom(self, value, qualifier):

        SpeedStatesTele = {
            '0': 0x20,
            '1': 0x21,
            '2': 0x22,
            '3': 0x23,
            '4': 0x24,
            '5': 0x25,
            '6': 0x26,
            '7': 0x27
        }

        SpeedStatesWide = {
            '0': 0x30,
            '1': 0x31,
            '2': 0x32,
            '3': 0x33,
            '4': 0x34,
            '5': 0x35,
            '6': 0x36,
            '7': 0x37
        }

        ValueStateValues = {
            'Wide': 'wide',
            'Tele': 'tele',
            'Stop': 'stop'
        }

        if ValueStateValues[value] == 'stop':
            ZoomCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x07, 0x00, 0xFF)
        elif ValueStateValues[value] == 'tele':
            ZoomCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x07, SpeedStatesTele[qualifier['Speed']], 0xFF)
        elif ValueStateValues[value] == 'wide':
            ZoomCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x07, SpeedStatesWide[qualifier['Speed']], 0xFF)
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x61\x41': "Command Not Executable.",
            b'\x61\x06': "Address ID Error",
            b'\x61\x05': "Address ID Error",
            b'\x61\x04': "Address ID Error",
            b'\x61\x03': "Address ID Error",
            b'\x61\x02': "Address ID Error",
            b'\x61\x01': "Address ID Error"
        }

        if 'Serial' not in self.ConnectionType:
            response = response[2:]
        if response[1:3] in DEVICE_ERROR_CODES:
            DeviceError = DEVICE_ERROR_CODES[response].decode()
            self.Error(['{0} {1}'.format(sourceCmdName, DeviceError)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        if 'Serial' not in self.ConnectionType:
            len_val = len(commandstring) + 2
            commandstring = b''.join([b'\x00', bytes([len_val]), commandstring])
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/Unexpected Response'.format(commandstring)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if 'Serial' not in self.ConnectionType:
            len_val = len(commandstring) + 2
            commandstring = b''.join([b'\x00', bytes([len_val]), commandstring])

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

        self.Send(b'\x88\x30\x01\xFF')
        self.Send(b'\x88\x01\x00\x01\xFF')

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')

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
        Command = self.Commands[command]
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
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model =None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

