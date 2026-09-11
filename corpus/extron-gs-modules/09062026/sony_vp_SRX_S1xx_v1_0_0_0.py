from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
            'LampUsage': {'Parameters':['Lamp'], 'Status': {}},
            'LensFocus': { 'Status': {}},
            'LensShift': { 'Status': {}},
            'LensZoom': { 'Status': {}},
            'Power': { 'Status': {}},
            'ScreenMode': { 'Status': {}},
            'ScreenMute': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'TestPattern': {'Parameters':['Color'], 'Status': {}},
            }

        self.header = b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00'
        self.lvpcPacketStart = b'\xA5\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01'
        self.lvpAdjUserStart = b'\x17\x00\x80\x08\x00\x06\x40\x54'
        self.lvpAdjUserStop = b'\x17\x00\x80\x08\x00\x06\x85\x5A'

    def UpdateLampUsage(self, value, qualifier):

        if qualifier['Lamp'] in ['A', 'B']:
            LampUsageCmdString = self.header + b'\x16' + self.lvpcPacketStart + b'\x01\x01\x80\x05\x00\x03\x00\x13\x04\x93\x5A'
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    resParse = unpack('>hh', res[-6:-2])
                    lampAVal = resParse[0]
                    lampBVal = resParse[1]
                    self.WriteStatus('LampUsage', lampAVal, {'Lamp': 'A'})
                    self.WriteStatus('LampUsage', lampBVal, {'Lamp': 'B'})
                except IndexError:
                    self.Error(['Lamp Usage: Invalid/unexpected response'])
        else:
            self.Discard('Device Is Busy for UpdateLampUsage')

    def SetLensFocus(self, value, qualifier):

        ValueStateValues = {
            '+'    : [self.lvpAdjUserStart, b'\x74\x00\x00\x00\xFB\x5A'],
            '-'    : [self.lvpAdjUserStart, b'\x75\x00\x00\x00\xFA\x5A'],
            'Stop' : [self.lvpAdjUserStop, b'\x7F\x00\x00\x00\xF0\x5A']
        }

        LensFocusCmdString = self.header + b'\x19' + self.lvpcPacketStart + ValueStateValues[value][0] + ValueStateValues[value][1]
        self.__SetHelper('LensFocus', LensFocusCmdString, value, qualifier)

    def SetLensShift(self, value, qualifier):

        ValueStateValues = {
            '+'    : [self.lvpAdjUserStart, b'\x72\x00\x00\x00\xFD\x5A'],
            '-'    : [self.lvpAdjUserStart, b'\x73\x00\x00\x00\xFC\x5A'],
            'Stop' : [self.lvpAdjUserStop, b'\x7F\x00\x00\x00\xF0\x5A']
        }

        LensShiftCmdString = self.header + b'\x19' + self.lvpcPacketStart + ValueStateValues[value][0] + ValueStateValues[value][1]
        self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)

    def SetLensZoom(self, value, qualifier):

        ValueStateValues = {
            '+'    : [self.lvpAdjUserStart, b'\x77\x00\x00\x00\xF8\x5A'],
            '-'    : [self.lvpAdjUserStart, b'\x78\x00\x00\x00\xF7\x5A'],
            'Stop' : [self.lvpAdjUserStop, b'\x7F\x00\x00\x00\xF0\x5A']
        }

        LensZoomCmdString = self.header + b'\x19' + self.lvpcPacketStart + ValueStateValues[value][0] + ValueStateValues[value][1]
        self.__SetHelper('LensZoom', LensZoomCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    :   b'\x2E\x00\x00\x00\xA1\x5A',
            'Off'   :   b'\x2F\x00\x00\x00\xA0\x5A'
        }

        PowerCmdString = self.header + b'\x19' + self.lvpcPacketStart + self.lvpAdjUserStart + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Off',
            b'\x01' : 'Warming Up',
            b'\x02' : 'Warming Up',
            b'\x03' : 'On',
            b'\x04' : 'Cooling Down',
            b'\x05' : 'Cooling Down'
        }

        PowerCmdString = self.header + b'\x16' + self.lvpcPacketStart + b'\x01\x01\x80\x05\x00\x03\x00\x02\x01\x87\x5A'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetScreenMode(self, value, qualifier):

        ValueStateValues = {
            'Single' : b'\x00\x00\x80\x07\x00\x05\x00\x05\x02\x00\x00\x87\x5A',
            'Dual'   : b'\x00\x00\x80\x07\x00\x05\x00\x05\x02\x01\x44\xC2\x5A',
            'Quad'   : b'\x00\x00\x80\x07\x00\x05\x00\x05\x02\x03\xE4\x60\x5A'
        }

        ScreenModeCmdString = self.header + b'\x18' + self.lvpcPacketStart + ValueStateValues[value]
        self.__SetHelper('ScreenMode', ScreenModeCmdString, value, qualifier)

    def UpdateScreenMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Single',
            b'\x01' : 'Dual',
            b'\x03' : 'Quad'
        }

        ScreenModeCmdString = self.header + b'\x15' + self.lvpcPacketStart + b'\x00\x01\x80\x04\x00\x02\x00\x05\x80\x5A'
        res = self.__UpdateHelper('ScreenMode', ScreenModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-3]]
                self.WriteStatus('ScreenMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Screen Mode: Invalid/unexpected response'])

    def SetScreenMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x00\x00\x80\x07\x00\x05\x00\x30\x02\x00\x0F\xBD\x5A',
            'Off' : b'\x00\x00\x80\x07\x00\x05\x00\x30\x02\x00\x00\xB2\x5A'
        }

        ScreenMuteCmdString = self.header + b'\x18' + self.lvpcPacketStart + ValueStateValues[value]
        self.__SetHelper('ScreenMute', ScreenMuteCmdString, value, qualifier)

    def SetShutter(self, value, qualifier):

        ShutterCmdString = self.header + b'\x19' + self.lvpcPacketStart + self.lvpAdjUserStart + b'\x24\x00\x00\x00\xAB\x5A'
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'Open',
            b'\x00' : 'Close',
        }

        ShutterCmdString = self.header + b'\x16' + self.lvpcPacketStart + b'\x01\x01\x80\x05\x00\x03\x00\x2F\x01\xAA\x5A'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-2]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def SetTestPattern(self, value, qualifier):

        ColorStates = {
            'Black'  : 0,
            'Blue'   : 1,
            'Green'  : 2,
            'Cyan'   : 3,
            'Red'    : 4,
            'Magenta': 5,
            'Yellow' : 6,
            'White'  : 7
        }

        ValueStateValues = {
            'Off'                 : 0,
            'Crosshatch (Normal)' : 1,
            'Crosshatch (Invert)' : 2,
            '100% Flat'           : 3,
            '80% Flat'            : 4,
            '60% Flat'            : 5,
            '40% Flat'            : 6,
            '20% Flat'            : 7,
            'Checker (Normal)'    : 8,
            'Checker (Invert)'    : 9
        }

        color = ColorStates[qualifier['Color']]
        pattern = ValueStateValues[value]
        val = bytearray.fromhex('{}{}'.format(color, pattern))[0]
        checksum = 0xBF ^ val
        TestPatternCmdString = self.header + b'\x18' + self.lvpcPacketStart + b'\x00\x00\x80\x07\x00\x05\x00\x3D\x02\x00' + val.to_bytes(1,'big') + checksum.to_bytes(1,'big') + b'\x5A'
        self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x01\x01': 'Undefined Command',
            b'\x01\x04': 'Size Error',
            b'\x01\x05': 'Select Error',
            b'\x01\x06': 'Range Over',
            b'\x01\x0A': 'Not Applicable',
            b'\x01\x0C': 'Data Error',
            b'\xF0\x10': 'Check Sum Error',
            b'\xF0\x20': 'Framing Error',
            b'\xF0\x30': 'Parity Error',
            b'\xF0\x40': 'Over Run Error',
            b'\xF0\x50': 'Other Communication Error'
        }

        if response:
            if response[-9:-8] == b'\x03' and response[-4:-2] in DEVICE_ERROR_CODES:
                self.Error([sourceCmdName + ' Error: ' + DEVICE_ERROR_CODES[response[-4:-2]]])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x5A')
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x5A')
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
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

