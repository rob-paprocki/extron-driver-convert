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
        self._DeviceID = 1
        self.Models = {}
        self._DeviceID = b'\x81'


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
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
            'ZoomManual': { 'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\x88'
        elif 1 <= int(value) <= 7:
            self._DeviceID = bytes([0x80 + int(value)])
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
        if res != '':
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

        ValueConstraints = {
            'Min' : 0,
            'Max' : 27
            }

        ValueStateValues = {
            0   : b'\x00\x00',
            1   : b'\x00\x01',
            2   : b'\x00\x02',
            3   : b'\x00\x03',
            4   : b'\x00\x04',
            5   : b'\x00\x05',
            6   : b'\x00\x06',
            7   : b'\x00\x07',
            8   : b'\x00\x08',
            9   : b'\x00\x09',
            10  : b'\x00\x0A',
            11  : b'\x00\x0B',
            12  : b'\x00\x0C',
            13  : b'\x00\x0D',
            14  : b'\x00\x0E',
            15  : b'\x00\x0F',
            16  : b'\x01\x00',
            17  : b'\x01\x01',
            18  : b'\x01\x02',
            19  : b'\x01\x03',
            20  : b'\x01\x04',
            21  : b'\x01\x05',
            22  : b'\x01\x06',
            23  : b'\x01\x07',
            24  : b'\x01\x08',
            25  : b'\x01\x09',
            26  : b'\x01\x0A',
            27  : b'\x01\x0B',
        }


        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = b''.join([self._DeviceID, b'\x01\x04\x4D\x00\x00', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00' : 0,
            b'\x00\x01' : 1,
            b'\x00\x02' : 2,
            b'\x00\x03' : 3,
            b'\x00\x04' : 4,
            b'\x00\x05' : 5,
            b'\x00\x06' : 6,
            b'\x00\x07' : 7,
            b'\x00\x08' : 8,
            b'\x00\x09' : 9,
            b'\x00\x0A' : 10,
            b'\x00\x0B' : 11,
            b'\x00\x0C' : 12,
            b'\x00\x0D' : 13,
            b'\x00\x0E' : 14,
            b'\x00\x0F' : 15,
            b'\x01\x00' : 16,
            b'\x01\x01' : 17,
            b'\x01\x02' : 18,
            b'\x01\x03' : 19,
            b'\x01\x04' : 20,
            b'\x01\x05' : 21,
            b'\x01\x06' : 22,
            b'\x01\x07' : 23,
            b'\x01\x08' : 24,
            b'\x01\x09' : 25,
            b'\x01\x0A' : 26,
            b'\x01\x0B' : 27
        }

        BrightnessCmdString = b''.join([self._DeviceID, b'\x09\x04\x4D\xFF'])
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:6]]
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])

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

        FocusCmdString = b''.join([self._DeviceID, b'\x01\x04\x08', bytes([focus_speed]), b'\xFF'])
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)
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

        ValueConstraints = {
            'Min' : 0,
            'Max' : 30
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GainCmdString = b''.join([self._DeviceID, b'\x01\x04\x4C\x00\x00\x00', bytes([int(value/2)]), b'\xFF'])
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):


        GainCmdString = b''.join([self._DeviceID, b'\x09\x04\x4C\xFF'])
        res = self.__UpdateHelper('Gain', GainCmdString, value, qualifier)
        if res:
            try:
                value = (res[-2])*2
                self.WriteStatus('Gain', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Gain: Invalid/unexpected response'])

    def SetHome(self, value, qualifier):

        HomeCmdString = b''.join([self._DeviceID, b'\x01\x06\x04\xFF'])
        self.__SetHelper('Home', HomeCmdString, value, qualifier)
    def SetIris(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 13
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            IrisCmdString = b''.join([self._DeviceID, b'\x01\x04\x4B\x00\x00\x00', bytes([value]), b'\xFF'])
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):


        IrisCmdString = b''.join([self._DeviceID, b'\x09\x04\x4B\xFF'])
        res = self.__UpdateHelper('Iris', IrisCmdString, value, qualifier)
        if res:
            try:
                value = res[-2]
                self.WriteStatus('Iris', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Iris: Invalid/unexpected response'])

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
    def SetResetPanTilt(self, value, qualifier):

        ResetPanTiltCmdString = b''.join([self._DeviceID, b'\x01\x06\x05\xFF'])
        self.__SetHelper('ResetPanTilt', ResetPanTiltCmdString, value, qualifier)
    def SetShutter(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 21
            }

        ValueStateValues = {
            0   : b'\x00\x00',
            1   : b'\x00\x01',
            2   : b'\x00\x02',
            3   : b'\x00\x03',
            4   : b'\x00\x04',
            5   : b'\x00\x05',
            6   : b'\x00\x06',
            7   : b'\x00\x07',
            8   : b'\x00\x08',
            9   : b'\x00\x09',
            10  : b'\x00\x0A',
            11  : b'\x00\x0B',
            12  : b'\x00\x0C',
            13  : b'\x00\x0D',
            14  : b'\x00\x0E',
            15  : b'\x00\x0F',
            16  : b'\x01\x00',
            17  : b'\x01\x01',
            18  : b'\x01\x02',
            19  : b'\x01\x03',
            20  : b'\x01\x04',
            21  : b'\x01\x05'
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ShutterCmdString = b''.join([self._DeviceID, b'\x01\x04\x4A\x00\x00', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00' : 0,
            b'\x00\x01' : 1,
            b'\x00\x02' : 2,
            b'\x00\x03' : 3,
            b'\x00\x04' : 4,
            b'\x00\x05' : 5,
            b'\x00\x06' : 6,
            b'\x00\x07' : 7,
            b'\x00\x08' : 8,
            b'\x00\x09' : 9,
            b'\x00\x0A' : 10,
            b'\x00\x0B' : 11,
            b'\x00\x0C' : 12,
            b'\x00\x0D' : 13,
            b'\x00\x0E' : 14,
            b'\x00\x0F' : 15,
            b'\x01\x00' : 16,
            b'\x01\x01' : 17,
            b'\x01\x02' : 18,
            b'\x01\x03' : 19,
            b'\x01\x04' : 20,
            b'\x01\x05' : 21
        }

        ShutterCmdString = b''.join([self._DeviceID, b'\x09\x04\x4A\xFF'])
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:6]]
                self.WriteStatus('Shutter', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Shutter: Invalid/unexpected response'])

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
    def SetZoomManual(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 20
            }

        ValueStateValues = {
            1   : b'\x00\x00\x00\x00',
            2   : b'\x01\x08\x05\x01',
            3   : b'\x02\x02\x0B\x0E',
            4   : b'\x02\x08\x0F\x06',
            5   : b'\x02\x0D\x04\x05',
            6   : b'\x03\x00\x08\x06',
            7   : b'\x03\x03\x02\x00',
            8   : b'\x03\x05\x04\x09',
            9   : b'\x03\x07\x01\x0E',
            10  : b'\x03\x08\x0B\x03',
            11  : b'\x03\x0A\x01\x02',
            12  : b'\x03\x0B\x04\x02',
            13  : b'\x03\x0C\x04\x07',
            14  : b'\x03\x0D\x02\x05',
            15  : b'\x03\x0D\x0D\x0F',
            16  : b'\x03\x0E\x07\x0B',
            17  : b'\x03\x0E\x0F\x0B',
            18  : b'\x03\x0F\x06\x04',
            19  : b'\x03\x0F\x0B\x0A',
            20  : b'\x04\x00\x00\x00'
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ZoomManualCmdString = b''.join([self._DeviceID, b'\x01\x04\x47', ValueStateValues[value], b'\xFF'])
            self.__SetHelper('ZoomManual', ZoomManualCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomManual')

    def UpdateZoomManual(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00\x00\x00': 1,
            b'\x01\x08\x05\x01': 2,
            b'\x02\x02\x0B\x0E': 3,
            b'\x02\x08\x0F\x06': 4,
            b'\x02\x0D\x04\x05': 5,
            b'\x03\x00\x08\x06': 6,
            b'\x03\x03\x02\x00': 7,
            b'\x03\x05\x04\x09': 8,
            b'\x03\x07\x01\x0E': 9,
            b'\x03\x08\x0B\x03': 10,
            b'\x03\x0A\x01\x02': 11,
            b'\x03\x0B\x04\x02': 12,
            b'\x03\x0C\x04\x07': 13,
            b'\x03\x0D\x02\x05': 14,
            b'\x03\x0D\x0D\x0F': 15,
            b'\x03\x0E\x07\x0B': 16,
            b'\x03\x0E\x0F\x0B': 17,
            b'\x03\x0F\x06\x04': 18,
            b'\x03\x0F\x0B\x0A': 19,
            b'\x04\x00\x00\x00': 20
        }

        ZoomManualCmdString = b''.join([self._DeviceID, b'\x09\x04\x47\xFF'])
        res = self.__UpdateHelper('ZoomManual', ZoomManualCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:6]]
                self.WriteStatus('ZoomManual', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Zoom Manual: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorMessageValues = {
            0x02 : 'Syntax Error',
            0x03 : 'Command Buffer Full',
            0x04 : 'Command Canceled',
            0x05 : 'No Socket',
            0x41 : 'Command Not Executable'
        }

        if response:
            if len(response) == 4 or len(response) == 6:
                if response[1] == 0x60:
                    errorstring = '{0}: {1}.'.format(sourceCmdName, ErrorMessageValues[response[2]])
                    self.Error([errorstring])
                elif response[1] == 0x50:
                    return response
                else:
                    self.Error(['{0}: Invalid/unexpected response'.format(sourceCmdName)])
                    response = '' 
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True



        
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