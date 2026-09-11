from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'AutoExposure': { 'Status': {}},
            'BacklightMode': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'FocusMode': { 'Status': {}},
            'Gain': { 'Status': {}},
            'Home': { 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Action'], 'Status': {}},
            'ResetPanTilt': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\x88'
        elif 1 <= int(value) <= 7:
            self._DeviceID = bytes([0x80+ int(value)])
        else:
            self.Error(['Invalid Device ID Parameter.']) 

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto'         : b'\x00', 
            'Manual'            : b'\x03', 
            'Shutter Priority'  : b'\x0A', 
            'Iris Priority'     : b'\x0B',
            'Bright'            : b'\x0D'
        }

        AutoExposureCmdString = b''.join([self._DeviceID, b'\x01\x04\x39', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00  : 'Full Auto', 
            0x03  : 'Manual', 
            0x0A  : 'Shutter Priority', 
            0x0B  : 'Iris Priority',
            0x0D  : 'Bright'
        }

        AutoExposureCmdString = b''.join([self._DeviceID, b'\x09\x04\x39\xFF'])
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\x02', 
            'Off'   : b'\x03'
        }

        BacklightModeCmdString = b''.join([self._DeviceID, b'\x01\x04\x33', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        BacklightModeCmdString = b''.join([self._DeviceID, b'\x09\x04\x33\xFF'])
        res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('BacklightMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight Mode: Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x02', 
            'Down'  : b'\x03', 
            'Reset' : b'\x00'
        }

        BrightnessCmdString = b''.join([self._DeviceID, b'\x01\x04\x0D', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
    def SetFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 0,
            'Max' : 7
            }

        ValueStateValues = {
            'Far'   : 0x20, 
            'Near'  : 0x30,
        }

        if value == 'Stop':
            focus_speed = 0x00
        else:
            focus_speed = ValueStateValues[value] + qualifier['Speed']

        if SpeedConstraints['Min'] <= qualifier['Speed'] <= SpeedConstraints['Max']:
            FocusCmdString = b''.join([self._DeviceID, b'\x01\x04\x08', bytes([focus_speed]), b'\xFF'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')
    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'      : b'\x02',
            'Manual'    : b'\x03'
        }

        FocusModeCmdString = b''.join([self._DeviceID, b'\x01\x04\x38', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'Auto', 
            0x03 : 'Manual'
        }

        FocusModeCmdString = b''.join([self._DeviceID, b'\x09\x04\x38\xFF'])
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x02', 
            'Down'  : b'\x03', 
            'Reset' : b'\x00'
        }

        GainCmdString = b''.join([self._DeviceID, b'\x01\x04\x0C', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Gain', GainCmdString, value, qualifier)
    def SetHome(self, value, qualifier):

        HomeCmdString = b''.join([self._DeviceID, b'\x01\x06\x04\xFF'])
        self.__SetHelper('Home', HomeCmdString, value, qualifier)
    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x02', 
            'Down'  : b'\x03', 
            'Reset' : b'\x00'
        }

        IrisCmdString = b''.join([self._DeviceID, b'\x01\x04\x0B', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)
    def SetPanTilt(self, value, qualifier):

        PanSpeedConstraints = {
            'Min' : 1,
            'Max' : 24
            }

        TiltSpeedConstraints = {
            'Min' : 1,
            'Max' : 20
            }

        ValueStateValues = {
            'Up'         : b'\x03\x01', 
            'Down'       : b'\x03\x02', 
            'Left'       : b'\x01\x03',  
            'Right'      : b'\x02\x03',  
            'Up Left'    : b'\x01\x01',
            'Up Right'   : b'\x02\x01', 
            'Down Left'  : b'\x01\x02', 
            'Down Right' : b'\x02\x02', 
            'Stop'       : b'\x03\x03'
        }

        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']

        if PanSpeedConstraints['Min'] <= pan_speed <= PanSpeedConstraints['Max'] and TiltSpeedConstraints['Min'] <= tilt_speed <= TiltSpeedConstraints['Max']:
            PanTiltCmdString = b''.join([self._DeviceID, b'\x01\x06\x01', bytes([pan_speed]), bytes([tilt_speed]), ValueStateValues[value], b'\xFF'])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\x02', 
            'Off'   : b'\x03'
        }

        PowerCmdString = b''.join([self._DeviceID, b'\x01\x04\x00', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        PowerCmdString = b''.join([self._DeviceID, b'\x09\x04\x00\xFF'])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Reset'     : b'\x00',
            'Save'      : b'\x01', 
            'Recall'    : b'\x02'
        }

        action = ActionStates[qualifier['Action']]

        if 0 <= int(value) <= 255:
            PresetCmdString = b''.join([self._DeviceID, b'\x01\x04\x3F', action, bytes([int(value)]), b'\xFF'])
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')
    def SetResetPanTilt(self, value, qualifier):

        ResetPanTiltCmdString = b''.join([self._DeviceID, b'\x01\x06\x05\xFF'])
        self.__SetHelper('ResetPanTilt', ResetPanTiltCmdString, value, qualifier)
    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x02', 
            'Down'  : b'\x03', 
            'Reset' : b'\x00'
        }

        ShutterCmdString = b''.join([self._DeviceID, b'\x01\x04\x0A', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto'              : b'\x35\x00', 
            'Indoor'            : b'\x35\x01', 
            'Outdoor'           : b'\x35\x02',  
            'One Push WB'       : b'\x35\x03', 
            'Manual'            : b'\x35\x05',  
            'One Push Trigger'  : b'\x10\x05'
        }

        WhiteBalanceCmdString = b''.join([self._DeviceID, b'\x01\x04', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Auto', 
            0x01 : 'Indoor', 
            0x02 : 'Outdoor', 
            0x03 : 'One Push WB', 
            0x05 : 'Manual'
        }

        WhiteBalanceCmdString = b''.join([self._DeviceID, b'\x09\x04\x35\xFF'])
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 0,
            'Max' : 7
            }

        ValueStateValues = {
            'Tele' : 0x20, 
            'Wide' : 0x30
        }

        if value == 'Stop':
            zoom_speed = 0x00
        else:
            zoom_speed = ValueStateValues[value] + qualifier['Speed']

        if SpeedConstraints['Min'] <= qualifier['Speed'] <= SpeedConstraints['Max']:
            ZoomCmdString = b''.join([self._DeviceID, b'\x01\x04\x07', bytes([zoom_speed]), b'\xFF'])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')
            
    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorMessageValues = {
            0x02 : 'Syntax Error',
            0x03 : 'Command Buffer Full',
            0x04 : 'Command Canceled',
            0x05 : 'No Socket',
            0x41 : 'Command Not Executable'
        }

        if response:
            if len(response) == 4:
                if response[1] in [0x60, 0x61, 0x62]:
                    errorstring = '{0}: {1}.'.format(sourceCmdName, ErrorMessageValues[response[2]])
                    self.Error([errorstring])
                elif response[1] == 0x50:
                    return response
                else:
                    self.Error(['Invalid/unexpected response'])
                    response = '' 
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or self._DeviceID == b'\x88':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag= b'\xFF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'\x88':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag= b'\xFF')
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

