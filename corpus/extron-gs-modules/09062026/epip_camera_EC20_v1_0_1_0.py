# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Backlight': { 'Status': {}},
            'ExposureMode': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Action'], 'Status': {}},
            'TallyLight': { 'Status': {}},
            'TallyLightColor': {'Parameters':['Color'], 'Status': {}},
            'TargetTracking': { 'Status': {}},
            'Tracking': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}}
        }

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
            }

        if value in ValueStateValues:
            BacklightCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        BacklightCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02: 'On',
                    0x03: 'Off'
                    }
                value = ValueStateValues[res[2]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetExposureMode(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': 0x00,
            'Manual': 0x03,
            'Shutter Priority': 0x0A,
            'Iris Priority': 0x0B,
            'Bright': 0x0D
            }

        if value in ValueStateValues:
            ExposureModeCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
            self.__SetHelper('ExposureMode', ExposureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExposureMode')

    def UpdateExposureMode(self, value, qualifier):

        ExposureModeCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('ExposureMode', ExposureModeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x00: 'Full Auto',
                    0x03: 'Manual',
                    0x0A: 'Shutter Priority',
                    0x0B: 'Iris Priority',
                    0x0D: 'Bright'
                    }
                value = ValueStateValues[res[2]]
                self.WriteStatus('ExposureMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Exposure Mode: Invalid/unexpected response'])

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

        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 20 and value in ValueStateValues:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = pack('>5B', 0x81, 0x01, 0x06, ValueStateValues[value], 0xFF)
            else:
                PanTiltCmdString = pack('>6BHB', 0x81, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF)

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            PowerCmdString = pack('>6B', 0x81, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = pack('>5B', 0x81, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02: 'On',
                    0x03: 'Off',
                    }

                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save':     0x01,
            'Recall':   0x02,
            'Reset':    0x00
        }
        action = qualifier['Action']

        if action in ActionStates and 0 <= int(value) <= 254:
            PresetCmdString = pack('>7B', 0x81, 0x01, 0x04, 0x3F, ActionStates[action], int(value), 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetTallyLight(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
            }

        if value in ValueStateValues:
            TallyLightCmdString = pack('>6B', 0x81, 0x0A, 0x11, 0x47, ValueStateValues[value], 0xFF)
            self.__SetHelper('TallyLight', TallyLightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTallyLight')

    def SetTallyLightColor(self, value, qualifier):

        ColorStates = {
            'Green': 0x00,
            'Red': 0x01
            }

        ValueStateValues = {
            'Blinking': 0x01,
            'Solid': 0x02,
            'Off': 0x03
            }

        if qualifier['Color'] in ColorStates and value in ValueStateValues:
            TallyLightColorCmdString = pack('>8B', 0x81, 0x0A, 0x02, 0x02, 0x47, ValueStateValues[value], ColorStates[qualifier['Color']], 0xFF)
            self.__SetHelper('TallyLightColor', TallyLightColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTallyLightColor')

    def SetTargetTracking(self, value, qualifier):

        ValueStateValues = {
            'Left': 0x02,
            'Right': 0x03,
            'Select': 0x04
            }

        if value in ValueStateValues:
            TargetTrackingCmdString = pack('>6B', 0x81, 0x0A, 0x11, 0xA3, ValueStateValues[value], 0xFF)
            self.__SetHelper('TargetTracking', TargetTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTargetTracking')

    def SetTracking(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
            }

        if value in ValueStateValues:
            TrackingCmdString = pack('>6B', 0x81, 0x0A, 0x11, 0x54, ValueStateValues[value], 0xFF)
            self.__SetHelper('Tracking', TrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTracking')

    def UpdateTracking(self, value, qualifier):

        TrackingCmdString = pack('>6B', 0x81, 0x09, 0x7E, 0x11, 0x54, 0xFF)
        res = self.__UpdateHelper('Tracking', TrackingCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02: 'On',
                    0x03: 'Off'
                    }

                value = ValueStateValues[res[2]]
                self.WriteStatus('Tracking', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Tracking: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 0x20,
            'Wide' : 0x30,
            'Stop' : b'\x81\x01\x04\x07\x00\xFF'
        }

        if 0 <= qualifier['Speed'] <= 7 and value in ValueStateValues:
            if value == 'Stop':
                ZoomCmdString = ValueStateValues[value]
            else:
                ZoomCmdString = b'\x81\x01\x04\x07' + pack('>B', ValueStateValues[value] + qualifier['Speed']) + b'\xFF'
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

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