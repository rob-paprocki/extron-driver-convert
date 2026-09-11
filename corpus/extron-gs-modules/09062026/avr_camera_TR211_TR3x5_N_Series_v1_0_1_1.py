# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface, EthernetServerInterfaceEx
from extronlib.system import Wait, ProgramLog
from extronlib import event
from struct import pack, unpack

class DeviceClass:

    Objects = {}

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
            'AutoTracking': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'FocusMode': { 'Status': {}},
            'Gain': { 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}}
        }

        if self.ConnectionType == 'Ethernet':
            DeviceClass.Objects[self.Hostname] = self

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if self.ConnectionType == 'Serial':
            if 1 <= int(value) <= 7:
                self._DeviceID = 0x80 + int(value)
            else:
                self.Error(['Invalid Device ID Parameter.'])
        else:
            self._DeviceID == 0x81

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

    def DefinePayloadLength(self, cmdString):

        payloadLengthByte = len(cmdString).to_bytes(1, "big")
        return b''.join([b'\x00', payloadLengthByte])

    def DefineSquenceNumber(self):

        try:
            sequenceNumberByte = self.SequenceNumber.to_bytes(4, byteorder="big")
        except:
            self.SequenceNumber = 0
            sequenceNumberByte = self.SequenceNumber.to_bytes(4, byteorder="big")
        self.SequenceNumber += 1
        return sequenceNumberByte

    def SetHeader(self, cmdString, SetOrGet):

        if self.ConnectionType == 'Serial':
            return cmdString
        else:
            if SetOrGet == 'Set':
                payloadTypeByte = b'\x01\x00'
            elif SetOrGet == 'Get':
                payloadTypeByte = b'\x01\x10'
            else:
                self.Discard('Invalid Command for SetHeader')

        payloadLength = self.DefinePayloadLength(cmdString)
        sequenceNumberByte = self.DefineSquenceNumber()
        return b''.join([payloadTypeByte, payloadLength, sequenceNumberByte, cmdString])
    
    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto':        0x00,
            'Manual':           0x03,
            'Shutter Priority': 0x0A, 
            'Iris Priority':    0x0B,
            'Bright':           0x0D
        }
        
        if value in ValueStateValues:
            AutoExposureCmdString = self.SetHeader(pack('>6B', self._DeviceID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority',
            0x0D: 'Bright'
        }

        AutoExposureCmdString = self.SetHeader(pack('>5B', self._DeviceID, 0x09, 0x04, 0x39, 0xFF), 'Get')
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoTracking(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }
        
        if value in ValueStateValues:
            AutoTrackingCmdString = self.SetHeader(pack('>6B', self._DeviceID, 0x01, 0x04, 0x7D, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('AutoTracking', AutoTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTracking')
    
    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }
        
        if value in ValueStateValues:
            BacklightCmdString = self.SetHeader(pack('>6B', self._DeviceID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')
    
    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto':     0x02,
            'Manual':   0x03
        }
        
        if value in ValueStateValues:
            FocusModeCmdString = self.SetHeader(pack('>6B', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Auto', 
            0x03: 'Manual'
        }

        FocusModeCmdString = self.SetHeader(pack('>5B', self._DeviceID, 0x09, 0x04, 0x38, 0xFF), 'Get')
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }
        
        if value in ValueStateValues:
            GainCmdString = self.SetHeader(pack('>6B', self._DeviceID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }
        
        if value in ValueStateValues:
            IrisCmdString = self.SetHeader(pack('>6B', self._DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

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
            'Stop':         0x0303,
            'Home':         0x04,
            'Reset':        0x05
        }

        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']
        if value == 'Home' or value == 'Reset':
            PanTiltCmdString = self.SetHeader(pack('5B', self._DeviceID, 0x01, 0x06, ValueStateValues[value], 0xFF), 'Set')
        elif 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 24 and value in ValueStateValues:
            PanTiltCmdString = self.SetHeader(pack('>6BHB', self._DeviceID, 0x01, 0x06, 0x01, pan_speed, 
                                            tilt_speed, ValueStateValues[value], 0xFF), 'Set')
        else:
            self.Discard('Invalid Command for SetPanTilt')
            return
        self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  0x02,
            'Off': 0x03
        }
        
        if value in ValueStateValues:
            PowerCmdString = self.SetHeader(pack('>6B', self._DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        PowerCmdString = self.SetHeader(pack('>5B', self._DeviceID, 0x09, 0x04, 0x00, 0xFF), 'Get')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PresetRecallCmdString = self.SetHeader(pack('7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x02, value, 0xFF), 'Set')
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
            
    def SetPresetSave(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and value not in [0x5F, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6]:
            PresetSaveCmdString = self.SetHeader(pack('7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, value, 0xFF), 'Set')
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')    

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x02,
            'Down': 0x03
        }
        
        if value in ValueStateValues:
            ShutterCmdString = self.SetHeader(pack('>6B', self._DeviceID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }
       
        zoom_speed = qualifier['Speed']
        if 0 <= zoom_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                zoom_speed = 0x00
            else:
                zoom_speed += ValueStateValues[value]

            ZoomCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x07, zoom_speed, 0xFF), 'Set')
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if self.ConnectionType != 'Serial':
            if len(response) > 8:
                response = response[8:]

        if response and len(response) >= 4:
            address, errorbyte, errorcode, terminator = unpack('>4B', response[:4])
            if errorbyte & 0x60 == 0x60:
                self.Error(['An error occurred.'])
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

        if 'Serial' not in self.ConnectionType:
            self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')
        else:
            pass

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