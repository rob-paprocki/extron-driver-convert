from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re

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
        self._CameraID = 0x81
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AddressSet': {'Status': {}},
            'Aperture': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'FocusMode': {'Status': {}},
            'HorizontalImageFlip': {'Status': {}},
            'Iris': {'Status': {}},
            'IRReceive': {'Status': {}},
            'PanandTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Preset Number'], 'Status': {}},
            'Shutter': {'Status': {}},
            'VerticalImageFlip': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.matchError = re.compile(b'[\x90\xA0\xB0\xC0][\x60\x61]([\x02\x41])\xFF')

    @property
    def CameraID(self):
        return self._CameraID

    @CameraID.setter
    def CameraID(self, value):
        if 1 <= int(value) <= 4:
            self._CameraID = 0x80 + int(value)
        else:
            print('Invalid CameraID entered. Range is from 1 - 4.')

    def SetAddressSet(self, value, qualifier):

        AddressSetCmdString = pack('>2sBs', b'\x88\x30', int(self._CameraID), b'\xFF')
        self.__SetHelper('AddressSet', AddressSetCmdString, value, qualifier)

    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x01\x04\x02\x00\xFF',
            'Up': b'\x01\x04\x02\x02\xFF',
            'Down': b'\x01\x04\x02\x03\xFF'
        }

        ApertureCmdString = pack('>B5s', self._CameraID, ValueStateValues[value])
        self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': b'\x01\x04\x39\x00\xFF',
            'Manual': b'\x01\x04\x39\x03\xFF',
            'Shutter Priority': b'\x01\x04\x39\x0A\xFF',
            'Iris Priority': b'\x01\x04\x39\x0B\xFF',
            'Bright': b'\x01\x04\x39\x0D\xFF'
        }

        AutoExposureCmdString = pack('>B5s', self._CameraID, ValueStateValues[value])
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority',
            0x0D: 'Bright'
        }

        AutoExposureCmdString = pack('>B4s', self._CameraID, b'\x09\x04\x39\xFF')
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure has invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        FocusSpeed = int(qualifier['Focus Speed'])
        if 0 <= FocusSpeed <= 15:
            if value == 'Far':
                FocusCmdString = pack('>B3sBB', self._CameraID, b'\x01\x04\x08', FocusSpeed + 0x20, 0xFF)
            elif value == 'Near':
                FocusCmdString = pack('>B3sBB', self._CameraID, b'\x01\x04\x08', FocusSpeed + 0x30, 0xFF)
            elif value == 'Stop':
                FocusCmdString = pack('>B5s', self._CameraID, b'\x01\x04\x08\x00\xFF')
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x01\x04\x38\x02\xFF',
            'Manual': b'\x01\x04\x38\x03\xFF'
        }

        FocusModeCmdString = pack('>B5s', self._CameraID, ValueStateValues[value])
        self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Auto',
            0x03: 'Manual'
        }

        FocusModeCmdString = pack('>B4s', self._CameraID, b'\x09\x04\x38\xFF')
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Focus Mode has invalid/unexpected response'])

    def SetHorizontalImageFlip(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x61\x02\xFF',
            'Off': b'\x01\x04\x61\x03\xFF'
        }

        HorizontalImageFlipCmdString = pack('>B5s', self._CameraID, ValueStateValues[value])
        self.__SetHelper('HorizontalImageFlip', HorizontalImageFlipCmdString, value, qualifier)

    def UpdateHorizontalImageFlip(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        HorizontalImageFlipCmdString = pack('>B4s', self._CameraID, b'\x09\x04\x61\xFF')
        res = self.__UpdateHelper('HorizontalImageFlip', HorizontalImageFlipCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('HorizontalImageFlip', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Horizontal Image Flip has invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x01\x04\x0B\x00\xFF',
            'Up': b'\x01\x04\x0B\x02\xFF',
            'Down': b'\x01\x04\x0B\x03\xFF'
        }

        IrisCmdString = pack('>B5s', self._CameraID, ValueStateValues[value])
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetIRReceive(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x06\x08\x02\xFF',
            'Off': b'\x01\x06\x08\x03\xFF'
        }

        IRReceiveCmdString = pack('>B5s', self._CameraID, ValueStateValues[value])
        self.__SetHelper('IRReceive', IRReceiveCmdString, value, qualifier)

    def UpdateIRReceive(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        IRReceiveCmdString = pack('>B4s', self._CameraID, b'\x09\x06\x08\xFF')
        res = self.__UpdateHelper('IRReceive', IRReceiveCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('IRReceive', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Receive has invalid/unexpected response'])

    def SetPanandTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x03\x01\xFF',
            'Down': b'\x03\x02\xFF',
            'Left': b'\x01\x03\xFF',
            'Right': b'\x02\x03\xFF',
            'UpLeft': b'\x01\x01\xFF',
            'UpRight': b'\x02\x01\xFF',
            'DownLeft': b'\x01\x02\xFF',
            'DownRight': b'\x02\x02\xFF',
            'Stop': b'\x03\x03\xFF',
            'Home': b'\x01\x06\x04\xFF',
            'Reset': b'\x01\x06\x05\xFF'
        }

        PanSpeed = int(qualifier['Pan Speed'])
        TiltSpeed = int(qualifier['Tilt Speed'])

        if value == 'Home' or value == 'Reset':
            PanandTiltCmdString = pack('>B4s', self._CameraID, ValueStateValues[value])
        elif value == 'Stop':
            PanandTiltCmdString = pack('>B5s3s', self._CameraID, b'\x01\x06\x01\x00\x00', ValueStateValues[value])
        else:
            if 1 <= PanSpeed <= 24 and 1 <= TiltSpeed <= 20:
                PanandTiltCmdString = pack('>B3sBB3s', self._CameraID, b'\x01\x06\x01', PanSpeed, TiltSpeed, ValueStateValues[value])

        self.__SetHelper('PanandTilt', PanandTiltCmdString, value, qualifier)


    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x00\x02\xFF',
            'Off': b'\x01\x04\x00\x03\xFF'
        }

        PowerCmdString = pack('>B5s', self._CameraID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        PowerCmdString = pack('>B4s', self._CameraID, b'\x09\x04\x00\xFF')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power has invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x01\x04\x3F\x00',
            'Set': b'\x01\x04\x3F\x01',
            'Recall': b'\x01\x04\x3F\x02'
        }

        PresetNumber = int(qualifier['Preset Number'])
        if 0 <= PresetNumber <= 254:
            PresetCmdString = pack('>B4sBB', self._CameraID, ValueStateValues[value], PresetNumber, 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x01\x04\x0A\x00\xFF',
            'Up': b'\x01\x04\x0A\x02\xFF',
            'Down': b'\x01\x04\x0A\x03\xFF'
        }

        ShutterCmdString = pack('>B5s', self._CameraID, ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def SetVerticalImageFlip(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x66\x02\xFF',
            'Off': b'\x01\x04\x66\x03\xFF'
        }

        VerticalImageFlipCmdString = pack('>B5s', self._CameraID, ValueStateValues[value])
        self.__SetHelper('VerticalImageFlip', VerticalImageFlipCmdString, value, qualifier)

    def UpdateVerticalImageFlip(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        VerticalImageFlipCmdString = pack('>B4s', self._CameraID, b'\x09\x04\x66\xFF')
        res = self.__UpdateHelper('VerticalImageFlip', VerticalImageFlipCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('VerticalImageFlip', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Vertical Image Flip has invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ZoomSpeed = int(qualifier['Zoom Speed'])

        if 0 <= ZoomSpeed <= 15:
            if value == 'Tele':
                ZoomCmdString = pack('>B3sBB', self._CameraID, b'\x01\x04\x07', ZoomSpeed + 0x20, 0xFF)
            elif value == 'Wide':
                ZoomCmdString = pack('>B3sBB', self._CameraID, b'\x01\x04\x07', ZoomSpeed + 0x30, 0xFF)
            elif value == 'Stop':
                ZoomCmdString = pack('>B5s', self._CameraID, b'\x01\x04\x07\x00\xFF')
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x02': 'Illegal command parameters',
            b'\x41': 'Command is not executable'
        }

        matchedInfo = re.search(self.matchError, response)

        if matchedInfo:
            self.Error(['{0} : {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[matchedInfo.group(1)])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{0} has invalid/unexpected response'.format(command)])
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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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

