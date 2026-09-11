from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack


class DeviceEthernetClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = 'admin'
        self.devicePassword = 'password'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'FocusMode': {'Status': {}},
            'Home': {'Status': {}},
            'Pan': {'Parameters': ['Speed'], 'Status': {}},
            'RecallPreset': {'Status': {}},
            'SetPreset': {'Status': {}},
            'SetTriSync': {'Parameters': ['Speed'], 'Status': {}},
            'Standby': {'Status': {}},
            'Tilt': {'Parameters': ['Speed'], 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'auto_focus:     (on|off)\r\n'), self.__MatchFocusMode, None)
            self.AddMatchString(re.compile(b'standby:        (on|off)\r\n'), self.__MatchStandby, None)
            self.AddMatchString(re.compile(b'login:'), self.__MatchSendUsername, None)
            self.AddMatchString(re.compile(b'\xFF\xFD\x01\xFF\xFD\x1F\xFF\xFB\x01\xFF\xFB\x03'), self.__MatchHandshake, None)
            self.AddMatchString(re.compile(b'ERROR'), self.__MatchError, None)

    def SetFocus(self, value, qualifier):

        FocusStateCommand = {
            'Far': 'far',
            'Near': 'near',
            'Stop': 'stop'
        }

        if 1 <= int(qualifier['Speed']) <= 8:
            speed = int(qualifier['Speed'])
            if value == 'Stop':
                FocusString = 'camera focus stop\r\n'
            else:
                FocusString = 'camera focus {0} {1}\r\n'.format(
                    FocusStateCommand[value], speed)
            self.__SetHelper('Focus', FocusString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'auto',
            'Manual': 'manual'
        }

        FocusModeCmdString = 'camera focus mode {0}\r\n'.format(
            ValueStateValues[value])
        self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def UpdateFocusMode(self, value, qualifier):

        FocusModeCmdString = 'camera focus mode get\r\n'
        self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def __MatchFocusMode(self, match, tag):

        ValueStateValues = {
            'on': 'Auto',
            'off': 'Manual'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FocusMode', value, None)

    def SetHome(self, value, qualifier):

        HomeCmdString = 'camera home\r\n'
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPan(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 24
        }

        ValueStateValues = {
            'Left': 'left',
            'Right': 'right',
            'Stop': 'stop'
        }

        PanSpd = int(qualifier['Speed'])
        if SpeedConstraints['Min'] <= PanSpd <= SpeedConstraints['Max']:
            if value == 'Stop':
                PanCmdString = 'camera pan stop\r\n'
            else:
                PanCmdString = 'camera pan {0} {1}\r\n'.format(ValueStateValues[value], PanSpd)
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')
            
    def SetRecallPreset(self, value, qualifier):
        
        if 1 <= int(value) <= 16:
            cmdValue = int(value)
            PresetCmdString = 'camera preset recall {0}\r\n'.format(cmdValue)
            self.__SetHelper('RecallPreset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')
    def SetSetPreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            cmdValue = int(value)
            PresetCmdString = 'camera preset store {0}\r\n'.format(cmdValue)
            self.__SetHelper('SetPreset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetPreset')
    def SetSetTriSync(self, value, qualifier):

        if 1 <= int(value) <= 16 and 1 <= int(qualifier['Speed']) <= 24:
            cmdValue = int(value)
            speed = int(qualifier['Speed'])
            TriSyncString = 'camera preset store {0} tri-sync {1}\r\n'.format(cmdValue, speed)
            self.__SetHelper('SetTriSync', TriSyncString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetTriSync')
    def SetStandby(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        StandbyCmdString = 'camera standby {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Standby', StandbyCmdString, value, qualifier)

    def UpdateStandby(self, value, qualifier):


        StandbyCmdString = 'camera standby get\r\n'

        self.__UpdateHelper('Standby', StandbyCmdString, value, qualifier)

    def __MatchStandby(self, match, tag):

        ValueStateValues = {
            'on'  : 'On', 
            'off' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Standby', value, None)


    def SetTilt(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 1,
            'Max' : 20
        }

        ValueStateValues = {
            'Up'   : 'up', 
            'Down' : 'down', 
            'Stop' : 'stop'
        }

        TiltSpd = int(qualifier['Speed'])
        if SpeedConstraints['Min'] <= TiltSpd <= SpeedConstraints['Max']:
            if value == 'Stop':
                TiltCmdString = 'camera tilt stop\r\n'
            else:
                TiltCmdString = 'camera tilt {0} {1}\r\n'.format(ValueStateValues[value], TiltSpd)
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')
    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 1,
            'Max' : 7
        }

        ValueStateValues = {
            'In'   : 'in', 
            'Out'  : 'out', 
            'Stop' : 'stop'
        }

        ZoomSpd = int(qualifier['Speed'])
        if SpeedConstraints['Min'] <= ZoomSpd <= SpeedConstraints['Max']:
            if value == 'Stop':
                ZoomCmdString = 'camera zoom stop\r\n'
            else:
                ZoomCmdString = 'camera zoom {0} {1}\r\n'.format(ValueStateValues[value], ZoomSpd)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')
            
    def SetHandshake(self, value, qualifier):

        self.__SetHelper('Handshake', b'\xFF\xFC\x01\xFF\xFC\x1F\xFF\xFE\x01\xFF\xFE\x03', None, None)

    def __MatchHandshake(self, match, tag):


        self.SetHandshake( None, None)
    def SetSendPassword(self, value, qualifier):

        self.Send(self.devicePassword + '\r\n')
    def SetSendUsername(self, value, qualifier):
  
        self.Send(self.deviceUsername + '\r\n')
    def __MatchSendUsername(self, match, tag):


        self.SetSendUsername( None, None)
        self.SetSendPassword( None, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)
        print(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)
            print(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0
        self.Error(['Error'])

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}



    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 


class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.cameraID = 0x81
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': { 'Status': {}},
            'BacklightMode': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'FocusMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Iris': { 'Status': {}},
            'Mute': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'RecallPreset': { 'Status': {}},
            'RecallTriSync': {'Parameters':['Speed'], 'Status': {}},
            'ResetPreset': { 'Status': {}},
            'SetPreset': { 'Status': {}},
            'SetTriSync': {'Parameters':['Speed'], 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }  

        self.regex = re.compile(b'.*(\x41\xFF|\x51\xFF)')
        
    @property
    def DeviceID(self):
        return self.cameraID

    @DeviceID.setter
    def DeviceID(self, value):        
        if 1 <= int(value) <= 7:
            self.cameraID = 0x80 + int(value)

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto'        : 0x00, 
            'Manual'           : 0x03, 
            'Shutter Priority' : 0x0A, 
            'Iris Priority'    : 0x0B, 
            'Bright'           : 0x0D
        }

        AutoExposureCmdString = pack('>6B', self.cameraID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0  : 'Full Auto', 
            3  : 'Manual', 
            10 : 'Shutter Priority', 
            11 : 'Iris Priority', 
            13 : 'Bright'
        }

        AutoExposureCmdString = pack('>5B', self.cameraID, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetBacklightMode(self, value, qualifier):

        BacklightStateCommand = {
            'On' : 0x02,
            'Off': 0x03,
            }
        BacklightString = pack('>6B',self.cameraID,0x01,0x04,0x33,BacklightStateCommand[value],0xFF)
        self.__SetHelper('BacklightMode', BacklightString, value, qualifier)      

    def UpdateBacklightMode(self, value, qualifier):

        BacklightString = pack('>5B',self.cameraID,0x09,0x04,0x33,0xFF)
        res = self.__UpdateHelper('BacklightMode', BacklightString, value, qualifier)
        if res:
            try:
                respID, queryByte, queryData, terminator = unpack('>BBBB', res)
                if (queryByte == 0x50) and (queryData == 0x02):
                    self.WriteStatus('BacklightMode', 'On', None)
                elif (queryByte == 0x50) and (queryData == 0x03):
                    self.WriteStatus('BacklightMode', 'Off', None)
                else:
                    self.Error(['Invalid/Unexpected Response'])
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetFocus(self, value, qualifier):

        FocusStateCommand = {
            'Far' : 0x20,
            'Near': 0x30,
            'Stop': 0x00,
            }

        if 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                focusSpeed = 0x00
            else:
                focusSpeed = int(qualifier['Speed']) + FocusStateCommand[value]
            FocusString = pack('>6B',self.cameraID,0x01,0x04,0x08,focusSpeed,0xFF)
            self.__SetHelper('Focus', FocusString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')
    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'   : 0x02, 
            'Manual' : 0x03
        }

        FocusModeCmdString = pack('>6B', self.cameraID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
        self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            2 : 'Auto', 
            3 : 'Manual'
        }

        FocusModeCmdString = pack('>5B', self.cameraID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        FreezeCmdString = pack('>6B', self.cameraID, 0x01, 0x04, 0x62, ValueStateValues[value], 0xFF)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            2 : 'On', 
            3 : 'Off'
        }

        FreezeCmdString = pack('>5B', self.cameraID, 0x09, 0x04, 0x62, 0xFF)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }

        IrisCmdString = pack('>6B', self.cameraID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)
    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        MuteCmdString = pack('>6B', self.cameraID, 0x01, 0x04, 0x75, ValueStateValues[value], 0xFF)
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            2 : 'On', 
            3 : 'Off'
        }

        MuteCmdString = pack('>5B', self.cameraID, 0x09, 0x04, 0x75, 0xFF)
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetPanTilt(self, value, qualifier):

        PanTiltStateCommand = {
            'Up' : [0x03,0x01],
            'Down' : [0x03,0x02],
            'Left' : [0x01,0x03],
            'Right' : [0x02,0x03],
            'Up Left' : [0x01,0x01],
            'Up Right' : [0x02,0x01],
            'Down Left' : [0x01,0x02],
            'Down Right' : [0x02,0x02],
            'Stop' : [0x03,0x03],
            }
        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])
        if PanSpd <= 0 or PanSpd > 24:
            self.Discard('Invalid Command for SetPanTilt')
        elif TiltSpd <= 0 or TiltSpd > 20:
            self.Discard('Invalid Command for SetPanTilt')
        else:
            PanTiltString = pack('>9B',self.cameraID,0x01,0x06,0x01,PanSpd,TiltSpd,PanTiltStateCommand[value][0],PanTiltStateCommand[value][1],0xFF)
            self.__SetHelper('PanTilt', PanTiltString, value, qualifier)
    def SetPower(self, value, qualifier):

        PowerStateCommand = {
            'On' : 0x02,
            'Off': 0x03,
            }
        PowerString = pack('>6B',self.cameraID,0x01,0x04,0x00,PowerStateCommand[value],0xFF)
        self.__SetHelper('Power', PowerString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerString = pack('>5B',self.cameraID,0x09,0x04,0x00,0xFF)
        res = self.__UpdateHelper('Power', PowerString, value, qualifier)
        if res:
            try:
                respID, queryByte, queryData, terminator = unpack('>BBBB', res)
                if (queryByte == 0x50) and (queryData == 0x02):
                    self.WriteStatus('Power', 'On', None)
                elif (queryByte == 0x50) and (queryData == 0x03):
                    self.WriteStatus('Power', 'Off', None)
                else:
                    self.Error(['Invalid/Unexpected Response'])
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetRecallPreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            cmdValue = int(value) - 1
            PresetString = pack('>7B', self.cameraID, 0x01, 0x04, 0x3F, 0x02, cmdValue, 0xFF)
            self.__SetHelper('RecallPreset', PresetString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')
    def SetRecallTriSync(self, value, qualifier):


        if 1 <= int(value) <= 16 and 1 <= int(qualifier['Speed']) <= 24:
            cmdValue = int(value) - 1
            speed = int(qualifier['Speed'])
            byte1 = speed // 10
            byte2 = speed % 10 
            TriSyncString = pack('>9B', self.cameraID, 0x01, 0x04, 0x3F, 0x12, cmdValue, byte1, byte2, 0xFF)
            self.__SetHelper('RecallTriSync', TriSyncString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallTriSync')
    def SetResetPreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            cmdValue = int(value) - 1
            PresetString = pack('>7B', self.cameraID, 0x01, 0x04, 0x3F, 0x00, cmdValue, 0xFF)
            self.__SetHelper('ResetPreset', PresetString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResetPreset')
    def SetSetPreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            cmdValue = int(value) - 1
            PresetString = pack('>7B', self.cameraID, 0x01, 0x04, 0x3F, 0x01, cmdValue, 0xFF)
            self.__SetHelper('SetPreset', PresetString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetPreset')
    def SetSetTriSync(self, value, qualifier):

        if 1 <= int(value) <= 16 and 1 <= int(qualifier['Speed']) <= 24:
            cmdValue = int(value) - 1
            speed = int(qualifier['Speed'])
            byte1 = speed // 10
            byte2 = speed % 10 
            TriSyncString = pack('>9B', self.cameraID, 0x01, 0x04, 0x3F, 0x11, cmdValue, byte1, byte2, 0xFF)
            self.__SetHelper('SetTriSync', TriSyncString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetTriSync')
    def SetZoom(self, value, qualifier):

        ZoomStateCommand = {
            'Tele' : 0x20,
            'Wide' : 0x30,
            'Stop' : 0x00,
        }

        if 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = int(qualifier['Speed']) + ZoomStateCommand[value]
            ZoomString = pack('>6B', self.cameraID, 0x01, 0x04, 0x07, zoomSpeed, 0xFF)
            self.__SetHelper('Zoom', ZoomString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):
                
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex= self.regex)
            if not res:
                self.Error(['Invalid/Unexpected Response'])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen = 4)
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


    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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
