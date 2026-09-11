from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 5
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CDStatus': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ElapsedTime': {'Status': {}},
            'PlayMode': {'Status': {}},
            'RemainTime': {'Status': {}},
            'Repeat': {'Status': {}},
            'RepeatMode': {'Status': {}},
            'Reset': {'Status': {}},
            'Sleep': {'Status': {}},
            'TapeStatus': {'Status': {}},
            'TotalRemainTime': {'Status': {}},
            'TrackNumber': {'Status': {}},
            'Transport': {'Status': {}},
        }
    def UpdateCDStatus(self, value, qualifier):

        self.UpdateDeviceStatus(value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceState = {
            b'\x30': 'Ready',
            b'\x31': 'Not Ready',
            b'\x32': 'CD Sync',
            b'\x34': 'Sleep'
        }

        CDState = {
            b'\x30': 'Ready',
            b'\x31': 'Not Ready',
            b'\x41': 'Play',
            b'\x42': 'Stop',
            b'\x43': 'Pause',
            b'\x44': 'No Media',
            b'\x45': 'Search',
            b'\x46': 'CD Error',
            b'\x47': 'Disc Loading',
            b'\x48': 'Disc Loading complete',
            b'\x49': 'Tray Opening',
            b'\x4A': 'Tray Closing',
            b'\x4B': 'Scan Play',
            b'\x4C': 'Pause Cue',
            b'\x4D': 'Servo on',
            b'\x4E': 'Disc Read Error'
        }

        TapeState = {
            b'\x30': 'Ready',
            b'\x31': 'Not Ready',
            b'\x41': 'Play',
            b'\x42': 'Stop',
            b'\x44': 'No Media',
            b'\x45': 'Search',
            b'\x61': 'Recording',
            b'\x62': 'Rec Pause',
            b'\x63': 'Rec Mute',
            b'\x64': 'Forward',
            b'\x65': 'Rewind',
            b'\x66': 'Cue',
            b'\x67': 'Review',
            b'\x68': 'Play Mute'
        }

        DeviceStatusCmdString = b'\x02\x30\x30\x00\x00\x00\x03\x36\x33'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = DeviceState[res[3:4]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

            try:
                value = CDState[res[7:8]]
                self.WriteStatus('CDStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

            try:
                trackNum = int(res[11:14].decode())
                self.WriteStatus('TrackNumber', trackNum, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

            try:
                min_ = res[16:19].decode()
                sec = res[19:21].decode()
                self.WriteStatus('ElapsedTime', min_ + ':' + sec, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

            try:
                value = TapeState[res[23:24]]
                self.WriteStatus('TapeStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

    def UpdateElapsedTime(self, value, qualifier):

        self.UpdateDeviceStatus(value, qualifier)

    def SetPlayMode(self, value, qualifier):

        PlayModeState = {
            'Single': b'\x02\x53\x30\x00\x00\x00\x03\x38\x36',
            'Continuous': b'\x02\x53\x31\x00\x00\x00\x03\x38\x37'
        }

        PlayModeCmdString = PlayModeState[value]
        self.__SetHelper('PlayMode', PlayModeCmdString, value, qualifier)

    def UpdatePlayMode(self, value, qualifier):

        PlayModeState = {
            b'\x30': 'Single',
            b'\x31': 'Continuous'
        }

        PlayModeCmdString = b'\x02\x30\x00\x00\x00\x00\x03\x33\x33'
        res = self.__UpdateHelper('PlayMode', PlayModeCmdString, value, qualifier)
        if res:
            try:
                value = PlayModeState[res[5:6]]
                self.WriteStatus('PlayMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePlayMode')

    def UpdateRemainTime(self, value, qualifier):

        RemainTimeCmdString = b'\x02\x30\x31\x00\x00\x00\x03\x36\x34'
        res = self.__UpdateHelper('RemainTime', RemainTimeCmdString, value, qualifier)
        if res:
            try:
                min_ = res[16:19].decode()
                sec = res[19:21].decode()
                self.WriteStatus('RemainTime', min_ + ':' + sec, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateRemainTime')

    def SetRepeat(self, value, qualifier):

        RepeatState = {
            'A Set': b'\x02\x4C\x31\x00\x00\x00\x03\x38\x30',
            'B Set': b'\x02\x4C\x32\x00\x00\x00\x03\x38\x31',
            'Off': b'\x02\x4C\x30\x00\x00\x00\x03\x37\x46'
        }

        RepeatCmdString = RepeatState[value]
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def SetRepeatMode(self, value, qualifier):

        RepeatModeState = {
            'On': b'\x02\x52\x30\x00\x00\x00\x03\x38\x35',
            'Off': b'\x02\x52\x31\x00\x00\x00\x03\x38\x36'
        }

        RepeatModeCmdString = RepeatModeState[value]
        self.__SetHelper('RepeatMode', RepeatModeCmdString, value, qualifier)

    def SetReset(self, value, qualifier):

        ResetCmdString = b'\x02\x20\x00\x00\x00\x00\x03\x32\x33'
        self.__SetHelper('Reset', ResetCmdString, value, qualifier)

    def SetSleep(self, value, qualifier):

        SleepCmdString = b'\x02\x21\x00\x00\x00\x00\x03\x32\x34'
        self.__SetHelper('Sleep', SleepCmdString, value, qualifier)

    def UpdateTapeStatus(self, value, qualifier):

        self.UpdateDeviceStatus(value, qualifier)

    def UpdateTotalRemainTime(self, value, qualifier):

        TotalRemainTimeCmdString = b'\x02\x30\x32\x00\x00\x00\x03\x36\x35'
        res = self.__UpdateHelper('TotalRemainTime', TotalRemainTimeCmdString, value, qualifier)
        if res:
            try:
                min_ = res[16:19].decode()
                sec = res[19:21].decode()
                self.WriteStatus('TotalRemainTime', min_ + ':' + sec, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateTotalRemainTime')

    def SetTrackNumber(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            digit100 = ord(str(value // 100))
            digit10 = ord(str((value // 10) % 10))
            digit1 = ord(str(value % 10))
            BCC = 0x4B + digit100 + digit10 + digit1
            BCCH = ord(hex(BCC).split('0x')[1][0])
            BCCL = ord(hex(BCC).split('0x')[1][1])

            TrackNumberCmdString = pack('>9B', 0x02, 0x48, 0x00, digit100, digit10, digit1, 0x03, BCCH, BCCL)
            self.__SetHelper('TrackNumber', TrackNumberCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTrackNumber')

    def UpdateTrackNumber(self, value, qualifier):
        self.UpdateDeviceStatus(value, qualifier)

    def SetTransport(self, value, qualifier):

        TransportState = {
            'CD Play': b'\x02\x40\x30\x00\x00\x00\x03\x37\x33',
            'Tape Play': b'\x02\x40\x31\x00\x00\x00\x03\x37\x34',
            'CD Pause': b'\x02\x42\x00\x00\x00\x00\x03\x34\x35',
            'CD Stop': b'\x02\x41\x30\x00\x00\x00\x03\x37\x34',
            'Tape Stop': b'\x02\x41\x31\x00\x00\x00\x03\x37\x35',
            'Open': b'\x02\x45\x31\x00\x00\x00\x03\x37\x39',
            'Close': b'\x02\x45\x30\x00\x00\x00\x03\x37\x38',
            'Cue': b'\x02\x46\x00\x00\x00\x00\x03\x34\x39',
            'Skip +': b'\x02\x43\x2B\x00\x00\x00\x03\x37\x31',
            'Skip -': b'\x02\x43\x2D\x00\x00\x00\x03\x37\x33',
            'Fast Forward': b'\x02\x64\x30\x00\x00\x00\x03\x39\x37',
            'Rewind': b'\x02\x65\x30\x00\x00\x00\x03\x39\x38',
            'Record': b'\x02\x63\x00\x00\x00\x00\x03\x36\x36'
        }

        TransportCmdString = TransportState[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x30: 'Invalid Command/Parameter',
            0x31: 'Format Error',
            0x32: 'None track requested',
            0x33: 'None time requested',
            0x35: 'Condition Error'
        }

        if response[0] in [0x02]:
            if response[2] in DEVICE_ERROR_CODES:
                print('{0} Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[2]]))
                response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        Length = {
            'DeviceStatus': 32,
            'PlayMode': 11,
            'RemainTime': 32,
            'TotalRemainTime': 32
        }
    
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=Length[command])
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

        self.lastDeviceStatusUpdate = 0

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
