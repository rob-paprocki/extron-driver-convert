from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack

class DeviceClass:

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DownTimer': {'Status': {}},
            'DownTimerMode': {'Parameters': ['Timer Display Mode', 'Alarm', 'Alarm Duration', 'Hour', 'Minute', 'Second', 'Tenths of a Second'], 'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'TimeMode': {'Status': {}},
            'TimerTimeWhileRunning': {'Status': {}},
            'TimerTimeWhileRunningCentiseconds': {'Status': {}},
            'TimerTimeWhileRunningDeciseconds': {'Status': {}},
            'TimerTimeWhileRunningHours': {'Status': {}},
            'TimerTimeWhileRunningMinutes': {'Status': {}},
            'TimerTimeWhileRunningSeconds': {'Status': {}},
            'UpTimer': {'Status': {}},
            'UpTimerMode': {'Parameters': ['Timer Display Mode'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'[\x04\x05][\x00-\xFF]{10}([\x00-\xFF]{2})[\x00-\x02][\x00-\xFF]{67}'), self.__MatchFirmwareVersion, None)

    def SetDownTimer(self, value, qualifier):

        ValueStateValues = {
            'Start': b'\xA6\x01\x00',
            'Pause': b'\xA6\x00\x00'
        }

        DownTimerCmdString = ValueStateValues[value]
        self.__SetHelper('DownTimer', DownTimerCmdString, value, qualifier)

    def SetDownTimerMode(self, value, qualifier):

        TimerDisplayModeStates = {
            'MIN:SEC.Tenths': 0x00,
            'HH:MM:SS': 0x01
        }

        AlarmStates = {
            'Enabled': 0x01,
            'Disabled': 0x00
        }

        HourConstraints = {
            'Min': 0,
            'Max': 23
        }

        MinuteConstraints = {
            'Min': 0,
            'Max': 59
        }

        SecondConstraints = {
            'Min': 0,
            'Max': 59
        }

        DecisecondConstraints = {
            'Min': 0,
            'Max': 9
        }

        AlarmDurationConstraints = {
            'Min': 0,
            'Max': 59
        }

        ValueStateValues = {
            'Set': 0xA5,
            'Reset': 0xA7
        }

        try:
            timerMode_val = qualifier['Timer Display Mode']
            alarm_val = qualifier['Alarm']
            hour_val = qualifier['Hour']
            minute_val = qualifier['Minute']
            second_val = qualifier['Second']
            decisecond_val = qualifier['Tenths of a Second']
            alarm_duration_val =  qualifier['Alarm Duration']
        except KeyError:
            self.Error(['Missing qualifiers for DownTimerMode command'])
        else:
            if (timerMode_val in TimerDisplayModeStates and alarm_val in AlarmStates and
                    all(val is not None for val in [hour_val, minute_val, second_val, decisecond_val, alarm_duration_val]) and
                    HourConstraints['Min'] <= hour_val <= HourConstraints['Max'] and
                    MinuteConstraints['Min'] <= minute_val <= MinuteConstraints['Max'] and
                    SecondConstraints['Min'] <= second_val <= SecondConstraints['Max'] and
                    DecisecondConstraints['Min'] <= decisecond_val <= DecisecondConstraints['Max'] and
                    AlarmDurationConstraints['Min'] <= alarm_duration_val <= AlarmDurationConstraints['Max']):

                DownTimerModeCmdString = pack('8B',
                                              ValueStateValues[value],
                                              TimerDisplayModeStates[timerMode_val],
                                              hour_val,
                                              minute_val,
                                              second_val,
                                              decisecond_val,
                                              AlarmStates[alarm_val],
                                              alarm_duration_val)

                self.__SetHelper('DownTimerMode', DownTimerModeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDownTimerMode')

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = b'\xA1\x04\xB2'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = '{major}.{minor}'.format(major=str(match.group(1)[0]), minor=str(match.group(1)[1]))
        self.WriteStatus('FirmwareVersion', value, None)

    def SetTimeMode(self, value, qualifier):

        TimeModeCmdString = b'\xA8\x01\x00'
        self.__SetHelper('TimeMode', TimeModeCmdString, value, qualifier)

    def SetTimerTimeWhileRunning(self, value, qualifier):

        HourConstraints = {
            'Min': 0,
            'Max': 23
        }

        MinuteConstraints = {
            'Min': 0,
            'Max': 59
        }

        SecondConstraints = {
            'Min': 0,
            'Max': 59
        }

        DecisecondConstraints = {
            'Min': 0,
            'Max': 9
        }

        CentisecondConstraints = {
            'Min': 0,
            'Max': 9
        }

        ValueStateValues = {
            'Up': 0xAA,
            'Down': 0xAB
        }
        try:
            hour_val = qualifier['Hour']
            minute_val = qualifier['Minute']
            second_val = qualifier['Second']
            decisecond_val =  qualifier['Tenths of a Second']
            centisecond_val = qualifier['Hundredths of a Second']
        except KeyError:
            self.Error(['Missing qualifier for TimerTimeWhileRunning'])

        if (all(val is not None for val in [hour_val, minute_val, second_val, decisecond_val, centisecond_val]) and
                HourConstraints['Min'] <= hour_val <= HourConstraints['Max'] and
                MinuteConstraints['Min'] <= minute_val <= MinuteConstraints['Max'] and
                SecondConstraints['Min'] <= second_val <= SecondConstraints['Max'] and
                DecisecondConstraints['Min'] <= decisecond_val <= DecisecondConstraints['Max'] and
                CentisecondConstraints['Min'] <= centisecond_val <= CentisecondConstraints['Max']):

            TimerTimeWhileRunningCmdString = pack('6B',
                                                  ValueStateValues[value],
                                                  hour_val,
                                                  minute_val,
                                                  second_val,
                                                  decisecond_val,
                                                  centisecond_val)

            self.__SetHelper('TimerTimeWhileRunning', TimerTimeWhileRunningCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTimerTimeWhileRunning')

    def SetUpTimer(self, value, qualifier):

        ValueStateValues = {
            'Start': b'\xA3\x01\x00',
            'Pause': b'\xA3\x00\x00'
        }

        UpTimerCmdString = ValueStateValues[value]
        self.__SetHelper('UpTimer', UpTimerCmdString, value, qualifier)

    def SetUpTimerMode(self, value, qualifier):

        TimerDisplayModeStates = {
            'MIN:SEC.Tenths': 0x00,
            'HH:MM:SS': 0x01
        }

        ValueStateValues = {
            'Set': 0xA2,
            'Reset': 0xA4
        }

        timerMode_val = qualifier['Timer Display Mode']
        if timerMode_val in TimerDisplayModeStates:
            UpTimerModeCmdString = pack('3B', ValueStateValues[value], TimerDisplayModeStates[timerMode_val], 0x00)
            self.__SetHelper('UpTimerMode', UpTimerModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUpTimerMode')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


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
