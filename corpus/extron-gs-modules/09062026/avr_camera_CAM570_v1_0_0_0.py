from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re
import time
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
        self._DeviceID = 0x81
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Focus': { 'Status': {}},
            'FocusMode': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'PIPHDMI': { 'Status': {}},
            'PIPUSB': { 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Action'], 'Status': {}},
            'TrackingMode': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }

        self.start_sequence = False
        self.previous_sequence = 0
        self.last_sequence_reset = 0

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if self.ConnectionType == 'Serial':
            if 1 <= int(value) <= 7:
                self._DeviceID = 0x80 + int(value)
            else:
                print('Invalid Device ID Parameter.')
        else:
            self._DeviceID = 0x81

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
        
    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Stop'  : 0x20,
            'Far'   : 0x30,
            'Near'  : 0x00
        }

        if value in ValueStateValues:
            FocusCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x08, ValueStateValues[value], 0xFF))
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Manual' : 0x03,
            'Auto'   : 0x02
        }

        if value in ValueStateValues:
            FocusModeCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF))
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'        : 0x0301,
            'Down'      : 0x0302,
            'Left'      : 0x0103,
            'Right'     : 0x0203,
            'Up Left'   : 0x0101,
            'Up Right'  : 0x0201,
            'Down Left' : 0x0102,
            'Down Right': 0x0202,
            'Stop'      : 0x0303
        }

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])

        if 0 <= pan_speed <= 15 and 0 <= tilt_speed <= 15 and value in ValueStateValues:
            if value == 'Stop':
                PanTiltCmdString = self.set_header(pack('>6BHB', self._DeviceID, 0x01, 0x06, 0x01, 0x00, 0x00, ValueStateValues[value], 0xFF))
            else:
                PanTiltCmdString = self.set_header(pack('>6BHB', self._DeviceID, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF))
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPIPHDMI(self, value, qualifier):

        ValueStateValues = {
            'PTZ Lens'              : 0x00,
            'AI Lens'               : 0x01,
            'PTZ + Right Down AI'   : 0x02,
            'PTZ + Left Up AI'      : 0x03,
            'Left PTZ + Right AI'   : 0x04,
            'AI + Right Down PTZ'   : 0x12,
            'AI + Left Up PTZ'      : 0x13,
            'Left AI + Right PTZ'   : 0x14
        }

        if value in ValueStateValues:
            PIPHDMICmdString = self.set_header(pack('7B', self._DeviceID, 0x01, 0x04, 0x7F, 0x01, ValueStateValues[value], 0xFF))
            self.__SetHelper('PIPHDMI', PIPHDMICmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPHDMI')

    def SetPIPUSB(self, value, qualifier):

        ValueStateValues = {
            'PTZ Lens'              : 0x00,
            'AI Lens'               : 0x01,
            'PTZ + Right Down AI'   : 0x02,
            'PTZ + Left Up AI'      : 0x03,
            'Left PTZ + Right AI'   : 0x04,
            'AI + Right Down PTZ'   : 0x12,
            'AI + Left Up PTZ'      : 0x13,
            'Left AI + Right PTZ'   : 0x14
        }

        if value in ValueStateValues:
            PIPUSBCmdString = self.set_header(pack('7B', self._DeviceID, 0x01, 0x04, 0x7F, 0x00, ValueStateValues[value], 0xFF))
            self.__SetHelper('PIPUSB', PIPUSBCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPUSB')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : 0x02,
            'Off'   : 0x03,
            'Reboot': 0x00
        }

        if value in ValueStateValues:
            PowerCmdString = self.set_header(pack('6B', self._DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF))
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save'  : 0x01,
            'Recall': 0x02
        }

        if qualifier['Action'] in ActionStates and 0 <= int(value) <= 127:
            PresetCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, ActionStates[qualifier['Action']], int(value), 0xFF))
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'Trigger'           : 0x00,
            'Off'               : 0x01,
            'Auto Frame'        : 0x02,
            'Manual Frame'      : 0x03,
            'Audio Tracking'    : 0x04,
            'Audio Frame'       : 0x05,
            'Audio Preset'      : 0x06,
            'Presentation Mode' : 0x07,
            'Preset Frame'      : 0x08
        }

        if value in ValueStateValues:
            TrackingModeCmdString = self.set_header(pack('>7B', self._DeviceID, 0x01, 0x04, 0x7D, ValueStateValues[value], 0x00, 0xFF))
            self.__SetHelper('TrackingMode', TrackingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingMode')

    def UpdateTrackingMode(self, value, qualifier):

        TrackingModeCmdString = self.get_header(pack('>5B', self._DeviceID, 0x09, 0x04, 0x7D, 0xFF))
        res = self.__UpdateHelper('TrackingMode', TrackingModeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x01 : 'Off',
                    0x02 : 'Auto Frame',
                    0x03 : 'Manual Frame',
                    0x04 : 'Audio Tracking',
                    0x05 : 'Audio Frame',
                    0x06 : 'Audio Preset',
                    0x07 : 'Presentation Mode',
                    0x08 : 'Preset Frame'
                }

                value = ValueStateValues[res[4]]
                self.WriteStatus('TrackingMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Tracking Mode: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Stop' : 0x00,
            'Tele' : 0x20,
            'Wide' : 0x30
        }

        if value in ValueStateValues:
            ZoomCmdString = self.set_header(pack('>6B', self._DeviceID, 0x01, 0x04, 0x07, ValueStateValues[value], 0xFF))
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