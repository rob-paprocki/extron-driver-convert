from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import time
import json
import struct
from base64 import encodebytes as base64encode
import random
import array

FIN = 0x80
OPCODE = 0x0f
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f

STREAM = 0x0
TEXT = 0x1
BINARY = 0x2
CLOSE = 0x8
PING = 0x9
PONG = 0xA

def _mask(_m, _d):
    for i in range(len(_d)):
        _d[i] ^= _m[i % 4]
    return _d.tostring()


class DeviceClass:

    def __init__(self, ipAddress):

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
        self.NumberofMeetingParticipants = 5
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CameraMute': { 'Status': {}},
            'MeetingBeginTime': { 'Status': {}},
            'MeetingControl': { 'Status': {}},
            'MeetingCreatorName': { 'Status': {}},
            'MeetingEndTime': { 'Status': {}},
            'MeetingIDStatus': { 'Status': {}},
            'MeetingListBeginTimeResults': {'Parameters': ['Position'], 'Status': {}},
            'MeetingListCreatorNameResults': {'Parameters': ['Position'], 'Status': {}},
            'MeetingListEndTimeResults': {'Parameters': ['Position'], 'Status': {}},
            'MeetingListIDResults': {'Parameters': ['Position'], 'Status': {}},
            'MeetingListResultSet': { 'Status': {}},
            'MeetingListTitleResults': {'Parameters': ['Position'], 'Status': {}},
            'MeetingListTypeResults': {'Parameters': ['Position'], 'Status': {}},
            'MeetingListUpdate': { 'Status': {}},
            'MeetingParticipantsAudioMute': {'Parameters': ['Position'], 'Status': {}},
            'MeetingParticipantsAudioMuteAll': { 'Status': {}},
            'MeetingParticipantsNameResults': {'Parameters': ['Position'], 'Status': {}},
            'MeetingParticipantsNavigation': { 'Status': {}},
            'MeetingParticipantsRemove': {'Parameters': ['Position'], 'Status': {}},
            'MeetingParticipantsUpdate': { 'Status': {}},
            'MeetingParticipantsVideoMute': {'Parameters': ['Position'], 'Status': {}},
            'MeetingPasswordStatus': { 'Status': {}},
            'MeetingStatus': { 'Status': {}},
            'MeetingTitle': { 'Status': {}},
            'MeetingType': { 'Status': {}},
            'MicrophoneMute': { 'Status': {}},
            'Share': {'Parameters': ['Share Type', 'Share Voice', 'Fluency First', 'Select Index', 'Device ID'], 'Status': {}},
            'ShareCastCode': { 'Status': {}},
            'ShareGuide': { 'Status': {}},
            'ShareWindow': {'Parameters': ['Share Voice', 'Fluency First', 'Select Index'], 'Status': {}},
            'SpeakerVolume': { 'Status': {}},
        }

        self.ipAddress = ipAddress
        self.uri = '/'
        self._handshake = (
            "GET %(uri)s HTTP/1.1\r\n"
            "Host: %(ipAddress)s\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: %(randomstring)s\r\n"
            "Sec-WebSocket-Version: 13\r\n"
	        "Sec-WebSocket-Protocol: %(encryptedPassword)s\r\n"
            "\r\n"
        )

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{"jsonrpc": "2\.0", "method": "Call\/(?:Device|Meeting|MeetingControl|Share)", "id": "(Camera Mute|Meeting Control|Microphone Mute|Meeting Participants Audio Mute|Meeting Participants Audio Mute All|Meeting Participants Remove|Meeting Participants Video Mute|Share|Share Guide|Share Window)", "result": {.*?}}'), self.__MatchControlCommandAck, None)
            self.AddMatchString(re.compile(b'{"jsonrpc": "2\.0", "method": "Query", "id": "Camera Mute", "result": {.*?}}}}'), self.__MatchCameraMute, None)
            self.AddMatchString(re.compile(b'{"jsonrpc": "2\.0", "method": "Query", "id": "Meeting List", "result": {.*?}}}'), self.__MatchMeetingList, None)
            self.AddMatchString(re.compile(b'{"jsonrpc": "2\.0", "method": "Query", "id": "Meeting Status", "result": {.*?}}}}'), self.__MatchMeetingStatus, None)
            self.AddMatchString(re.compile(b'{"jsonrpc": "2\.0", "method": "Query", "id": "Meeting Participants Update", "result": {.*?}}}}'), self.__MatchMeetingParticipantsUpdate, None)
            self.AddMatchString(re.compile(b'{"jsonrpc": "2\.0", "method": "Query", "id": "Microphone Mute", "result": {.*?}}}}'), self.__MatchMicrophoneMute, None)
            self.AddMatchString(re.compile(b'{"jsonrpc": "2\.0", "method": "Query", "id": "Share Cast Code", "result": {.*?}}}}'), self.__MatchShareCastCode, None)
            self.AddMatchString(re.compile(b'{"jsonrpc": "2\.0", "method": "Query", "id": "Speaker Volume", "result": {.*?}}}}'), self.__MatchSpeakerVolume, None)

        self.meeting_begin_time_directory = Directory('MeetingListBeginTimeResults', 4, filler='')
        self.meeting_begin_time_directory.write_status_function = self.WriteStatus

        self.meeting_creator_name_directory = Directory('MeetingListCreatorNameResults', 4, filler='')
        self.meeting_creator_name_directory.write_status_function = self.WriteStatus

        self.meeting_end_time_directory = Directory('MeetingListEndTimeResults', 4, filler='')
        self.meeting_end_time_directory.write_status_function = self.WriteStatus

        self.meeting_id_directory = Directory('MeetingListIDResults', 4, filler='')
        self.meeting_id_directory.write_status_function = self.WriteStatus

        self.meeting_title_directory = Directory('MeetingListTitleResults', 4, filler='')
        self.meeting_title_directory.write_status_function = self.WriteStatus

        self.meeting_type_directory = Directory('MeetingListTypeResults', 4, filler='Unknown')
        self.meeting_type_directory.write_status_function = self.WriteStatus

    @property
    def NumberofMeetingParticipants(self):
        return self._NumberofMeetingParticipants

    @NumberofMeetingParticipants.setter
    def NumberofMeetingParticipants(self, value):
        try:
            if not 1 <= int(value) <= 10:
                self.Error(['Number of Meeting Participants Parameter is outside of the range of allowable values.'])
            else:
                self._NumberofMeetingParticipants= int(value)
                self.meeting_participants_scroller = Scroller([], self._NumberofMeetingParticipants)
        except (ValueError, TypeError):
            self.Error('Number of Meeting Participants Parameter is the wrong type.')

    def SetLoginHandShake(self, value, url):
        if self.devicePassword:
            encryptedPassword = 'auth-' + base64encode(self.devicePassword.encode()).strip().decode()
            handshake = self._handshake % {'uri': self.uri, 'ipAddress': self.ipAddress, 'randomstring': self.generatestring(), 'encryptedPassword': encryptedPassword}
            self.Send(handshake)
        else:
            self.MissingCredentialsLog('Password')

    def build(self, id, method, params):
        return json.dumps({"jsonrpc": "2.0", "id": id, "method": method, "params": params})

    def __MatchControlCommandAck(self, match, tag):
        self.__CheckResponseForErrors(match.group(1).decode(), match.group(0).decode())

    def __meeting_participants_name_refresh(self):
        for position, name in enumerate(self.meeting_participants_scroller, 1):
            if isinstance(name, dict):
                name = name['nickname']
            
            self.WriteStatus('MeetingParticipantsNameResults', name, {'Position': position})
            
    def SetCameraMute(self, value, qualifier):

        ValueStateValues = {
            'On': False,
            'Off': True
        }

        if value in ValueStateValues:
            params = {"action": "EnableCamera", "action_params": {"enable": ValueStateValues[value]}}
            CameraMuteCmdString = self.build("Camera Mute", "Call/Device", params)
            self.__SetHelper('CameraMute', CameraMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraMute')

    def UpdateCameraMute(self, value, qualifier):

        params = {"path": ["Device", "CameraInfo"]}
        CameraMuteCmdString = self.build("Camera Mute", "Query", params)
        self.__UpdateHelper('CameraMute', CameraMuteCmdString, value, qualifier)

    def __MatchCameraMute(self, match, tag):

        ValueStateValues = {
            False: 'On',
            True: 'Off'
        }

        results = self.__CheckResponseForErrors('Camera Mute', match.group(0).decode())
        if results:
            try:
                value = ValueStateValues[results['result']['data']['camera_info']['switch']]
                self.WriteStatus('CameraMute', value, None)
            except KeyError:
                self.Error(['Camera Mute: Invalid/unexpected response'])

    def SetMeetingControl(self, value, qualifier):

        ValueStateValues = {
            'Start': 'StartMeeting',
            'Join': 'JoinMeeting',
            'End': 'DissolveMeeting',
            'Leave': 'LeaveMeeting',
            'Leave Waiting Room': 'LeaveWaitingRoom'
        }

        if value in ValueStateValues:
            params = {"action": ValueStateValues[value]}
            if value == 'Start':
                params["action_params"] = {"meeting_type": "instant"}
            elif value == 'Join':
                meetingID = qualifier.get('MeetingID')
                if not meetingID:
                    return self.Discard('Invalid Command for SetMeetingControl')
                params["action_params"] = {"meeting_code": meetingID.replace(' ', '')}                    
                password = qualifier.get('Password')
                if not password:
                    password = ''
                params['action_params']['password'] = password
            MeetingControlCmdString = self.build("Meeting Control", "Call/Meeting", params)
            self.__SetHelper('MeetingControl', MeetingControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMeetingControl')

    def SetMeetingListResultSet(self, value, qualifier):

        meetingID = None
        if 1 <= int(value) <= 4:
            meetingID = self.ReadStatus('MeetingListIDResults', {'Position': value})

        if meetingID:
            meetingID = meetingID.replace(' ', '')
        else:
            self.Discard('Invalid Command for SetMeetingListResultSet')

    def SetMeetingListUpdate(self, value, qualifier):

        params = {"path": ["Meeting", "MeetingList"]}
        MeetingListUpdateCmdString = self.build("Meeting List", "Query", params)
        self.__SetHelper('MeetingListUpdate', MeetingListUpdateCmdString, value, qualifier)

    def __MatchMeetingList(self, match, tag):

        MeetingTypeStates = {
            -1: 'Unknown',
            0: 'One Time Meeting',
            1: 'Recurring Meeting',
            2: 'WeChat Meeting',
            3: 'Screen Sharing Meeting',
        }

        beginTimeList = []
        creatorNameList = []
        endTimeList = []
        idList = []
        titleList = []
        typeList = []
        results = self.__CheckResponseForErrors('Meeting List Update', match.group(0).decode())
        if results:
            for meeting in results['result']['data']['meeting_list']:
                beginTimeList.append(str(time.strftime('%Y-%m-%d %H:%M',time.localtime(meeting['meeting_time']['begin_time']))))
                creatorNameList.append(meeting['meeting_creator_name'])
                endTimeList.append(str(time.strftime('%Y-%m-%d %H:%M',time.localtime(meeting['meeting_time']['end_time']))))
                idList.append(meeting['formatted_meeting_code'])
                titleList.append(meeting['meeting_title'])
                typeList.append(MeetingTypeStates[meeting['meeting_type']])
        self.meeting_begin_time_directory.reset(beginTimeList)
        self.meeting_creator_name_directory.reset(creatorNameList)
        self.meeting_end_time_directory.reset(endTimeList)
        self.meeting_id_directory.reset(idList)
        self.meeting_title_directory.reset(titleList)
        self.meeting_type_directory.reset(typeList)

    def SetMeetingParticipantsAudioMute(self, value, qualifier):

        position = qualifier['Position']

        if 1 <= position <= self.meeting_participants_scroller.window and self.meeting_participants_scroller[position - 1] not in [self.meeting_participants_scroller.end, self.meeting_participants_scroller.fill]:
            params = {"action": "MuteMember", "action_params": {"user_id": self.meeting_participants_scroller[position - 1]['user_id']}}
            MeetingParticipantsAudioMuteCmdString = self.build("Meeting Participants Audio Mute", "Call/MeetingControl", params)
            self.__SetHelper('MeetingParticipantsAudioMute', MeetingParticipantsAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMeetingParticipantsAudioMute')

    def SetMeetingParticipantsAudioMuteAll(self, value, qualifier):

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if value in ValueStateValues:
            params = {"action": "MuteAll", "action_params": {"audio_allow_unmute_by_self": ValueStateValues[value]}}
            MeetingParticipantsAudioMuteAllCmdString = self.build("Meeting Participants Audio Mute All", "Call/MeetingControl", params)
            self.__SetHelper('MeetingParticipantsAudioMuteAll', MeetingParticipantsAudioMuteAllCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMeetingParticipantsAudioMuteAll')

    def SetMeetingParticipantsNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':           self.meeting_participants_scroller.previous,
            'Down':         self.meeting_participants_scroller.next,
            'Page Up':      self.meeting_participants_scroller.previous_page,
            'Page Down':    self.meeting_participants_scroller.next_page
        }

        if value in ValueStateValues and self.meeting_participants_scroller.all_size > 0:
            ValueStateValues[value]()
            self.__meeting_participants_name_refresh()
        else:
            self.Discard('Invalid Command for SetMeetingParticipantsNavigation')

    def SetMeetingParticipantsRemove(self, value, qualifier):

        position = qualifier['Position']

        ValueStateValues = {
            'True':     True,
            'False':    False
        }

        if 1 <= position <= self.meeting_participants_scroller.window and self.meeting_participants_scroller[position - 1] not in [self.meeting_participants_scroller.end, self.meeting_participants_scroller.fill]:
            params = {"action": "RemoveMember", "action_params": {"user_id": self.meeting_participants_scroller[position - 1]['user_id'], 'allow_join': ValueStateValues[value]}}
            MeetingParticipantsRemoveCmdString = self.build("Meeting Participants Remove", "Call/MeetingControl", params)
            self.__SetHelper('MeetingParticipantsRemove', MeetingParticipantsRemoveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMeetingParticipantsRemove')

    def SetMeetingParticipantsUpdate(self, value, qualifier):

        params = {"path": ["Members"]}
        MeetingParticipantsUpdateCmdString = self.build("Meeting Participants Update", "Query", params)
        self.__SetHelper('MeetingParticipantsUpdate', MeetingParticipantsUpdateCmdString, value, qualifier)

    def __MatchMeetingParticipantsUpdate(self, match, tag):
        results = self.__CheckResponseForErrors('Meeting Participants Update', match.group(0).decode())
        if results:
            try:
                self.meeting_participants_scroller.overwrite(results['result']['data']['user_list_info'])
            except KeyError:
                self.meeting_participants_scroller.clear()
                return self.Error(['Meeting Participants Update: Invalid/unexpected response'])
        else:
            self.meeting_participants_scroller.clear()

        self.__meeting_participants_name_refresh()

    def SetMeetingParticipantsVideoMute(self, value, qualifier):

        position = qualifier['Position']

        if 1 <= position <= self.meeting_participants_scroller.window and self.meeting_participants_scroller[position - 1] not in [self.meeting_participants_scroller.end, self.meeting_participants_scroller.fill]:
            params = {"action": "StopVideo", "action_params": {"user_id": self.meeting_participants_scroller[position - 1]['user_id']}}
            MeetingParticipantsVideoMuteCmdString = self.build("Meeting Participants Video Mute", "Call/MeetingControl", params)
            self.__SetHelper('MeetingParticipantsVideoMute', MeetingParticipantsVideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMeetingParticipantsVideoMute')

    def UpdateMeetingStatus(self, value, qualifier):

        params = {"path": ["Meeting", "MeetingInfo"]}
        MeetingStatusCmdString = self.build("Meeting Status", "Query", params)
        self.__UpdateHelper('MeetingStatus', MeetingStatusCmdString, value, qualifier)

    def __MatchMeetingStatus(self, match, tag):

        MeetingStatusStates = {
            0: 'Not In Meeting',
            1: 'In Meeting',
            2: 'Joining Meeting',
            3: 'Waiting Room',
            4: 'Sharing Screen Before Meeting',
            5: 'PSTN Before Meeting'
        }

        MeetingTypeStates = {
            -1: 'Unknown',
            0: 'One Time Meeting',
            1: 'Recurring Meeting',
            2: 'WeChat Meeting',
            3: 'Screen Sharing Meeting',
        }

        results = self.__CheckResponseForErrors('Meeting Status', match.group(0).decode())
        if results:
            try:
                meetingStatus = MeetingStatusStates[results['result']['data']['meeting_info']['meeting_status']]
                self.WriteStatus('MeetingStatus', meetingStatus, None)
            except KeyError:
                return self.Error(['Meeting Status: Invalid/unexpected response'])

            if meetingStatus == 'In Meeting':
                try:
                    value = results['result']['data']['meeting_info']['meeting_title']
                    self.WriteStatus('MeetingTitle', value, None)
                except KeyError:
                    self.Error(['Meeting Title: Invalid/unexpected response'])

                try:
                    value = MeetingTypeStates[results['result']['data']['meeting_info']['meeting_type']]
                    self.WriteStatus('MeetingType', value, None)
                except KeyError:
                    self.Error(['Meeting Type: Invalid/unexpected response'])

                try:
                    time_stamp = results['result']['data']['meeting_info']['meeting_time']['begin_time']
                    value = str(time.strftime('%Y-%m-%d %H:%M',time.localtime(time_stamp)))
                    self.WriteStatus('MeetingBeginTime', value, None)
                except KeyError:
                    self.Error(['Meeting Begin Time: Invalid/unexpected response'])

                try:
                    time_stamp = results['result']['data']['meeting_info']['meeting_time']['end_time']
                    value = str(time.strftime('%Y-%m-%d %H:%M',time.localtime(time_stamp)))
                    self.WriteStatus('MeetingEndTime', value, None)
                except KeyError:
                    self.Error(['Meeting End Time: Invalid/unexpected response'])

                try:
                    value = results['result']['data']['meeting_info']['meeting_password']
                    self.WriteStatus('MeetingPasswordStatus', value, None)
                except KeyError:
                    self.Error(['Meeting Password Status: Invalid/unexpected response'])

                try:
                    value = results['result']['data']['meeting_info']['formatted_meeting_code']
                    self.WriteStatus('MeetingIDStatus', value, None)
                except KeyError:
                    self.Error(['Meeting ID Status: Invalid/unexpected response'])

                try:
                    value = results['result']['data']['meeting_info']['meeting_creator_name']
                    self.WriteStatus('MeetingCreatorName', value, None)
                except KeyError:
                    self.Error(['Meeting Creator Name: Invalid/unexpected response'])
            else:
                self.WriteStatus('MeetingTitle', '', None)
                self.WriteStatus('MeetingType', 'Unknown', None)
                self.WriteStatus('MeetingBeginTime', '', None)
                self.WriteStatus('MeetingEndTime', '', None)
                self.WriteStatus('MeetingPasswordStatus', '', None)
                self.WriteStatus('MeetingIDStatus', '', None)
                self.WriteStatus('MeetingCreatorName', '', None)

    def SetMicrophoneMute(self, value, qualifier):

        ValueStateValues = {
            'On': False,
            'Off': True
        }

        if value in ValueStateValues:
            params = {"action": "EnableMic", "action_params": {"enable": ValueStateValues[value]}}
            MicrophoneMuteCmdString = self.build("Microphone Mute", "Call/Device", params)
            self.__SetHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneMute')

    def UpdateMicrophoneMute(self, value, qualifier):

        params = {"path": ["Device", "MicInfo"]}
        MicrophoneMuteCmdString = self.build("Microphone Mute", "Query", params)
        self.__UpdateHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)

    def __MatchMicrophoneMute(self, match, tag):

        ValueStateValues = {
            False: 'On',
            True: 'Off'
        }

        results = self.__CheckResponseForErrors('Microphone Mute', match.group(0).decode())
        if results:
            try:
                value = ValueStateValues[results['result']['data']['mic_info']['switch']]
                self.WriteStatus('MicrophoneMute', value, None)
            except KeyError:
                self.Error(['Microphone Mute: Invalid/unexpected response'])

    def SetShare(self, value, qualifier):

        ShareTypeStates = {
            'Local PC':         0,
            'Captured Device':  1
        }
        share_type = qualifier['Share Type']

        ShareVoiceStates = {
            'On':   True,
            'Off':  False
        }
        share_voice = qualifier['Share Voice']

        FluencyFirstStates = {
            'On':   True,
            'Off':  False
        }
        fluency_first = qualifier['Fluency First']

        select_index = qualifier['Select Index']

        device_id = qualifier['Device ID']

        ValueStateValues = {
            'Start':    'StartShare',
            'Stop':     'StopShare'
        }

        if value in ValueStateValues:
            params = {'action': ValueStateValues[value]}

            if value == 'Start' and share_type in ShareTypeStates and share_voice in ShareVoiceStates:
                params['action_params'] = {'share_type': ShareTypeStates[share_type], 'share_voice': ShareVoiceStates[share_voice]}

                if share_type == 'Local PC' and fluency_first in FluencyFirstStates and 0 <= select_index:
                    params['action_params']['fluency_first'] = FluencyFirstStates[fluency_first]
                    params['action_params']['select_index'] = select_index
                elif share_type == 'Captured Device':
                    if device_id:
                        params['action_params']['device_id'] = device_id
                else:
                    self.Discard('Invalid Command for SetShare')
                    return
            elif value != 'Stop':
                self.Discard('Invalid Command for SetShare')
                return

            ShareCmdString = self.build("Share", "Call/Share", params)
            self.__SetHelper('Share', ShareCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShare')

    def UpdateShareCastCode(self, value, qualifier):

        params = {"path": ["Share"]}
        ShareCastCodeCmdString = self.build("Share Cast Code", "Query", params)
        self.__UpdateHelper('ShareCastCode', ShareCastCodeCmdString, value, qualifier)

    def __MatchShareCastCode(self, match, tag):

        results = self.__CheckResponseForErrors('Share Cast Code', match.group(0).decode())
        if results:
            try:
                value = results['result']['data']['share']['cast_code']
                self.WriteStatus('ShareCastCode', value, None)
            except KeyError:
                return self.Error(['Share Cast Code: Invalid/unexpected response'])

    def SetShareGuide(self, value, qualifier):

        ValueStateValues = {
            'On':   'OpenShareGuide',
            'Off':  'CloseShareGuide'
        }

        if value in ValueStateValues:
            params = {"action": ValueStateValues[value]}
            ShareGuideCmdString = self.build("Share Guide", "Call/Share", params)
            self.__SetHelper('ShareGuide', ShareGuideCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShareGuide')

    def SetShareWindow(self, value, qualifier):

        ShareVoiceStates = {
            'On':   True,
            'Off':  False
        }
        share_voice = qualifier['Share Voice']

        FluencyFirstStates = {
            'On':   True,
            'Off':  False
        }
        fluency_first = qualifier['Fluency First']

        select_index = qualifier['Select Index']

        ValueStateValues = {
            'Start':    'StartWindowShare',
            'Stop':     'StopWindowShare'
        }

        if value in ValueStateValues:
            params = {'action': ValueStateValues[value]}

            if value == 'Start' and share_voice in ShareVoiceStates and fluency_first in FluencyFirstStates and 0 <= select_index:
                params['action_params'] = {'share_voice': ShareVoiceStates[share_voice]}
                params['action_params']['fluency_first'] = FluencyFirstStates[fluency_first]
                params['action_params']['select_index'] = select_index
            elif value != 'Stop':
                self.Discard('Invalid Command for SetShareWindow')
                return

            ShareWindowCmdString = self.build("Share Window", "Call/Share", params)
            self.__SetHelper('ShareWindow', ShareWindowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShareWindow')

    def SetSpeakerVolume(self, value, qualifier):

        if 0 <= value <= 100:
            params = {"action": "SetSpeakerVolume", "action_params": {"volume": value}}
            SpeakerVolumeCmdString = self.build("Speaker Volume", "Call/Device", params)
            self.__SetHelper('SpeakerVolume', SpeakerVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerVolume')

    def UpdateSpeakerVolume(self, value, qualifier):

        params = {"path": ["Device", "SpeakerInfo"]}
        SpeakerVolumeCmdString = self.build("Speaker Volume", "Query", params)
        self.__UpdateHelper('SpeakerVolume', SpeakerVolumeCmdString, value, qualifier)

    def __MatchSpeakerVolume(self, match, tag):

        results = self.__CheckResponseForErrors('Speaker Volume', match.group(0).decode())
        if results:
            try:
                value = results['result']['data']['speaker_info']['volume']
                if 0 <= value <= 100:
                    self.WriteStatus('SpeakerVolume', value, None)
                else:
                    self.Error(['Speaker Volume: Invalid/unexpected response'])
            except TypeError:
                self.Error(['Speaker Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            1: 'Fail',
            2: 'Control System Disabled',
            3: 'Rooms Not Logged In',
            4: 'Request Header Error',
            5: 'Authentication Failed',
            6: 'Query Path Error',
            7: 'Subscribe Path Error',
            8: 'Parameter Error',
            9: 'Unsupported Action',
            10: 'Request Too Frequently',
            11: 'Subscribe Failed',
            12: 'Rooms Network Failed',
            13: 'Rooms Proactively Disconnected',
            14: 'Rooms Version Retired',
            15: 'Rooms CSAPI Version Retired',
            16: 'Rooms CSAPI Password Failed',
            17: 'Repeat Operation',
            9999: 'Unknown Error',
            10000: 'Rooms Not In Meeting',
            10001: 'Rooms Already In Meeting',
            10002: 'Rooms Not Invited',
            10003: 'End Meeting Failed',
            10004: 'Leave Meeting Failed',
            10005: 'Join Meeting Failed',
            10006: 'Meeting Code Mismatch',
            10007: 'No Permission to Join Meeting',
            10008: 'Meeting Canceled',
            10009: 'Meeting Deleted',
            10010: 'Meeting Code Invalid',
            10011: 'Meeting Registration Failed',
            10012: 'Webinar Meeting Rooms Binding User Host',
            10013: 'Webinar Meeting Rooms Binding User CoHost',
            10014: 'Host Not In Meeting',
            10015: 'Meeting Locked',
            10016: 'Rooms Has No Enterprise Permission',
            10017: 'Meeting Already Joined From Other App',
            10018: 'Meeting Needs Password',
            10019: 'Meeting Does Not Exist',
            10020: 'Meeting Password Error',
            10021: 'Failed To Enter Waiting Room',
            10022: 'Rooms Not Host Or Cohost',
            10023: 'No Permission To Join Private Meeting',
            10024: 'No Permission To Create Instant Meeting',
            10025: 'Cannot Join Meeting',
            10026: 'Cannot Start Instant Meeting, Exit Sharing Mode',
            10027: 'Cannot Join Meeting, Exit Sharing Mode',
            10028: 'Cannot Join Meeting, Exit Sharing Mode',
            10029: 'Cannot Join Meeting, Whiteboard In Use',
            10030: 'Cannot Join PMI Meeting',
            10031: 'Unknown Layout',
            10032: 'Cannot Switch Layout',
            20000: 'No Camera Available',
            20001: 'Camera Already Enabled',
            20002: 'Camera Already Disabled',
            20003: 'Camera Not Accessible',
            20004: 'No Mic Available',
            20005: 'Mic Already Enabled',
            20006: 'Mic Already Disabled',
            20007: 'Mic Not Accessible',
            20008: 'Push Video Failed',
            20009: 'Push Video Limit',
            20010: 'Push Audio Failed',
            20011: 'Push Audio Limit',
            20012: 'Push Audio Timeout',
            20013: 'Audience Have No Permission To Operate',
            20014: 'Speaker Test Failed',
            20015: 'Mic Test Failed',
            20016: 'PTZ Failed, Camera Off',
            20017: 'PTZ Failed, Camera Off And Not In Meeting',
            20018: 'PTZ Failed, Camera ID Error',
            20019: 'Camera Select Error, Cannot Find Camera ID',
            40000: 'PSTN Not Enabled',
            40001: 'PSTN Incorrect Action Command',
            40002: 'PSTN Dial Failed, Whiteboard In Use',
            40003: 'PSTN Dial Failed, Exit Sharing Mode',
            40004: 'PSTN Dial Failed, Exit Cast Guide',
            40005: 'PSTN Dial Is Ringing Error',
            40006: 'PSTN Dial State Error',
            40007: 'PSTN Dial Phone Number Error',
            50000: 'User Not in Meeting',
            50001: 'Cannot Leave Meeting',
            50002: 'Recording Disabled',
            50003: 'Already Recording',
            50004: 'Request To Record First'
        }

        results = json.loads(response, strict=False)
        err_code = results['result']['error_code']
        if err_code in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[err_code])])
            results = ''
        elif err_code != 0:
            self.Error(['{0}: Unknown Error Code {1}'.format(sourceCmdName, err_code)])
            results = ''
        return results

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.send_text(commandstring)

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

            self.send_text(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.SetLoginHandShake(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    ################################################################
    # BEGIN WEBSOCKET METHODS
    ################################################################

    def generatestring(self):
        return base64encode('{}'.format(random.randint(-27555755, 666333366)).zfill(16).encode()).decode(
            'utf-8').strip()

    def get_mask_key(self):
        return '{}'.format(random.randint(0, 6553)).zfill(4).encode()

    def try_decode_UTF8(self, data):
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return False
        except Exception as e:
            raise (e)

    def encode_to_UTF8(self, data):
        try:
            return data.encode('utf-8', 'ignore')
        except UnicodeEncodeError as e:
            return False
        except Exception as e:
            raise (e)

    def mask(self, mask_key, data):
        if data is None:
            data = ""
        _m = array.array("B", mask_key)
        _d = array.array("B", data)
        return _mask(_m, _d)

    def _get_masked(self, mask_key, message):
        s = self.mask(mask_key, message)
        return mask_key + s

    def send_text(self, message, masked=True, opcode=TEXT):
        if isinstance(message, bytes):
            message = self.try_decode_UTF8(message)
            if not message:
                return False

        header = bytearray()
        payload = self.encode_to_UTF8(message)
        payload_length = len(payload)
        if payload_length <= 125:
            header.append(FIN | opcode)
            header.append(1 << 7 | payload_length)
        elif payload_length >= 126 and payload_length <= 65535:
            header.append(FIN | opcode)
            header.append(1 << 7 | PAYLOAD_LEN_EXT16)
            header.extend(struct.pack(">H", payload_length))
        elif payload_length < 18446744073709551616:
            header.append(FIN | opcode)
            header.append(1 << 7 | PAYLOAD_LEN_EXT64)
            header.extend(struct.pack(">Q", payload_length))
        else:
            raise Exception("Message is too big. Consider breaking it into chunks.")

        if masked:
            mask_key = self.get_mask_key()
            self.Send(bytes(header + self._get_masked(mask_key, payload)))
        else:
            self.Send(bytes(header + payload))

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
        
        #check incoming data if it matched any expected data from device module
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

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self, Hostname)
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
# BEGIN DIRECTORY CLASSES
################################################################

def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_driver()
        return res

    return wrapper
    
class Directory:

    def __init__(self, write_function_name, display_count, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Position'
        self._qualifier_type = 'Enum'
        self.write_function_name = write_function_name
        self.entry_list = []

        self._start_index = 0
        self.auto_update = True
        self.filler = filler
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

        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Number':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            self.write_status_function(self.write_function_name, self.entry_function(entry[0]), {self.qualifier_name : position_value})

    def write_status_function(self, value, qualifier, context):
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


        if self.__display_position_check(display_position):
            try:
                return self.entry_list.pop(self._start_index + display_position - 1)
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_entry(self, display_position):

        if self.__display_position_check(display_position):
            try:
                return self.entry_list[self._start_index + display_position - 1]
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_displayed_entries(self):

        index = self._start_index
        while index <= self._start_index + self._display_count - 1:
            if index >= len(self.entry_list):
                yield self.filler, index + 1
            else:
                yield self.entry_list[index], index + 1
            index += 1

    def __display_position_check(self, position):

        return 0 < position <= self._display_count

    @UseAutoUpdate
    def scroll_up(self, step=1):
        if self._start_index - step >= 0:
            self._start_index -= step
        else:
            self._start_index = 0

    @UseAutoUpdate
    def scroll_down(self, step=1):
        if self._start_index + step < len(self.entry_list):
            self._start_index += step
        else:
            self._start_index = len(self.entry_list) - 1 # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1


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
