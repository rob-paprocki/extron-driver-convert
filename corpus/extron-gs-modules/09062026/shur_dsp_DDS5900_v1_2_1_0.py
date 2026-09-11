from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from collections import OrderedDict


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
        self._MicrophoneListDisplayCount = 10
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AllMicrophonesOffStatus': {'Status': {}},
            'AudioPath': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'DelegateSpeakersMax': {'Status': {}},
            'DelegateMicrophonesOff': {'Status': {}},
            'InterruptMode': {'Status': {}},
            'LineInputLevel': {'Status': {}},
            'LineOutputLevel': {'Parameters': ['Output'], 'Status': {}},
            'LoudspeakerLevel': {'Status': {}},
            'MicrophoneControl': {'Parameters': ['Seat'], 'Status': {}},
            'MicrophoneList': {'Parameters': ['Position'], 'Status': {}},
            'MicrophoneListMute': {'Parameters': ['Position'], 'Status': {}},
            'MicrophoneListNavigation': {'Parameters': ['Step'], 'Status': {}},
            'MicrophoneListRefresh': {'Status': {}},
            'OperationMode': {'Status': {}},
            'RequestListClear': {'Status': {}},
            'RequestListControl': {'Parameters': ['Seat'], 'Status': {}},
            'RequestListMax': {'Status': {}},
            'RequestListNext': {'Status': {}},
            'RequestListStatus': {'Parameters': ['Seat'], 'Status': {}},
            'Status': {'Status': {}},  # invisible
            'TotalSpeakersMax': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'mic_all_off\r'), self.__MatchAllMicrophonesOffStatus, None)
            self.AddMatchString(re.compile(b'audio_path (mic|linein_1)_to_(speaker|lineout_[A-D]|floor) (on|off)\r'), self.__MatchAudioPath, None)
            self.AddMatchString(re.compile(b'max_speakers ([1-8])\r'), self.__MatchDelegateSpeakersMax, None)
            self.AddMatchString(re.compile(b'mic_interrupt (on|off)\r'), self.__MatchInterruptMode, None)
            self.AddMatchString(re.compile(b'line_input_level_1 (-?[0-9]{1,2})\r'), self.__MatchLineInputLevel, None)
            self.AddMatchString(re.compile(b'line_output_volume ([A-D]) (-?[0-9]{1,2})\r'), self.__MatchLineOutputLevel, None)
            self.AddMatchString(re.compile(b'loudspeaker_volume (-?[0-9]{1,2})\r'), self.__MatchLoudspeakerLevel, None)
            self.AddMatchString(re.compile(b'mic_(on|off) ([0-9]{1,5}).*?\r'), self.__MatchMicrophoneControl, None)
            self.AddMatchString(re.compile(b'mic_mode (auto|fifo|manual|vox)\r'), self.__MatchOperationMode, None)
            self.AddMatchString(re.compile(b'max_requests ([0-9]{1,3})\r'), self.__MatchRequestListMax, None)
            self.AddMatchString(re.compile(b'mic_request_(on|off) ([0-9]{1,5}).*?\r'), self.__MatchRequestListStatus, None)
            self.AddMatchString(re.compile(b'max_total_speakers ([1-8])\r'), self.__MatchTotalSpeakersMax, None)
            self.AddMatchString(re.compile(b'command_error (unknown command|syntax error)\r'), self.__MatchError, None)

        self.micDirectory = Directory(self.MicrophoneListDisplayCount, filler='')
        self.micDirectory.write_status_function = self.WriteStatus

        self.seatNumberPattern = re.compile('seat_state (\d+) active (.*)\r')
        self.MicrophoneNameDict = OrderedDict()
        self.MicrophoneListPosition = {}

    @property
    def MicrophoneListDisplayCount(self):
        return self._MicrophoneListDisplayCount

    @MicrophoneListDisplayCount.setter
    def MicrophoneListDisplayCount(self, value):
        if 1<= int(value)<= 15:
            self._MicrophoneListDisplayCount = int(value)
        else:
            print('Invalid MicrophoneListDisplayCount value, valid range is from 1 to 15')

    def SetMicrophoneListMute(self, value, qualifier):

        position = qualifier['Position']
        if 1 <= int(position) <= 10:
            seatString = self.ReadStatus('MicrophoneList', {'Position': position})
            if seatString and seatString != '***End of List***':
                seatNumber = int(seatString.split('-')[0].strip())
                self.SetMicrophoneControl(value, {'Seat': seatNumber})
                #forcing
                micStatus = self.ReadStatus('MicrophoneControl', {'Seat': seatNumber})
                self.WriteStatus('MicrophoneListMute', micStatus, {'Position': position})

                self.MicrophoneListPosition[seatString] = position
        else:
            self.Discard('Invalid Command for SetMicrophoneListMute')

    def SetMicrophoneListNavigation(self, value, qualifier):

        step_size = int(qualifier['Step'])
        if 1 <= step_size <= 10:
            if value == 'Up':
                self.micDirectory.scroll_up(step_size)
            elif value == 'Down':
                self.micDirectory.scroll_down(step_size)
            for i in range(1, self.MicrophoneListDisplayCount + 1):
                seatString = self.ReadStatus('MicrophoneList', {'Position': str(i)})
                if seatString and '-' in seatString:
                    seatNumber = seatString.split('-')[0].strip()
                    micStatus = self.ReadStatus('MicrophoneControl', {'Seat': int(seatNumber)})
                    self.WriteStatus('MicrophoneListMute', micStatus, {'Position': str(i)})
                    self.MicrophoneListPosition[seatString] = str(i)
                else:
                    self.WriteStatus('MicrophoneListMute', 'N/A', {'Position': str(i)})
        else:
            self.Discard('Invalid Command for SetMicrophoneListNavigation')

    def SetMicrophoneListRefresh(self, value, qualifier):

        MicrophoneListRefreshCmdString = 'mic_status\r'
        res = self.__SetHelper('MicrophoneListRefresh', MicrophoneListRefreshCmdString, value, qualifier)
        if res:
            self.MicrophoneNameDict = OrderedDict(self.seatNumberPattern.findall(res))
            micList = []
            for i in self.MicrophoneNameDict:
                temp = '{0} - {1}'.format(i, self.MicrophoneNameDict[i])
                micList.append(temp)
                self.MicrophoneListPosition[temp] = 0
            micList.append('***End of List***')
            self.micDirectory.reset(micList)
            for i in range(1, self.MicrophoneListDisplayCount + 1):
                tempStr = self.ReadStatus('MicrophoneList', {'Position': str(i)})
                if tempStr and '-' in tempStr:
                    seatNumber = tempStr.split('-')[0].strip()
                    tempMute = self.ReadStatus('MicrophoneControl', {'Seat': int(seatNumber)})
                    if tempMute is None:
                        tempMute = 'Off'
                        self.WriteStatus('MicrophoneControl', tempMute, {'Seat': int(seatNumber)})
                    self.MicrophoneListPosition[tempStr] = str(i)
                    self.WriteStatus('MicrophoneListMute', tempMute, {'Position': str(i)})
                else:
                    self.WriteStatus('MicrophoneListMute', 'N/A', {'Position': str(i)})

    def __MatchAllMicrophonesOffStatus(self, match, tag):

        self.WriteStatus('AllMicrophonesOffStatus', 'Enable', None)

    def SetAudioPath(self, value, qualifier):

        InputStates = {
            'Microphones': 'mic',
            'Line Input': 'linein_1'
        }

        OutputStates = {
            'Speakers': 'speaker',
            'Line Output A': 'lineout_A',
            'Line Output B': 'lineout_B',
            'Line Output C': 'lineout_C',
            'Line Output D': 'lineout_D',
            'Floor': 'floor'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        input_ = qualifier['Input']
        output = qualifier['Output']
        if input_ in InputStates and output in OutputStates:
            AudioPathCmdString = 'audio_path {0}_to_{1} {2}\r'.format(InputStates[input_], OutputStates[output], ValueStateValues[value])
            self.__SetHelper('AudioPath', AudioPathCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioPath')

    def __MatchAudioPath(self, match, tag):

        InputStates = {
            'mic': 'Microphones',
            'linein_1': 'Line Input'
        }

        OutputStates = {
            'speaker': 'Speakers',
            'lineout_A': 'Line Output A',
            'lineout_B': 'Line Output B',
            'lineout_C': 'Line Output C',
            'lineout_D': 'Line Output D',
            'floor': 'Floor'
        }

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        qualifier['Output'] = OutputStates[match.group(2).decode()]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('AudioPath', value, qualifier)

    def SetDelegateSpeakersMax(self, value, qualifier):

        if 1 <= int(value) <= 8:
            DelegateSpeakersMaxCmdString = 'max_speakers {0}\r'.format(value)
            self.__SetHelper('DelegateSpeakersMax', DelegateSpeakersMaxCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDelegateSpeakersMax')

    def __MatchDelegateSpeakersMax(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DelegateSpeakersMax', value, None)

    def SetDelegateMicrophonesOff(self, value, qualifier):

        DelegateMicrophonesOffCmdString = 'mic_all_delegates_off\r'
        self.__SetHelper('DelegateMicrophonesOff', DelegateMicrophonesOffCmdString, value, qualifier)

    def SetInterruptMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        InterruptModeCmdString = 'mic_interrupt {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('InterruptMode', InterruptModeCmdString, value, qualifier)

    def __MatchInterruptMode(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InterruptMode', value, None)

    def SetLineInputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -41,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LineInputLevelCmdString = 'line_input_level_1 {0}\r'.format(value)
            self.__SetHelper('LineInputLevel', LineInputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInputLevel')

    def __MatchLineInputLevel(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LineInputLevel', value, None)

    def SetLineOutputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -41,
            'Max': 0
        }

        output = qualifier['Output']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and output in ['A', 'B', 'C', 'D']:
            LineOutputLevelCmdString = 'line_output_volume {0} {1}\r'.format(output, value)
            self.__SetHelper('LineOutputLevel', LineOutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineOutputLevel')

    def __MatchLineOutputLevel(self, match, tag):

        qualifier = {}
        qualifier['Output'] = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('LineOutputLevel', value, qualifier)

    def SetLoudspeakerLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -41,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LoudspeakerLevelCmdString = 'loudspeaker_volume {0}\r'.format(value)
            self.__SetHelper('LoudspeakerLevel', LoudspeakerLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoudspeakerLevel')

    def __MatchLoudspeakerLevel(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LoudspeakerLevel', value, None)

    def SetMicrophoneControl(self, value, qualifier):

        SeatConstraints = {
            'Min': 1,
            'Max': 65535
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        seat = qualifier['Seat']
        if SeatConstraints['Min'] <= seat <= SeatConstraints['Max']:
            MicrophoneControlCmdString = 'mic_{0} {1}\r'.format(ValueStateValues[value], qualifier['Seat'])
            self.__SetHelper('MicrophoneControl', MicrophoneControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneControl')

    def __MatchMicrophoneControl(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        qualifier = {}
        qualifier['Seat'] = int(match.group(2).decode())
        value = ValueStateValues[match.group(1).decode()]
        if value == 'On':
            self.WriteStatus('AllMicrophonesOffStatus', 'Disable', None)
        self.WriteStatus('MicrophoneControl', value, qualifier)

    def SetOperationMode(self, value, qualifier):

        ValueStateValues = {
            'Automatic': 'auto',
            'FIFO': 'fifo',
            'Manual': 'manual',
            'Voice Active': 'vox'
        }

        OperationModeCmdString = 'mic_mode {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('OperationMode', OperationModeCmdString, value, qualifier)

    def __MatchOperationMode(self, match, tag):

        ValueStateValues = {
            'auto': 'Automatic',
            'fifo': 'FIFO',
            'manual': 'Manual',
            'vox': 'Voice Active'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OperationMode', value, None)

    def SetRequestListClear(self, value, qualifier):

        RequestListClearCmdString = 'mic_all_requests_off\r'
        self.__SetHelper('RequestListClear', RequestListClearCmdString, value, qualifier)

    def SetRequestListControl(self, value, qualifier):

        SeatConstraints = {
            'Min': 1,
            'Max': 65535
        }

        ValueStateValues = {
            'Insert': 'on',
            'Remove': 'off'
        }

        seat = qualifier['Seat']
        if SeatConstraints['Min'] <= seat <= SeatConstraints['Max']:
            RequestListControlCmdString = 'mic_request_{0} {1}\r'.format(ValueStateValues[value], qualifier['Seat'])
            self.__SetHelper('RequestListControl', RequestListControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRequestListControl')

    def SetRequestListMax(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 250
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            RequestListMaxCmdString = 'max_requests {0}\r'.format(value)
            self.__SetHelper('RequestListMax', RequestListMaxCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRequestListMax')

    def __MatchRequestListMax(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('RequestListMax', value, None)

    def SetRequestListNext(self, value, qualifier):

        RequestListNextCmdString = 'mic_next_on\r'
        self.__SetHelper('RequestListNext', RequestListNextCmdString, value, qualifier)

    def __MatchRequestListStatus(self, match, tag):

        ValueStateValues = {
            'on': 'Requested',
            'off': 'Not Requested',
        }

        qualifier = {}
        qualifier['Seat'] = int(match.group(2).decode())
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RequestListStatus', value, qualifier)

    def UpdateStatus(self, value, qualifier):

        self.UpdateAudio(None, None)
        self.UpdateMics(None, None)

    def SetTotalSpeakersMax(self, value, qualifier):

        if 1 <= int(value) <= 8:
            TotalSpeakersMaxCmdString = 'max_total_speakers {0}\r'.format(value)
            self.__SetHelper('TotalSpeakersMax', TotalSpeakersMaxCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTotalSpeakersMax')

    def __MatchTotalSpeakersMax(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TotalSpeakersMax', value, None)

    def UpdateMics(self, value, qualifier):

        self.__UpdateHelper('Status', 'mic_status\r', value, qualifier)

    def UpdateAudio(self, value, qualifier):

        self.__UpdateHelper('Status', 'audio_status\r', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if command == 'MicrophoneListRefresh':
            res = self.SendAndWait(commandstring, 10, deliTag=b'mic_status_done\r')
            if not res:
                self.Error(['MicrophoneListRefresh: Invalid/unexpected response'])
                res = ''
            else:
                res = res.decode()
            return res
        else:
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

    def __MatchError(self, match, tag):
        self.counter = 0

        self.Error(['Error: ' + match.group(1).decode().capitalize()])

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()


################################################################
# BEGIN DIRECTORY CODE
################################################################

def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_driver()
        return res
    return wrapper

class Directory:
    """Handles the logic of a directory scrolling up/down and writing to the correct status labels
    3.1
    """

    def __init__(self, display_count, filler=None):

        # Number of items to show
        self._display_count = int(display_count)

        # name of the qualifier specifying the entry position
        self.qualifier_name = 'Position'

        # type of the 'Position' qualifier in Driver Studio. Either Enum or Number
        self._qualifier_type = 'Enum'

        self.entry_list = []

        self._start_index = 0

        # flag to specify if write_to_driver should be called automatically
        self.auto_update = True

        # This is the object to be used to fill out displayed positions if the list
        # runs out of elements to display. Also returned if invalid position is
        # accessed. Default is None.
        self.filler = filler

        # Function for grabbing the entry. Can be overwritten if entry is something other
        # than just a string. Ex: a dictionary: return entry['Name'] instead of just return entry
        self.entry_function = lambda entry: entry

    @property
    def display_count(self):
        return self._display_count

    @property
    def qualifier_type(self):
        return self._qualifier_type

    @qualifier_type.setter
    def qualifier_type(self, value):
        if value in ('Enum', 'Number'):
            self._qualifier_type = value

    def write_to_driver(self):
        """Write to driver status.
        Assumes each "entry" in the entry list is a string. If it's something else (ex: dictionary),
        self.entry_function must be overwritten with a new function that returns the correct string
        """
        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Number':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            self.write_status_function('MicrophoneList', self.entry_function(entry[0]), {self.qualifier_name: position_value})

    def write_status_function(self, cmdName, value, qualifier):
        pass

    @UseAutoUpdate
    def add_entry(self, entry):
        if isinstance(entry, list):
            self.entry_list.extend(entry)
        else:
            self.entry_list.append(entry)

    @UseAutoUpdate
    def reset(self, newEntries=None):
        if isinstance(newEntries, list):
            self.entry_list.clear()
            self.entry_list.extend(newEntries)
        else:
            self.entry_list.clear()
        self._start_index = 0

    @UseAutoUpdate
    def remove_entry(self, display_position):
        """Removes the entry in the entry list
        The index of the entry to retrieve is offset by the _start_index

        display_position is assumed to not be 0-based.
        """

        if self.__display_position_check(display_position):
            try:
                return self.entry_list.pop(self._start_index + display_position - 1)
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_entry(self, display_position):
        """Return the value of the entry
        The index of the entry to retrieve is offset by the _start_index

        display_position (int) is assumed to not be 0-based.
        """

        # Make sure the position is valid
        if self.__display_position_check(display_position):
            try:
                return self.entry_list[self._start_index + display_position - 1]
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_displayed_entries(self):
        """Returns an iterator of only the displayed entries.
        Each returned value is a tuple (entry object, item's position in the list)
        """
        index = self._start_index
        while index <= self._start_index + self._display_count - 1:
            if index >= len(self.entry_list):
                yield self.filler, index + 1
            else:
                yield self.entry_list[index], index + 1

            index += 1

    def __display_position_check(self, position):
        """Checks to make sure the given position is a valid position to display"""
        return 0 < position <= self._display_count

    @UseAutoUpdate
    def scroll_up(self, step=1):
        # Make sure new start index is greater than 0
        if self._start_index - step >= 0:
            self._start_index -= step
        else:
            self._start_index = 0

    @UseAutoUpdate
    def scroll_down(self, step=1):
        # Make sure new start index doesn't go past the length of entry list
        if self._start_index + step < len(self.entry_list):
            self._start_index += step
        else:
            self._start_index = len(self.entry_list) - 1  # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1