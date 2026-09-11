from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
        self._DeviceID = b'\x81'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutoTracking': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'ImageFlip': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'RTMP': {'Parameters':['Stream'], 'Status': {}},
            'StandbyLight': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if self.ConnectionType == 'Serial':
            if 1 <= int(value) <= 7:
                self._DeviceID = pack('B', 0x80 + int(value))
            else:
                self.Error(['Invalid Device ID Parameter.'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'Auto'   : b'\x02',
            'Manual' : b'\x03'
        }

        if value in ValueStateValues:
            AutoFocusCmdString = self._DeviceID + b'\x01\x04\x38' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = self._DeviceID + b'\x09\x04\x38\xFF'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02 : 'Auto',
                    0x03 : 'Manual'
                }

                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetAutoTracking(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02',
            'Off' : b'\x03'
        }

        if value in ValueStateValues:
            AutoTrackingCmdString = self._DeviceID + b'\x0A\x11\x54' + ValueStateValues[value] +  b'\xFF'
            self.__SetHelper('AutoTracking', AutoTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTracking')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far'   : 0x20,
            'Near'  : 0x30,
            'Stop'  : 0x00
        }

        if 0 <= qualifier['Speed'] <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = b'\x00'
            else:
                speed = pack('B', ValueStateValues[value] + qualifier['Speed'])

            FocusCmdString = self._DeviceID + b'\x01\x04\x08' + speed + b'\xFF'
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02',
            'Off' : b'\x03'
        }

        if value in ValueStateValues:
            FreezeCmdString = self._DeviceID + b'\x01\x04\x62' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def SetImageFlip(self, value, qualifier):

        ValueStateValues = {
            'Off'             : b'\x00',
            'Horizontal Flip' : b'\x01',
            'Vertical Flip'   : b'\x02',
            'Flip Both'       : b'\x03'
        }

        if value in ValueStateValues:
            ImageFlipCmdString = self._DeviceID + b'\x01\x04\xA4' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('ImageFlip', ImageFlipCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageFlip')

    def UpdateImageFlip(self, value, qualifier):

        ImageFlipCmdString = self._DeviceID + b'\x09\x04\xA4\xFF'
        res = self.__UpdateHelper('ImageFlip', ImageFlipCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x00 : 'Off',
                    0x01 : 'Horizontal Flip',
                    0x02 : 'Vertical Flip',
                    0x03 : 'Flip Both'
                }

                value = ValueStateValues[res[2]]
                self.WriteStatus('ImageFlip', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Image Flip: Invalid/unexpected response'])

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'            : b'\x03\x01',
            'Down'          : b'\x03\x02',
            'Left'          : b'\x01\x03',
            'Right'         : b'\x02\x03',
            'Up Left'       : b'\x01\x01',
            'Up Right'      : b'\x02\x01',
            'Down Left'     : b'\x01\x02',
            'Down Right'    : b'\x02\x02',
            'Stop'          : b'\x03\x03',
            'Home'          : b'\x04',
            'Reset'         : b'\x05'
        }

        if 1 <= qualifier['Pan Speed'] <= 24 and 1 <= qualifier['Tilt Speed'] <= 20 and value in ValueStateValues:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = self._DeviceID + b'\x01\x06' + ValueStateValues[value] + b'\xFF'
            else:
                PanTiltCmdString = self._DeviceID + b'\x01\x06\x01' + pack('B', qualifier['Pan Speed']) + pack('B', qualifier['Tilt Speed']) + ValueStateValues[value] + b'\xFF' 
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
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self._DeviceID + b'\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02 : 'On',
                    0x03 : 'Off',
                    0x04 : 'Internal Power Circuit Error'
                }

                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 127:
            PresetRecallCmdString = self._DeviceID + b'\x01\x04\x3F\x02' + pack('B', int(value)) + b'\xFF'
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 127:
            PresetSaveCmdString = self._DeviceID + b'\x01\x04\x3F\x01' + pack('B', int(value)) + b'\xFF'
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRTMP(self, value, qualifier):

        StreamStates = {
            '1' : 0x10,
            '2' : 0x20
        }

        ValueStateValues = {
            'On'  : 0x02,
            'Off' : 0x03
        }

        if qualifier['Stream'] in StreamStates and value in ValueStateValues:
            RTMPCmdString = self._DeviceID + b'\x0A\x11\xA8' + pack('B', StreamStates[qualifier['Stream']] + ValueStateValues[value]) + b'\xFF'
            self.__SetHelper('RTMP', RTMPCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRTMP')

    def UpdateRTMP(self, value, qualifier):

        if 1 <= int(qualifier['Stream']) <= 2:
            RTMPCmdString = self._DeviceID + b'\x09\x11\x53\xFF'
            res = self.__UpdateHelper('RTMP', RTMPCmdString, value, qualifier)
            if res:
                try:
                    value = res[2]
                    if value == 0x00: # Both Off
                        self.WriteStatus('RTMP', 'Off', {'Stream' : '1'})
                        self.WriteStatus('RTMP', 'Off', {'Stream' : '2'})
                    elif value == 0x01: # Stream 1 On
                        self.WriteStatus('RTMP', 'On', {'Stream' : '1'})
                        self.WriteStatus('RTMP', 'Off', {'Stream' : '2'})
                    elif value == 0x02: # Stream 2 On
                        self.WriteStatus('RTMP', 'Off', {'Stream' : '1'})
                        self.WriteStatus('RTMP', 'On', {'Stream' : '2'})
                    elif value == 0x03: # Both On
                        self.WriteStatus('RTMP', 'On', {'Stream' : '1'})
                        self.WriteStatus('RTMP', 'On', {'Stream' : '2'})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['RTMP: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRTMP')

    def SetStandbyLight(self, value, qualifier):

        ValueStateValues = {
            'Flashing'        : b'\x01',
            'Light Always On' : b'\x02',
            'Normal'          : b'\x03'
        }

        if value in ValueStateValues:
            StandbyLightCmdString = self._DeviceID + b'\x0A\x02\x02' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('StandbyLight', StandbyLightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandbyLight')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 0x20,
            'Wide' : 0x30,
            'Stop' : 0x00
        }

        if 0 <= qualifier['Speed'] <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = b'\x00'
            else:
                speed = pack('B', ValueStateValues[value] + qualifier['Speed'])

            ZoomCmdString = self._DeviceID + b'\x01\x04\x07' + speed + b'\xFF'
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) == 4:
            error_map = {
                0x01: 'Message Length Error',
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()