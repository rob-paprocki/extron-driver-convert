from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait
import time


class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioXP': {'Parameters': ['Destination', 'Source'], 'Status': {}},
            'Bulk': {'Status': {}},
            'ChannelGain': {'Parameters': ['Channel'], 'Status': {}},
            'Commit': {'Status': {}},
            'Copy': {'Status': {}},
            'Fan': {'Parameters': ['Warm', 'Full', 'Critical'], 'Status': {}},
            'FollowPort': {'Parameters': ['Follow'], 'Status': {}},
            'GPO': {'Parameters': ['Port'], 'Status': {}},
            'Lock': {'Parameters': ['Channel'], 'Status': {}},
            'MasterClock': {'Status': {}},
            'MasterClockMultiplier': {'Status': {}},
            'MasterClockSource': {'Status': {}},
            'MidiXP': {'Parameters': ['Destination', 'Source'], 'Status': {}},
            'Off': {'Parameters': ['Start', 'End', 'Value'], 'Status': {}},
            'PolySource': {'Parameters': ['Destination', 'Source'], 'Status': {}},
            'PortFrame': {'Parameters': ['Port'], 'Status': {}},
            'PortGain': {'Parameters': ['Port'], 'Status': {}},
            'PortMode': {'Parameters': ['Port'], 'Status': {}},
            'PortXP': {'Parameters': ['Destination', 'Source'], 'Status': {}},
            'SerialXP': {'Parameters': ['Destination', 'Source'], 'Status': {}},
            'SetMasterClockMultiplier': {'Status': {}},
            'Snapload': {'Status': {}},
            'Termination': {'Status': {}},
            'Unity': {'Parameters': ['Start', 'End'], 'Status': {}},
            'WCKMul': {'Parameters': ['Port'], 'Status': {}}
        }

    def SetAudioXP(self, value, qualifier):

        if 1 <= qualifier['Destination'] <= 1024 and 0 <= qualifier['Source'] <= 1024:
            if value == 'Online':
                AudioXPCmdString = 'audioxp 1 {0} {1}\r\n'.format(qualifier['Destination'], qualifier['Source'])
            else:
                AudioXPCmdString = 'audioxp 2 {0} {1}\r\n'.format(qualifier['Destination'], qualifier['Source'])
            self.__SetHelper('AudioXP', AudioXPCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAudioXP')

    def SetBulk(self, value, qualifier):

        if value == 'Begin':
            self.__SetHelper('Bulk', 'bulk begin\r\n', value, qualifier)
        elif value == 'End':
            self.__SetHelper('Bulk', 'bulk end\r\n', value, qualifier)
        else:
            print('Invalid Command for SetBulk')

    def SetChannelGain(self, value, qualifier):

        if -60 <= value <= 30 and 1 <= qualifier['Channel'] <= 1024:
            ChannelGainCmdString = 'gain {0} {1}\r\n'.format(qualifier['Channel'], "{0:0.1f}".format(value))
            self.__SetHelper('ChannelGain', ChannelGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannelGain')

    def SetCommit(self, value, qualifier):
        self.__SetHelper('Commit', 'commit\r\n', value, qualifier)

    def SetCopy(self, value, qualifier):
        self.__SetHelper('Copy', 'copy\r\n', value, qualifier)
        
    def SetMasterClock(self, value, qualifier):

        if value == 'Enable':
            self.__SetHelper('MasterClock', 'enable_master_clock 1\r\n', value, qualifier)
        elif value == 'Disable':
            self.__SetHelper('MasterClock', 'enable_master_clock 0\r\n', value, qualifier)
        else:
            print('Invalid Command for SetMasterClock')
            
    def SetMasterClockMultiplier(self, value, qualifier):

        if value == 'Enable':
            self.__SetHelper('MasterClockMultiplier', 'enable_master_mul 1\r\n', value, qualifier)
        elif value == 'Disable':
            self.__SetHelper('MasterClockMultiplier', 'enable_master_mul 0\r\n', value, qualifier)
        else:
            print('Invalid Command for SetMasterClockMultiplier')
            
    def SetFan(self, value, qualifier):

        warm = int(qualifier['Warm'])
        full = int(qualifier['Full'])
        crit = int(qualifier['Critical'])

        if 30 <= warm <= 60 and 40 <= full <= 75 and 50 <= crit <= 99 and warm < full < crit:
            FanCmdString = 'fan {0} {1} {2}\r\n'.format(warm, full, crit)
            self.__SetHelper('Fan', FanCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFan')
            
    def SetFollowPort(self, value, qualifier):

        if qualifier['Follow'] == 'Disable':
            FollowPortCmdString = 'follow_port {0} {0}\r\n'.format(value)
            self.__SetHelper('FollowPort', FollowPortCmdString, value, qualifier)
        elif qualifier['Follow'] == 'Master':
            FollowPortCmdString = 'follow_port {0} 17\r\n'.format(value)
            self.__SetHelper('FollowPort', FollowPortCmdString, value, qualifier)
        elif 1 <= int(qualifier['Follow']) <= 16:
            FollowPortCmdString = 'follow_port {0} {1}\r\n'.format(value, qualifier['Follow'])
            self.__SetHelper('FollowPort', FollowPortCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFollowPort')

    def SetGPO(self, value, qualifier):

        if value == 'On':
            GPOCmdString = 'gpo {0} 1\r\n'.format(qualifier['Port'])
            self.__SetHelper('GPO', GPOCmdString, value, qualifier)
        elif value == 'Off':
            GPOCmdString = 'gpo {0} 0\r\n'.format(qualifier['Port'])
            self.__SetHelper('GPO', GPOCmdString, value, qualifier)
        else:
            print('Invalid Command for SetGPO')
            
    def SetLock(self, value, qualifier):

        if value == 'Lock' and 1 <= int(qualifier['Channel']) <= 1024:
            LockCmdString = 'lock {0}\r\n'.format(qualifier['Channel'])
            self.__SetHelper('Lock', LockCmdString, value, qualifier)
        elif value == 'Unlock' and 1 <= int(qualifier['Channel']) <= 1024:
            LockCmdString = 'unlock {0}\r\n'.format(qualifier['Channel'])
            self.__SetHelper('Lock', LockCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLock')
            
    def SetMidiXP(self, value, qualifier):

        if qualifier['Source'] == 'No Connection':
            MidiXPCmdString = 'midixp {0} 0\r\n'.format(qualifier['Destination'])
            self.__SetHelper('MidiXP', MidiXPCmdString, value, qualifier)
        elif 1 <= int(qualifier['Source']) <= 18 and 1 <= int(qualifier['Destination']) <= 18:
            MidiXPCmdString = 'midixp {0} {1}\r\n'.format(qualifier['Destination'], qualifier['Source'])
            self.__SetHelper('MidiXP', MidiXPCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMidiXP')
            
    def SetOff(self, value, qualifier):
        start = int(qualifier['Start'])
        end = int(qualifier['End'])

        if value == 'Online' and 1 <= start <= end <= 1024:
            OffCmdString = 'off 1 {0} {1}\r\n'.format(start, end)
            self.__SetHelper('Off', OffCmdString, value, qualifier)
        elif value == 'Offline' and 1 <= start <= end <= 1024:
            OffCmdString = 'off 2 {0} {1}\r\n'.format(start, end)
            self.__SetHelper('Off', OffCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOff')

    def SetPolySource(self, value, qualifier):
        DestinationStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            'WCK': '17'
        }

        SourceStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            'WCK': '17',
            'Video 44.1 kHz': '18',
            'Video 48 kHz': '19',
            'Internal 44.1 kHz': '20',
            'Internal 48 kHz': '21'
        }

        PolySourceCmdString = 'poly_source {0} {1}'.format(DestinationStates[qualifier['Destination']], SourceStates[qualifier['Source']])
        self.__SetHelper('PolySource', PolySourceCmdString, value, qualifier)

    def SetPortFrame(self, value, qualifier):

        PortFrameCmdString = 'port_frame {0} {1}\r\n'.format(qualifier['Port'], value)
        self.__SetHelper('PortFrame', PortFrameCmdString, value, qualifier)

    def SetPortGain(self, value, qualifier):

        if value == 'All':
            PortGainCmdString = 'portgain_mode 0 {0}'.format(qualifier['Port'])
            self.__SetHelper('PortGain', PortGainCmdString, value, qualifier)
        elif value == 'Unlocked':
            PortGainCmdString = 'portgain_mode 1 {0}'.format(qualifier['Port'])
            self.__SetHelper('PortGain', PortGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPortGain')



    def SetPortMode(self, value, qualifier):

        PortModeCmdString = 'port_mode {0} {1}\r\n'.format(qualifier['Port'], value)
        self.__SetHelper('PortMode', PortModeCmdString, value, qualifier)



    def SetPortXP(self, value, qualifier):
        DestinationStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16'
        }

        SourceStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            'No Connection': '0'
        }

        ValueStateValues = {
            'Online': '1',
            'Offline': '2'
        }

        PortXPCmdString = 'portxp {0} {1} {2}\r\n'.format(ValueStateValues[value], DestinationStates[qualifier['Destination']], SourceStates[qualifier['Source']])
        self.__SetHelper('PortXP', PortXPCmdString, value, qualifier)

    def SetSerialXP(self, value, qualifier):
        DestinationStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20'
        }

        SourceStates = {
            'No Connection': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20'
        }

        SerialXPCmdString = 'serxp {0} {1}\r\n'.format(DestinationStates[qualifier['Destination']], SourceStates[qualifier['Source']])
        self.__SetHelper('SerialXP', SerialXPCmdString, value, qualifier)

    def SetMasterClockSource(self, value, qualifier):
        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            'WCK': '17',
            'Video 44.1 kHz': '18',
            'Video 48 kHz': '19',
            'Internal 44.1 kHz': '20',
            'Internal 48 kHz': '21'
        }

        MasterClockSourceCmdString = 'master_clock {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('MasterClockSource', MasterClockSourceCmdString, value, qualifier)

    def SetSetMasterClockMultiplier(self, value, qualifier):

        if value in ['1', '2', '4']:
            SetMasterClockMultiplierCmdString = 'master_mul {0}\r\n'.format(value)
            self.__SetHelper('SetMasterClockMultiplier', SetMasterClockMultiplierCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSetMasterClockMultiplier')



    def SetSnapload(self, value, qualifier):

        id = int(value)
        if 1 <= id <= 127:
            SnaploadCmdString = 'snapload {0}'.format(id)
            self.__SetHelper('Snapload', SnaploadCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSnapload')

    def SetTermination(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        TerminationCmdString = 'term {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Termination', TerminationCmdString, value, qualifier)

    def SetUnity(self, value, qualifier):
        start = qualifier['Start']
        end = qualifier['End']

        if value == 'Online' and 1 <= start <= end <= 1024:
            UnityCmdString = 'unity 1 {0} {1}\r\n'.format(start, end)
            self.__SetHelper('Unity', UnityCmdString, value, qualifier)
        elif value == 'Offline' and 1 <= start <= end <= 1024:
            UnityCmdString = 'unity 2 {0} {1}\r\n'.format(start, end)
            self.__SetHelper('Unity', UnityCmdString, value, qualifier)
        else:
            print('Invalid Command for SetUnity')

    def SetWCKMul(self, value, qualifier):
        port = int(qualifier['Port'])
        mul = int(value)

        if 1 <= port <= 16 and 1 <= mul <= 4:
            WCKMulCmdString = 'wck_mul {0} {1}\r\n'.format(qualifier['Port'], mul)
            self.__SetHelper('WCKMul', WCKMulCmdString, value, qualifier)
        else:
            print('Invalid Command for SetWCKMul')

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        pass

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)
        except AttributeError:
            print(command, 'does not support Update.')

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback
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
        if self.connectionFlag == False:
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
