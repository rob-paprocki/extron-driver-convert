from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}
        self._DeviceID = b'\x01'

        self.Commands = {
            'Clock': {'Parameters': ['Flash Display', 'Timer Control', 'Countdown Timer', 'Display Colons', 'AM PM Indicator', 'Mode'], 'Status': {}},
        }      

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\x00'
        elif 1 <= int(value) <= 15:
            self._DeviceID = pack('>B', int(value))
        else:
            initError.append('Device ID not in range 1 - 15, or Broadcast.')

    def SetClock(self, value, qualifier):

        FlashDisplayStates = {
            'On': 128,
            'Off': 0
        }

        TimerControlStates = {
            'Use New Value': 0,
            'Resume Old Timer': 8
        }

        CountdownTimerStates = {
            'Start': 0,
            'Stop': 4
        }

        DisplayColonsStates = {
            'On': 2,
            'Off': 0
        }

        AMPMIndicatorStates = {
            'On': 1,
            'Off': 0
        }

        ModeStates = {
            'ASCII': b'\x00',
            'Number': b'\x01',
            'Graphic': b'\x02',
            '12 Hour': b'\x03',
            '24 Hour': b'\x04',
            'Countdown Timer': b'\x05',
            'Display Version': b'\x06',
            'Preset Day Counter': b'\x07'
        }
        clockStr = value
        if clockStr is None or len(clockStr) != 6:
            print('Invalid Command for SetClock')
        else:
            settingsValue = FlashDisplayStates[qualifier['Flash Display']] + TimerControlStates[qualifier['Timer Control']] + CountdownTimerStates[qualifier['Countdown Timer']] + DisplayColonsStates[qualifier['Display Colons']] + AMPMIndicatorStates[qualifier['AM PM Indicator']]
            ClockCmdString = b'\x11' + self.DeviceID + ModeStates[qualifier['Mode']] + clockStr.encode(encoding='iso-8859-1') + pack('>B', settingsValue)
            self.__SetHelper('Clock', ClockCmdString, value, qualifier)

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

    def __init__(self, Host, Port, Baud=2400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
