from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CleanCancel': {'Parameters': ['Load ID'], 'Status': {}},
            'Clean': {'Parameters': ['Load ID'], 'Status': {}},
            'FadeLoad': {'Parameters': ['Load ID', 'Fade Time'], 'Status': {}},
            'ForceOn': {'Parameters': ['Load ID'], 'Status': {}},
            'ForceOnCancel': {'Parameters': ['Load ID'], 'Status': {}},
            'HoursMode': {'Status': {}},
            'Load': {'Parameters': ['Load ID'], 'Status': {}},
            'LockButtons': {'Parameters': ['Time Delay'], 'Status': {}},
            'MasterRamp': {'Parameters': ['Rate'], 'Status': {}},
            'MasterRampStop': {'Status': {}},
            'Profile': {'Status': {}},
            'Ramp': {'Parameters': ['Load ID', 'Rate'], 'Status': {}},
            'RampStop': {'Parameters': ['Load ID'], 'Status': {}},
            'RecallScene': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'SaveScene': {'Status': {}},
            'UnlockButtons': {'Status': {}},
        }

        self.FirstLoad = True

        if self.Unidirectional == 'False':

            self.AddMatchString(re.compile(b'[RS]: ?(?:GETLOAD|LOAD) (\d{1,2}) (\d{1,3})\r'), self.__MatchLoad, None)
            self.AddMatchString(re.compile(b'S: ?PROFILE (\d{1,2})\r'), self.__MatchProfile, None)
            self.AddMatchString(re.compile(b'S: ?SCENE (\d{1,2})\r'), self.__MatchRecallScene, None)
            self.AddMatchString(re.compile(b'R: ?VERSION (.*)\r'), self.__MatchFirmwareVersion, None)

    def SetCleanCancel(self, value, qualifier):

        if 1 <= int(qualifier['Load ID']) <= 64:
            CleanCancelCmdString = 'CLEANCANCEL {0}\r'.format(qualifier['Load ID'])
            self.__SetHelper('CleanCancel', CleanCancelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCleanCancel')

    def SetClean(self, value, qualifier):

        if (1 <= value <= 100) and (1 <= int(qualifier['Load ID']) <= 64):
            CleanCmdString = 'CLEAN {0} {1}\r'.format(qualifier['Load ID'], value)
            self.__SetHelper('Clean', CleanCmdString, value, qualifier)
        else:
            print('Invalid Command for SetClean')

    def SetFadeLoad(self, value, qualifier):

        if (0 <= value <= 100) and (1 <= int(qualifier['Load ID']) <= 64) and (0 <= qualifier['Fade Time'] <= 64800):
            FadeLoadCmdString = 'FADELOAD {0} {1} {2}\r'.format(qualifier['Load ID'], value, qualifier['Fade Time'])
            self.__SetHelper('FadeLoad', FadeLoadCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFadeLoad')

    def SetForceOn(self, value, qualifier):

        if (1 <= value <= 100) and (1 <= int(qualifier['Load ID']) <= 64):
            ForceOnCmdString = 'FORCEON {0} {1}\r'.format(qualifier['Load ID'], value)
            self.__SetHelper('ForceOn', ForceOnCmdString, value, qualifier)
        else:
            print('Invalid Command for SetForceOn')

    def SetForceOnCancel(self, value, qualifier):

        if 1 <= int(qualifier['Load ID']) <= 64:
            ForceOnCancelCmdString = 'FORCEONCANCEL {0}\r'.format(qualifier['Load ID'])
            self.__SetHelper('ForceOnCancel', ForceOnCancelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetForceOnCancel')

    def SetHoursMode(self, value, qualifier):

        ValueStateValues = {
            'Normal Hours': 'NORMALHOURS \r',
            'After Hours': 'AFTERHOURS \r'
        }

        HoursModeCmdString = ValueStateValues[value]
        self.__SetHelper('HoursMode', HoursModeCmdString, value, qualifier)

    def SetLoad(self, value, qualifier):

        if (0 <= value <= 100) and (1 <= int(qualifier['Load ID']) <= 64):
            LoadCmdString = 'LOAD {0} {1}\r'.format(qualifier['Load ID'], value)
            self.__SetHelper('Load', LoadCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLoad')

    def UpdateLoad(self, value, qualifier):

        if 1 <= int(qualifier['Load ID']) <= 64:
            LoadCmdString = 'GETLOAD {0}\r'.format(qualifier['Load ID'])
            self.__UpdateHelper('Load', LoadCmdString, value, qualifier)

            if self.FirstLoad:
                LoadCmdString = 'STATUS LOAD\r'
                self.__UpdateHelper('Load', LoadCmdString, value, qualifier)
                self.FirstLoad = False
        else:
            print('Invalid Command for UpdateLoad')

    def __MatchLoad(self, match, tag):

        value = int(match.group(2).decode())
        if value != 255:
            self.WriteStatus('Load', value, {'Load ID': match.group(1).decode()})
        else:
            print('Load: Invalid/Unexpected Response')

    def SetLockButtons(self, value, qualifier):

        if 0 <= qualifier['Time Delay'] <= 240:
            LockButtonsCmdString = 'LOCKBUTTONS {0}\r'.format(qualifier['Time Delay'])
            self.__SetHelper('LockButtons', LockButtonsCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLockButtons')

    def SetMasterRamp(self, value, qualifier):

        ValueStateValues = {
            'Up': 'UP',
            'Down': 'DOWN'
        }

        if 1 <= qualifier['Rate'] <= 100:
            MasterRampCmdString = 'MASTERRAMP{0} {1}\r'.format(ValueStateValues[value], qualifier['Rate'])
            self.__SetHelper('MasterRamp', MasterRampCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMasterRamp')

    def SetMasterRampStop(self, value, qualifier):

        MasterRampStopCmdString = 'MASTERRAMPSTOP \r'
        self.__SetHelper('MasterRampStop', MasterRampStopCmdString, value, qualifier)

    def SetProfile(self, value, qualifier):

        if 1 <= int(value) <= 16:
            ProfileCmdString = 'CHANGEPROFILE {0}\r'.format(value)
            self.__SetHelper('Profile', ProfileCmdString, value, qualifier)
        else:
            print('Invalid Command for SetProfile')

    def UpdateProfile(self, value, qualifier):

        ProfileCmdString = 'STATUS PROFILE\r'
        self.__UpdateHelper('Profile', ProfileCmdString, value, qualifier)

    def __MatchProfile(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Profile', value, None)

    def SetRamp(self, value, qualifier):

        ValueStateValues = {
            'Up': 'UP',
            'Down': 'DOWN'
        }

        if (1 <= qualifier['Rate'] <= 100) and (1 <= int(qualifier['Load ID']) <= 64):
            RampCmdString = 'RAMP{0} {1} {2}\r'.format(ValueStateValues[value], qualifier['Load ID'], qualifier['Rate'])
            self.__SetHelper('Ramp', RampCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRamp')

    def SetRampStop(self, value, qualifier):

        if 1 <= int(qualifier['Load ID']) <= 64:
            RampStopCmdString = 'RAMPSTOP {0}\r'.format(qualifier['Load ID'])
            self.__SetHelper('RampStop', RampStopCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRampStop')

    def SetRecallScene(self, value, qualifier):

        if 1 <= int(value) <= 16:
            RecallSceneCmdString = 'SCENE {0}\r'.format(value)
            self.__SetHelper('RecallScene', RecallSceneCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRecallScene')

    def UpdateRecallScene(self, value, qualifier):

        RecallSceneCmdString = 'STATUS SCENE\r'
        self.__UpdateHelper('RecallScene', RecallSceneCmdString, value, qualifier)

    def __MatchRecallScene(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('RecallScene', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'VERSION \r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetSaveScene(self, value, qualifier):

        if 1 <= int(value) <= 16:
            SaveSceneCmdString = 'SETSCENE {0}\r'.format(value)
            self.__SetHelper('SaveScene', SaveSceneCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSaveScene')

    def SetUnlockButtons(self, value, qualifier):

        UnlockButtonsCmdString = 'UNLOCKBUTTONS\r'
        self.__SetHelper('UnlockButtons', UnlockButtonsCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.FirstLoad = True

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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
