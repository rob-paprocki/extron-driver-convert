from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}
        self.DeviceID = '1'
        self.Commands = {
            'Alarm': {'Status': {}},
            'AlarmDuration': {'Status': {}},
            'AlarmTime': {'Parameters': ['Position', 'Seconds', 'Minutes', 'Hours'], 'Status': {}},
            'CounterSet': {'Status': {}},
            'CounterTime': {'Parameters': ['Type'], 'Status': {}},
            'OperatingMode': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'TimerControlOperatingMode': {'Status': {}},
            'TimerControlTimerCounterDirection': {'Status': {}},
            'TimerTime': {'Parameters': ['Type', 'Seconds', 'Minutes', 'Hours'], 'Status': {}},
            'TimerCounterControl': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = '{0:02}'.format(int(value))
        else:
            print('Invalid Device ID Parameter.')

    def SetAlarm(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 2,
            'Disable': 0
        }

        AlarmCmdString = '*!{0}49{1:02}{2:>27}'.format(self._DeviceID, ValueStateValues[value], '#')
        self.__SetHelper('Alarm', AlarmCmdString, value, qualifier)

    def SetAlarmDuration(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 50
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AlarmDurationCmdString = '*!{0}48{1:02}{2:>27}'.format(self._DeviceID, value, '#')
            self.__SetHelper('AlarmDuration', AlarmDurationCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAlarmDuration')

    def SetAlarmTime(self, value, qualifier):

        if 1 <= int(qualifier['Position']) <= 99 and 0 <= int(qualifier['Seconds']) <= 60 and 0 <= int(qualifier['Minutes']) <= 60 and 0 <= int(qualifier['Hours']) <= 99:
            AlarmTimeCmdString = '*!{0}41{1:02}{2:02}{3:02}{4:02}{5:>21}'.format(self._DeviceID, int(qualifier['Position']), qualifier['Seconds'], qualifier['Minutes'], qualifier['Hours'], '#')
            self.__SetHelper('AlarmTime', AlarmTimeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAlarmTime')

    def SetCounterSet(self, value, qualifier):

        ValueConstraints = {
            'Min': -99999999,
            'Max': 99999999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CounterSetCmdString = '*!{0}57{1:09}{2:>20}'.format(self._DeviceID, value, '#')
            self.__SetHelper('CounterSet', CounterSetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCounterSet')

    def SetCounterTime(self, value, qualifier):

        TypeStates = {
            'Start': 56,
            'End': 55
        }

        ValueConstraints = {
            'Min': -99999999,
            'Max': 99999999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CounterTimeCmdString = '*!{0}{1}{2:09}{3:>20}'.format(self._DeviceID, TypeStates[qualifier['Type']], value, '#')
            self.__SetHelper('CounterTime', CounterTimeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCounterTime')

    def SetOperatingMode(self, value, qualifier):

        ValueStateValues = {
            'Real Time Clock': 1,
            'Up Timer': 2,
            'Down Timer': 3,
            'Up Counter': 4,
            'Down Counter': 5
        }

        OperatingModeCmdString = '*!{0}10{1}{2:>28}'.format(self._DeviceID, ValueStateValues[value], '#')
        self.__SetHelper('OperatingMode', OperatingModeCmdString, value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        PresetRecallCmdString = '*!{0}13{1:>29}'.format(self._DeviceID, '#')
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        PresetSaveCmdString = '*!{0}12{1:>29}'.format(self._DeviceID, '#')
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetTimerControlOperatingMode(self, value, qualifier):

        ValueStateValues = {
            'Resume real time': 1,
            'Stay in timer mode': 2,
            'Enable split time display': 3,
            'Enable alarm schedule switching': 4
        }

        TimerControlOperatingModeCmdString = '*!{0}65{1}{2:>28}'.format(self._DeviceID, ValueStateValues[value], '#')
        self.__SetHelper('TimerControlOperatingMode', TimerControlOperatingModeCmdString, value, qualifier)

    def SetTimerControlTimerCounterDirection(self, value, qualifier):

        ValueStateValues = {
            'Up': 0,
            'Down': 1
        }

        TimerControlTimerCounterDirectionCmdString = '*!{0}66{1}{2:>28}'.format(self._DeviceID, ValueStateValues[value], '#')
        self.__SetHelper('TimerControlTimerCounterDirection', TimerControlTimerCounterDirectionCmdString, value, qualifier)

    def SetTimerTime(self, value, qualifier):

        TypeStates = {
            'Start': 53,
            'End': 52
        }

        if 0 <= int(qualifier['Seconds']) <= 60 and 0 <= int(qualifier['Minutes']) <= 60 and 0 <= int(qualifier['Hours']) <= 99:
            TimerTimeCmdString = '*!{0}{1}{2:02}{3:02}{4:02}{5:>23}'.format(self._DeviceID, TypeStates[qualifier['Type']], qualifier['Seconds'], qualifier['Minutes'], qualifier['Hours'], '#')
            self.__SetHelper('TimerTime', TimerTimeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTimerTime')

    def SetTimerCounterControl(self, value, qualifier):

        ValueStateValues = {
            'Start Timer/Pause Timer/Increment Counter': 61,
            'Timer Control/Decrement Counter': 62,
            'Reset': 63
        }

        TimerCounterControlCmdString = '*!{0}{1:02}{2:>29}'.format(self._DeviceID, ValueStateValues[value], '#')
        self.__SetHelper('TimerCounterControl', TimerCounterControlCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
