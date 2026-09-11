# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import time
import re
from collections import defaultdict
import copy

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
        self._NumberofCallHistoryResults = 5
        self._NumberofPhonebookResults = 5
        self._NumberofListResults = 5
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CallerID': {'Parameters': ['Control ID'], 'Status': {}},
            'CallerName': {'Parameters': ['Control ID'], 'Status': {}},
            'CallHistoryNavigation': {'Parameters': ['Control ID'], 'Status': {}},
            'CallHistoryResultSet' : {'Parameters': ['Dial String ID', 'Control ID', 'Position'], 'Status': {}},
            'CallHistoryResults': {'Parameters': ['Control ID', 'Position'], 'Status': {}},
            'CallHistoryUpdate': {'Parameters': ['Control ID'], 'Status': {}},
            'CallStatus': {'Parameters': ['Control ID'], 'Status': {}},
            'ControlSetString': {'Parameters': ['Control ID', 'Control String'], 'Status': {}},
            'ControlSetValue': {'Parameters': ['Control ID', 'Control Value'], 'Status': {}},
            'ControlTrigger': {'Parameters': ['Control ID'], 'Status': {}},
            'DesignName': {'Status': {}},
            'DialString': {'Parameters': ['Control ID', 'Control Value'], 'Status': {}},
            'FocusControl': {'Parameters': ['Control ID'], 'Status': {}},
            'FocusMode': {'Parameters': ['Control ID'], 'Status': {}},
            'FocusSpeed': {'Parameters': ['Control ID'], 'Status': {}},
            'Function': {'Parameters': ['Control ID'], 'Status': {}},
            'Gain': {'Parameters': ['Control ID'], 'Status': {}},
            'GainExpansion': {'Parameters': ['Control ID'], 'Status': {}},
            'GetStatusString': {'Parameters': ['Control ID'], 'Status': {}},
            'GetStatusValue': {'Parameters': ['Control ID'], 'Status': {}},
            'LevelMeter': {'Parameters': ['Control ID'], 'Status': {}},
            'ListNavigation': {'Parameters': ['Control ID'], 'Status': {}},
            'ListResultSet': {'Parameters': ['Control ID', 'Position'], 'Status': {}},
            'ListResults': {'Parameters': ['Control ID', 'Position'], 'Status': {}},
            'ListUpdate': {'Parameters': ['Control ID'], 'Status': {}},
            'Mute': {'Parameters': ['Control ID'], 'Status': {}},
            'PhonebookControl': {'Parameters': ['Control ID', 'Phonebook ID'], 'Status': {}},
            'PhonebookListUpdate': {'Parameters': ['Control ID'], 'Status': {}},
            'PhonebookNavigation': {'Parameters': ['Control ID'], 'Status': {}},
            'PhonebookResults': {'Parameters': ['Control ID', 'Position'], 'Status': {}},
            'PhonebookResultSet': {'Parameters': ['Control ID', 'Position'], 'Status': {}},
            'PhonebookSearch': {'Parameters': ['Control ID'], 'Status': {}},
            'PhonebookUpdate': {'Parameters': ['Control ID'], 'Status': {}},
            'PTZControl': {'Parameters': ['Control ID'], 'Status': {}},
            'PTZSpeed': {'Parameters': ['Control ID'], 'Status': {}},
            'Router': {'Parameters': ['Control ID'], 'Status': {}},
            'SnapshotLoad': {'Parameters': ['Load Time', 'Bank'], 'Status': {}},
            'SnapshotSave': {'Parameters': ['Bank'], 'Status': {}},
        }

        self.login_required = False
        self.login_counter = 0
        self.match_strings = set()
        self.lastChangeGroupCreate = 0

        if self.Unidirectional == 'False':
            if self.ConnectionType == 'Ethernet':
                self.AddMatchString(re.compile(b'login NAME PIN'), self.__MatchLogin, True)
                self.AddMatchString(re.compile(b'login_required'), self.__MatchLogin, True)
                self.AddMatchString(re.compile(b'login_failed'), self.__MatchLogin, False)

            self.AddMatchString(re.compile(b'sr "(.*?)" ".*?" [01] [01]\r\n'), self.__MatchDesignName, None)
            self.AddMatchString(re.compile(b'bad_change_group_handle 1\r\n'), self.__MatchChangeGroupCreate, None)

            self.AddMatchString(re.compile(b'bad_(.*?)\r\n'), self.__MatchError, None)
            

        self.call_history_scroller = defaultdict(lambda: Scroller([], self._NumberofCallHistoryResults, end='*** End of List ***'))
        self.list_scroller = defaultdict(lambda: Scroller([], self._NumberofListResults, end='*** End of List ***'))
        self.phonebook_scroller = defaultdict(lambda: Scroller([], self._NumberofPhonebookResults, end='*** End of List ***'))
        self.call_history_regex = re.compile('"\{\\\\"Text\\\\":\\\\"(.+?)\\\\",.+?\}"')

        self.cmvv_regex = re.compile('cmvv ".*?" \d+ \d+ (.*?)\d+ \d+\r\n')
        self.cmvv_entry_regex = re.compile('"(.*?)"')

    @property
    def NumberofCallHistoryResults(self):
        return self._NumberofCallHistoryResults

    @NumberofCallHistoryResults.setter
    def NumberofCallHistoryResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofCallHistoryResults = int(value)
            self.call_history_scroller = defaultdict(lambda: Scroller([], self._NumberofCallHistoryResults, end='*** End of List ***'))

    @property
    def NumberofPhonebookResults(self):
        return self._NumberofPhonebookResults

    @NumberofPhonebookResults.setter
    def NumberofPhonebookResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofPhonebookResults = int(value)
            self.phonebook_scroller = defaultdict(lambda: Scroller([], self._NumberofPhonebookResults, end='*** End of List ***'))

    @property
    def NumberofListResults(self):
        return self._NumberofListResults

    @NumberofListResults.setter
    def NumberofListResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofListResults = value
            self.list_scroller = defaultdict(lambda: Scroller([], self._NumberofListResults, end='*** End of List ***'))

    def __MatchLogin(self, match, tag):
        if tag:
            self.login_required = True
            self.SetPassword(None, None)
        else:
            self.login_counter += 1
            self.Error(['Login failed. Please verify username and pin.'])

    def SetPassword(self, value, qualifier):
        if self.login_required and not (self.deviceUsername and self.devicePassword):
            self.login_counter = 5
            self.Error(['Login required. Please supply username and pin.'])
        elif self.login_counter < 5 and self.deviceUsername and self.devicePassword:
            self.Send('login {} {}\n'.format(self.deviceUsername, self.devicePassword))

    def __MatchChangeGroupCreate(self, match, tag):

        # This should not be sent more than once every second
        ctime = time.monotonic()
        if ctime - self.lastChangeGroupCreate > 1:
            self.lastChangeGroupCreate = ctime
            self.Send('cgc 1\n')
            self.Send('cgsna 1 100\n')
        else:
            self.Discard('Device Is Busy')

    def match_string_helper(self, match_string, match_function, tag):
        if match_string not in self.match_strings and match_function:
            self.AddMatchString(re.compile(match_string.encode()), match_function, tag)
            self.match_strings.add(match_string)

    def CallHistoryStatusRefresh(self, control_id):
        for position, entry in enumerate(self.call_history_scroller[control_id], 1):
            self.WriteStatus('CallHistoryResults', entry, {'Control ID': control_id, 'Position': str(position)})

    def ListStatusRefresh(self, control_id):
        for position, entry in enumerate(self.list_scroller[control_id], 1):
            self.WriteStatus('ListResults', entry.lstrip('<').rstrip('>'), {'Control ID': control_id, 'Position': str(position)})

    def PhonebookStatusRefresh(self, control_id):
        for position, entry in enumerate(self.phonebook_scroller[control_id], 1):
            self.WriteStatus('PhonebookResults', entry, {'Control ID': control_id, 'Position': str(position)})

    def UpdateCallerID(self, value, qualifier):

        self.UpdateCallStatus(value, {'Control ID': qualifier['Control ID']})

    def UpdateCallerName(self, value, qualifier):

        self.UpdateCallStatus(value, {'Control ID': qualifier['Control ID']})

    def SetCallHistoryNavigation(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id and control_id in self.call_history_scroller:
            call_history = self.call_history_scroller[control_id]

            ValueStateValues = {
                'Up': call_history.previous,
                'Down': call_history.next,
                'Page Up': call_history.previous_page,
                'Page Down': call_history.next_page
            }

            if value in ValueStateValues and call_history.current_size > 0:
                ValueStateValues[value]()
                self.CallHistoryStatusRefresh(control_id)
            else:
                self.Discard('Invalid Command for SetCallHistoryNavigation')
        else:
            self.Discard('Invalid Command for SetCallHistoryNavigation')

    def SetCallHistoryResultSet(self, value, qualifier):

        dial_string_id = qualifier['Dial String ID']
        control_id = qualifier['Control ID']
        position = int(qualifier['Position'])

        if dial_string_id and control_id and control_id in self.call_history_scroller and 1 <= position <= self.call_history_scroller[control_id].window <= 10:
            call_history = self.call_history_scroller[control_id]
            if call_history.offset + position <= call_history.current_size:
                CallHistoryResultSetCmdString = 'css "{}" "{}"\n'.format(dial_string_id, call_history[position - 1])
                self.__SetHelper('CallHistoryResultSet', CallHistoryResultSetCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCallHistoryResultSet')
        else:
            self.Discard('Invalid Command for SetCallHistoryResultSet')

    def SetCallHistoryUpdate(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.call_history_scroller[control_id].clear()

            self.WriteStatus('CallHistoryResults', '*** Loading ***', {'Control ID': control_id, 'Position': '1'})
            for position in range(2, int(self._NumberofCallHistoryResults) + 1):
                self.WriteStatus('CallHistoryResults', '...', {'Control ID': control_id, 'Position': str(position)})

            res = self.SendAndWait('cgm "{}"\n'.format(control_id), 1, deliTag='\n')
            if res:
                self.call_history_scroller[control_id].extend(self.call_history_regex.findall(res.decode()))
                self.CallHistoryStatusRefresh(control_id)
            else:
                self.WriteStatus('CallHistoryResults', '*** Not Available ***', {'Control ID': control_id, 'Position': '1'})
                for position in range(2, int(self._NumberofCallHistoryResults) + 1):
                    self.WriteStatus('CallHistoryResults', '', {'Control ID': control_id, 'Position': str(position)})
        else:
            self.Discard('Invalid Command for SetCallHistoryUpdate')

    def UpdateCallStatus(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" "(?:((.*?) - (.*?) \((.*?)\))|(.*?))".*?\r\n'.format(re.escape(control_id)), self.__MatchCallStatus, None)

            CallStatusCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCallStatus')

    def __MatchCallStatus(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        if match.group(6):
            self.WriteStatus('CallStatus', match.group(6).decode(), qualifier)
            self.WriteStatus('CallerID', 'N/A', qualifier)
            self.WriteStatus('CallerName', 'N/A', qualifier)
        else:
            self.WriteStatus('CallerID', match.group(5).decode(), qualifier)
            self.WriteStatus('CallerName', match.group(4).decode(), qualifier)
            self.WriteStatus('CallStatus', match.group(3).decode(), qualifier)

    def SetControlSetString(self, value, qualifier):

        control_id = qualifier['Control ID']
        control_string = qualifier['Control String']

        if control_id:
            ControlSetStringCmdString = 'css "{}" "{}"\n'.format(control_id, control_string)
            self.__SetHelper('ControlSetString', ControlSetStringCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetControlSetString')

    def SetControlSetValue(self, value, qualifier):

        control_id = qualifier['Control ID']
        control_value = qualifier['Control Value']

        if control_id and 0 <= control_value <= 100:
            ControlSetValueCmdString = 'csv "{}" {}\n'.format(control_id, control_value)
            self.__SetHelper('ControlSetValue', ControlSetValueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetControlSetValue')

    def SetControlTrigger(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            ControlTriggerCmdString = 'ct "{}"\n'.format(control_id)
            self.__SetHelper('ControlTrigger', ControlTriggerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetControlTrigger')

    def UpdateDesignName(self, value, qualifier):

        DesignNameCmdString = 'sg\n'
        self.__UpdateHelper('DesignName', DesignNameCmdString, value, qualifier)

    def __MatchDesignName(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DesignName', value, None)

    def SetDialString(self, value, qualifier):

        control_id = qualifier['Control ID']
        control_value = qualifier['Control Value']

        ValueStateValues = [
            '0',
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            '*',
            '#',
            'Delete',
            'Clear'
        ]

        if control_id and 1 <= control_value <= 100 and value in ValueStateValues:
            DialStringCmdString = 'csv "{}" {}\n'.format(control_id, control_value)
            self.__SetHelper('DialString', DialStringCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetFocusControl(self, value, qualifier):

        control_id = qualifier['Control ID']

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        if control_id and value in ValueStateValues:
            FocusControlCmdString = 'csv "{}" {}\n'.format(control_id, ValueStateValues[value])
            self.__SetHelper('FocusControl', FocusControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusControl')

    def UpdateFocusMode(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" "(true|false)".*?\r\n'.format(re.escape(control_id)), self.__MatchFocusMode, None)

            FocusModeCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFocusMode')

    def __MatchFocusMode(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        ValueStateValues = {
            'true': 'Auto',
            'false': 'Manual'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FocusMode', value, qualifier)

    def SetFocusSpeed(self, value, qualifier):

        control_id = qualifier['Control ID']
        value = round(value, 3)

        if control_id and 0.001 <= value <= 1:
            FocusSpeedCmdString = 'csv "{}" {}\n'.format(control_id, value)
            self.match_string_helper('cv "({})" "(\d?\.\d+)".*?\r\n'.format(re.escape(control_id)), self.__MatchFocusSpeed, None)

            self.__SetHelper('FocusSpeed', FocusSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusSpeed')

    def UpdateFocusSpeed(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" "(\d?\.\d+)".*?\r\n'.format(re.escape(control_id)), self.__MatchFocusSpeed, None)

            FocusSpeedCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('FocusSpeed', FocusSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFocusSpeed')

    def __MatchFocusSpeed(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        value = float(match.group(2).decode())
        if 0.001 <= value <= 1:
            self.WriteStatus('FocusSpeed', value, qualifier)

    def SetFunction(self, value, qualifier):

        control_id = qualifier['Control ID']

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        if control_id and value in ValueStateValues:
            FunctionCmdString = 'csv "{}" {}\n'.format(control_id, ValueStateValues[value])
            self.match_string_helper('cv "({})" "(enable|disable)d".*?\r\n'.format(re.escape(control_id)), self.__MatchFunction, None)

            self.__SetHelper('Function', FunctionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFunction')

    def UpdateFunction(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" "(enable|disable)d".*?\r\n'.format(re.escape(control_id)), self.__MatchFunction, None)

            FunctionCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('Function', FunctionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFunction')

    def __MatchFunction(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        value = match.group(2).decode().title()
        self.WriteStatus('Function', value, qualifier)

    def SetGain(self, value, qualifier):

        control_id = qualifier['Control ID']
        value = round(value, 1)

        if control_id and -100 <= value <= 20:
            GainCmdString = 'csv "{}" {}\n'.format(control_id, value)
            self.match_string_helper('cv "({})" "(.+?)dB".*?\r\n'.format(re.escape(control_id)), self.__MatchGain, None)

            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" "(.+?)dB".*?\r\n'.format(re.escape(control_id)), self.__MatchGain, None)

            GainCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGain')

    def __MatchGain(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        value = float(match.group(2).decode())
        if -100 <= value <= 20:
            self.WriteStatus('Gain', value, qualifier)

    def SetGainExpansion(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id and -100 <= value <= 83:
            GainExpansionCmdString = 'csv "{}" {}\n'.format(control_id, value)
            self.match_string_helper('cv "({})" "(.+?)dB".*?\r\n'.format(re.escape(control_id)), self.__MatchGainExpansion, None)

            self.__SetHelper('GainExpansion', GainExpansionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGainExpansion')

    def UpdateGainExpansion(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" "(.+?)dB".*?\r\n'.format(re.escape(control_id)), self.__MatchGainExpansion, None)

            GainExpansionCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('GainExpansion', GainExpansionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGainExpansion')

    def __MatchGainExpansion(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        value = float(match.group(2).decode())
        if -100 <= value <= 83:
            self.WriteStatus('GainExpansion', value, qualifier)

    def UpdateGetStatusString(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" "(.*?)".*?\r\n'.format(re.escape(control_id)), self.__MatchGetStatusString, None)

            GetStatusCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('GetStatusString', GetStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for GetStatusString')

    def __MatchGetStatusString(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        value = match.group(2).decode()
        self.WriteStatus('GetStatusString', value, qualifier)

    def UpdateGetStatusValue(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" ([01]).*?\r\n'.format(re.escape(control_id)), self.__MatchGetStatusValue, None)
            self.match_string_helper('cv "({})" ".*?" ([01]).*?\r\n'.format(re.escape(control_id)), self.__MatchGetStatusValue, None)

            GetStatusCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('GetStatusValue', GetStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGetStatusValue')

    def __MatchGetStatusValue(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('GetStatusValue', value, qualifier)

    def UpdateLevelMeter(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cvv "({})" 2 "(.+?)dB" ".+?dB".*?\r\n'.format(re.escape(control_id)), self.__MatchLevelMeter, None)

            LevelMeterCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('LevelMeter', LevelMeterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLevelMeter')

    def __MatchLevelMeter(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        value = float(match.group(2).decode())
        if -120 <= value <= 20:
            self.WriteStatus('LevelMeter', value, qualifier)

    def SetListNavigation(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id and control_id in self.list_scroller:
            list_ = self.list_scroller[control_id]
            
            ValueStateValues = {
                'Up':           list_.previous,
                'Down':         list_.next,
                'Page Up':      list_.previous_page,
                'Page Down':    list_.next_page
            }

            if value in ValueStateValues and list_.current_size > 0:
                ValueStateValues[value]()
                self.ListStatusRefresh(control_id)
            else:
                self.Discard('Invalid Command for SetListNavigation')
        else:
            self.Discard('Invalid Command for SetListNavigation')

    def SetListResultSet(self, value, qualifier):

        control_id = qualifier['Control ID']
        position = int(qualifier['Position'])

        if control_id and control_id in self.list_scroller and 1 <= position <= self.list_scroller[control_id].window <= 10:
            list_ = self.list_scroller[control_id]

            if list_.offset + position <= list_.current_size:
                ListResultSetCmdString = 'css "{}" "{}"\n'.format(control_id, list_[position - 1])
                self.__SetHelper('ListResultSet', ListResultSetCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetListResultSet')
        else:
            self.Discard('Invalid Command for SetListResultSet')

    def SetListUpdate(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.list_scroller[control_id].clear()

            self.WriteStatus('ListResults', '*** Loading ***', {'Control ID': control_id, 'Position': '1'})
            for position in range(2, int(self._NumberofListResults) + 1):
                self.WriteStatus('ListResults', '...', {'Control ID': control_id, 'Position': str(position)})

            res = self.SendAndWait('cgm "{}"\n'.format(control_id), 1, deliTag='\n')
            if res:
                match = self.cmvv_regex.match(res)
                if match:
                    self.list_scroller[control_id].extend(self.cmvv_entry_regex.findall(match.group(1)))

                self.ListStatusRefresh(control_id)
            else:
                self.WriteStatus('ListResults', '*** Not Available ***', {'Control ID': control_id, 'Position': '1'})
                for position in range(2, int(self._NumberofListResults) + 1):
                    self.WriteStatus('ListResults', '', {'Control ID': control_id, 'Position': str(position)})
        else:
            self.Discard('Invalid Command for SetListUpdate')

    def SetMute(self, value, qualifier):

        control_id = qualifier['Control ID']

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if control_id and value in ValueStateValues:
            MuteCmdString = 'csv "{}" {}\n'.format(control_id, ValueStateValues[value])
            self.match_string_helper('cv "({})" "(muted|unmuted)".*?\r\n'.format(re.escape(control_id)), self.__MatchMute, None)

            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" "(muted|unmuted)".*?\r\n'.format(re.escape(control_id)), self.__MatchMute, None)

            MuteCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        ValueStateValues = {
            'muted': 'On',
            'unmuted': 'Off'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Mute', value, qualifier)

    def SetPhonebookControl(self, value, qualifier):

        control_id = qualifier['Control ID']
        phonebook_id = qualifier['Phonebook ID']

        if control_id and phonebook_id:
            dial_string = self.ReadStatus('GetStatusString', {'Control ID': phonebook_id})
            if dial_string is not None:
                PhonebookControlCmdString = 'css "{}" "{}"\n'.format(control_id, dial_string)
                self.__SetHelper('PhonebookControl', PhonebookControlCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPhonebookControl')
        else:
            self.Discard('Invalid Command for SetPhonebookControl')

    def SetPhonebookListUpdate(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.phonebook_scroller[control_id].clear()

            self.WriteStatus('PhonebookResults', '*** Loading ***', {'Control ID': control_id, 'Position': '1'})
            for position in range(2, int(self._NumberofPhonebookResults) + 1):
                self.WriteStatus('PhonebookResults', '...', {'Control ID': control_id, 'Position': str(position)})

            res = self.SendAndWait('cgm "{}"\n'.format(control_id), 1, deliTag='\n')
            if res:
                self.phonebook_scroller[control_id].extend(self.call_history_regex.findall(res.decode()))
                self.PhonebookStatusRefresh(control_id)
            else:
                self.WriteStatus('PhonebookResults', '*** Not Available ***', {'Control ID': control_id, 'Position': '1'})
                for position in range(2, int(self._NumberofPhonebookResults) + 1):
                    self.WriteStatus('PhonebookResults', '', {'Control ID': control_id, 'Position': str(position)})
        else:
            self.Discard('Invalid Command for SetPhonebookListUpdate')

    def SetPhonebookNavigation(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id and control_id in self.phonebook_scroller:
            phonebook = self.phonebook_scroller[control_id]

            ValueStateValues = {
                'Up': phonebook.previous,
                'Down': phonebook.next,
                'Page Up': phonebook.previous_page,
                'Page Down': phonebook.next_page
            }

            if value in ValueStateValues and phonebook.current_size > 0:
                ValueStateValues[value]()
                self.PhonebookStatusRefresh(control_id)
            else:
                self.Discard('Invalid Command for SetPhonebookNavigation')
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookResultSet(self, value, qualifier):

        control_id = qualifier['Control ID']
        position = int(qualifier['Position'])

        if control_id and control_id in self.phonebook_scroller and 1 <= position <= self.phonebook_scroller[control_id].window <= 10:
            phonebook = self.phonebook_scroller[control_id]

            if phonebook.offset + position <= phonebook.current_size:

                PhonebookResultSetCmdString = 'css "{}" "{}"\n'.format(control_id, phonebook[position - 1])
                self.__SetHelper('PhonebookResultSet', PhonebookResultSetCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPhonebookResultSet')
        else:
            self.Discard('Invalid Command for SetPhonebookResultSet')

    def SetPhonebookSearch(self, value, qualifier):

        control_id = qualifier['Control ID']
        string = qualifier['Contact']
        if string is None:
            string = ''

        if control_id:
            PhonebookSearchCmdString = 'css "{}" "{}"\n'.format(control_id, string)
            self.__SetHelper('PhonebookSearch', PhonebookSearchCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookSearch')

    def SetPhonebookUpdate(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.phonebook_scroller[control_id].clear()

            self.WriteStatus('PhonebookResults', '*** Loading ***', {'Control ID': control_id, 'Position': '1'})
            for position in range(2, int(self._NumberofPhonebookResults) + 1):
                self.WriteStatus('PhonebookResults', '...', {'Control ID': control_id, 'Position': str(position)})

            res = self.SendAndWait('cgm "{}"\n'.format(control_id), 1, deliTag='\n')
            if res:
                match = self.cmvv_regex.match(res)
                if match:
                    self.phonebook_scroller[control_id].extend(self.cmvv_entry_regex.findall(match.group(1)))

                self.PhonebookStatusRefresh(control_id)
            else:
                self.WriteStatus('PhonebookResults', '*** Not Available ***', {'Control ID': control_id, 'Position': '1'})
                for position in range(2, int(self._NumberofPhonebookResults) + 1):
                    self.WriteStatus('PhonebookResults', '', {'Control ID': control_id, 'Position': str(position)})
        else:
            self.Discard('Invalid Command for SetPhonebookUpdate')

    def SetPTZControl(self, value, qualifier):

        control_id = qualifier['Control ID']

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        if control_id and value in ValueStateValues:
            PTZControlCmdString = 'csv "{}" {}\n'.format(control_id, ValueStateValues[value])
            self.__SetHelper('PTZControl', PTZControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPTZControl')

    def SetPTZSpeed(self, value, qualifier):

        control_id = qualifier['Control ID']
        value = round(value, 3)

        if control_id and 0.001 <= value <= 1:
            PTZSpeedCmdString = 'csv "{}" {}\n'.format(control_id, value)
            self.match_string_helper('cv "({})" "(\d?\.\d+)".*?\r\n'.format(re.escape(control_id)), self.__MatchPTZSpeed, None)

            self.__SetHelper('PTZSpeed', PTZSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPTZSpeed')

    def UpdatePTZSpeed(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" "(\d?\.\d+)".*?\r\n'.format(re.escape(control_id)), self.__MatchPTZSpeed, None)

            PTZSpeedCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('PTZSpeed', PTZSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePTZSpeed')

    def __MatchPTZSpeed(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        value = float(match.group(2).decode())
        if 0.001 <= value <= 1:
            self.WriteStatus('PTZSpeed', value, qualifier)

    def SetRouter(self, value, qualifier):

        control_id = qualifier['Control ID']

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        if control_id and value in ValueStateValues:
            RouterCmdString = 'csv "{}" {}\n'.format(control_id, ValueStateValues[value])
            self.match_string_helper('cv "({})" ".*?" ([01]).*?\r\n'.format(re.escape(control_id)), self.__MatchRouter, None)

            self.__SetHelper('Router', RouterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRouter')

    def UpdateRouter(self, value, qualifier):

        control_id = qualifier['Control ID']

        if control_id:
            self.match_string_helper('cv "({})" ".*?" ([01]).*?\r\n'.format(re.escape(control_id)), self.__MatchRouter, None)

            RouterCmdString = 'cga 1 "{}"\n'.format(control_id)
            self.__UpdateHelper('Router', RouterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRouter')

    def __MatchRouter(self, match, tag):

        qualifier = {
            'Control ID': match.group(1).decode()
        }

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Router', value, qualifier)

    def SetSnapshotLoad(self, value, qualifier):

        load_time = qualifier['Load Time']
        bank = qualifier['Bank']

        if 0 <= load_time <= 60 and bank and 1 <= int(value) <= 24:
            SnapshotLoadCmdString = 'ssl "{}" {} {}\n'.format(bank, value, load_time)
            self.__SetHelper('SnapshotLoad', SnapshotLoadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSnapshotLoad')

    def SetSnapshotSave(self, value, qualifier):

        bank = qualifier['Bank']

        if bank and 1 <= int(value) <= 24:
            SnapshotSaveCmdString = 'sss "{}" {}\n'.format(bank, value)
            self.__SetHelper('SnapshotSave', SnapshotSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSnapshotSave')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.login_counter < 5:
            self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.login_counter < 5:
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
        else:
            self.Discard('Inappropriate Command ' + command)

            if command == 'DesignName':
                if self.login_required and not (self.deviceUsername and self.devicePassword):
                    self.Error(['Login required. Please supply username and pin.'])
                else:
                    self.Error(['Login failed. Please verify username and pin.'])

    def __MatchError(self, match, tag):

        self.counter = 0

        self.Error(['An error occurred: {}.'.format(match.group(0).decode(encoding='iso-8859-1').strip())])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        if self.ConnectionType == 'Ethernet':
            self.SetPassword(None, None)

        self.Send('cgc 1\n')
        self.Send('cgsna 1 100\n')

    def OnDisconnected(self):
        self.lastChangeGroupCreate = 0
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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

        tempList = copy.copy(self.__matchStringDict)
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in tempList.items():
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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

class Scroller:
    def __init__(self, items, window, mark_end=True, end='', fill=''):

        self.__all_items = list(items)
        self.__filtered_items = []
        self.__filter_key = None
        self.__current_items = self.__all_items
        self.__offset = 0
        self.__window = max(1, window)
        self.__mark_end = mark_end
        self.__end = end
        self.__fill = fill

    def __getitem__(self, index):

        return self.view()[index]

    def __iter__(self):

        stop = min(self.offset + self.window, self.current_size)

        for item in self.__current_items[self.offset:stop]:
            yield item

        fill_count = self.offset + self.window - self.current_size
        if fill_count > 0:
            if self.mark_end:
                yield self.end

            for i in range(fill_count - int(self.mark_end)):
                yield self.fill

    def __str__(self):

        s = 'Offset {}/{}, viewing ({{}}) {}/{} items ({})'.format(self.offset, self.max_offset, self.window, self.current_size, self.view())

        if not self.filtered:
            return s.format('all')
        else:
            return s.format('filtered')

    @property
    def current_items(self):

        return self.__current_items.copy()

    @property
    def all_items(self):

        return self.__all_items.copy()

    @property
    def filtered_items(self):

        return self.__filtered_items.copy()

    @property
    def current_size(self):

        return len(self.__current_items)

    @property
    def all_size(self):

        return len(self.__all_items)

    @property
    def filtered_size(self):

        return len(self.__filtered_items)

    @property
    def offset(self):

        self.__offset = min(self.__offset, self.max_offset)
        return self.__offset

    @offset.setter
    def offset(self, offset):

        if 0 <= offset <= self.max_offset:
            self.__offset = offset
            return

        raise Exception('offset value \'{}\' is out of range [0, {}]'.format(offset, self.max_offset))

    @property
    def window(self):

        return self.__window

    @property
    def mark_end(self):

        return self.__mark_end

    @property
    def end(self):

        return self.__end

    @property
    def fill(self):

        return self.__fill

    @property
    def filtered(self):

        return self.__filter_key is not None

    @property
    def max_offset(self):

        return max(0, self.current_size - self.window + int(self.mark_end))

    def view(self):

        return list(self.__iter__())

    def format(self, key):

        items = []

        stop = min(self.offset + self.window, self.current_size)

        for item in self.__current_items[self.offset:stop]:
            items.append(key(item))

        fill_count = self.offset + self.window - self.current_size
        if fill_count > 0:
            if self.mark_end:
                items.append(self.end)

            for i in range(fill_count - int(self.mark_end)):
                items.append(self.fill)

        return items

    def clear(self):

        self.__all_items.clear()

        self.__filtered_items.clear()
        self.__filter_key = None

        self.__current_items = self.__all_items

        self.offset = 0

    def overwrite(self, items):

        self.clear()
        self.extend(items)

    def append(self, item):

        self.__all_items.append(item)

        if self.__filter_key is not None and self.__filter_key(item):
            self.__filtered_items.append(item)

    def extend(self, items):

        self.__all_items.extend(items)

        if self.__filter_key is not None:
            for item in items:
                if self.__filter_key(item):
                    self.__filtered_items.append(item)

    def filter(self, key):

        self.__filter_key = key

        if self.__filter_key is not None:
            self.__filtered_items = [item for item in self.__all_items if self.__filter_key(item)]
            self.__current_items = self.__filtered_items
        else:
            self.__filtered_items.clear()
            self.__current_items = self.__all_items

        self.offset = 0

    def scroll(self, steps):

        self.offset = max(0, min(self.offset + steps, self.max_offset))

    def previous(self):

        self.scroll(-1)

    def next(self):

        self.scroll(1)

    def previous_page(self):

        self.scroll(-self.window)

    def next_page(self):

        self.scroll(self.window)

    def first(self):

        self.offset = 0

    def last(self):

        self.offset = self.max_offset