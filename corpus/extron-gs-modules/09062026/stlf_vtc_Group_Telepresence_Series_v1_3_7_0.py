from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
import json
from re import compile, search
import urllib.error
import urllib.request
from struct import pack
from random import randint
from base64 import b64encode as _b64encode
import hashlib
from binascii import b2a_hex as _b2a_hex, unhexlify
import hmac as HMAC
import time


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CallStatus': {'Parameters': ['Call'], 'Status': {}},
            'CameraControl': {'Status': {}},
            'CameraPreset': {'Status': {}},
            'CameraSelect': {'Status': {}},
            'Conference': {'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DTMF': {'Status': {}},
            'FavoriteID': {'Parameters': ['Button'], 'Status': {}},
            'FavoriteNavigation': {'Status': {}},
            'FavoriteNumber': {'Parameters': ['Button'], 'Status': {}},
            'FavoritePresence': {'Parameters': ['Button'], 'Status': {}},
            'FavoriteResult': {'Parameters': ['Button'], 'Status': {}},
            'FavoriteSearch': {'Status': {}},
            'Hook': {'Status': {}},
            'MicrophoneMute': {'Status': {}},
            'ParticipantAction': {'Status': {}},
            'ParticipantNavigation': {'Status': {}},
            'ParticipantResult': {'Parameters': ['Call', 'Button', 'Detail Type'], 'Status': {}},
            'ParticipantUpdate': {'Status': {}},
            'PCShare': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button', 'Detail Type'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'Transfer': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Parameters': ['Volume Select'], 'Status': {}},
            'ScheduledConferencesNavigation': {'Status': {}},
            'ScheduledConferencesID': {'Parameters': ['Button'], 'Status': {}},
            'ScheduledConferencesResult': {'Parameters': ['Button'], 'Status': {}},
            'ScheduledConferencesSearch': {'Status': {}},
            'ScheduledConferencesState': {'Parameters': ['Button'], 'Status': {}},
            'ScheduledConferencesEndTime': {'Parameters': ['Button'], 'Status': {}},
            'ScheduledConferencesStartTime': {'Parameters': ['Button'], 'Status': {}},
            'SelfView': {'Status': {}},
        }

        self.AudioRex = compile(b'{"response":{"counter":\d+,"audio":{"counter":\d+,"mute":(true|false),"incall_volume":(\d+),"ringer_volume":(\d+),"adjunct_volume":(\d+)}}}')
        self.videoMuteRex = compile(b'"video":{"counter":\d+,"mute":(true|false),"')
        self.SelfViewRex = compile(b'"self_view":([0-2])')
        self.PcShareStatusRex = compile(b'"pc_share_status":([0-2])')
        self.callStatusRex = compile(b'{"response":{"counter":\d+,"calls":{"counter":\d+,"list":\[.*\]}}}')
        self.DoNotDisturbRex = compile(b'"dnd":(true|false),')
        self.PhonebookRex = compile(b'{"response":{("view_sequence":\d+,"total_entries":\d+,)?"results":\[.*\]}}\r\n')
        self.ErrorRex = compile(b'"error":{"error_code":(\d+),"')
        self.nameList = []
        self.faveList = []
        self.partList = {1: [], 2: [], 3: []}

        self.StartingEntry = 0
        self.FavoriteStartingEntry = 0
        self.SearchStartingEntry = 0
        self.ParticipantStartingEntry = {1: 0, 2: 0, 3: 0}

        self.NumberOfButton_Favorite = 5
        self.NumberOfButton_Participant = 5
        self.NumberOfButton_PhonebookSearch = 5
        self.NumberOfButton_ScheduledConferences = 5

        self.ScheduledConList = []
        self.ScheduledConStartingEntry = 0

    @property
    def NumberOfFavoriteSearch(self):
        return self.NumberOfButton_Favorite

    @NumberOfFavoriteSearch.setter
    def NumberOfFavoriteSearch(self, value):
        if 1 <= int(value) <= 15:
            self.NumberOfButton_Favorite = int(value)
        else:
            self.Discard('Invalid range for NumberOfFavoriteSearch.')

    @property
    def NumberOfParticipantSearch(self):
        return self.NumberOfButton_Participant

    @NumberOfParticipantSearch.setter
    def NumberOfParticipantSearch(self, value):
        if 1 <= int(value) <= 15:
            self.NumberOfButton_Participant = int(value)
        else:
            self.Discard('Invalid range for NumberOfParticipantSearch.')

    @property
    def NumberOfPhonebookSearch(self):
        return self.NumberOfButton_PhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        if 1 <= int(value) <= 15:
            self.NumberOfButton_PhonebookSearch = int(value)
        else:
            self.Discard('Invalid range for NumberOfPhonebookSearch.')

    @property
    def NumberOfScheduledConferencesSearch(self):
        return self.NumberOfButton_ScheduledConferences

    @NumberOfScheduledConferencesSearch.setter
    def NumberOfScheduledConferencesSearch(self, value):
        if 1 <= int(value) <= 15:
            self.NumberOfButton_ScheduledConferences = int(value)
        else:
            self.Discard('Invalid range for NumberOfScheduledConferencesSearch.')

    def UpdateCallStatus(self, value, qualifier):

        callStatusStates = {
            '0': 'Inactive',
            '1': 'Dialing',
            '2': 'Waiting',
            '3': 'Ringing',
            '4': 'In Call',
            '5': 'On Hold',
            '6': 'Ended',
        }

        CallStatusCmdString = '{"request":{"action":"state","filter":"calls"}}\r'
        res = self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)
        if res:
            try:
                tempValue = search(self.callStatusRex, res)
                parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))
                numberOfCalls = len(parsed_json['response']['calls']['list'])

                if numberOfCalls == 0:
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '1'})
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '2'})
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '3'})
                elif numberOfCalls == 1:
                    callState1 = callStatusStates[str(parsed_json['response']['calls']['list'][0]['state'])]
                    self.WriteStatus('CallStatus', callState1, {'Call': '1'})
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '2'})
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '3'})
                elif numberOfCalls == 2:
                    callState1 = callStatusStates[str(parsed_json['response']['calls']['list'][0]['state'])]
                    callState2 = callStatusStates[str(parsed_json['response']['calls']['list'][1]['state'])]
                    self.WriteStatus('CallStatus', callState1, {'Call': '1'})
                    self.WriteStatus('CallStatus', callState2, {'Call': '2'})
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '3'})
                else:
                    callState1 = callStatusStates[str(parsed_json['response']['calls']['list'][0]['state'])]
                    callState2 = callStatusStates[str(parsed_json['response']['calls']['list'][1]['state'])]
                    callState3 = callStatusStates[str(parsed_json['response']['calls']['list'][2]['state'])]
                    self.WriteStatus('CallStatus', callState1, {'Call': '1'})
                    self.WriteStatus('CallStatus', callState2, {'Call': '2'})
                    self.WriteStatus('CallStatus', callState3, {'Call': '3'})
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateCallStatus'])

    def SetCameraSelect(self, value, qualifier):

        ValueStateValues = {
            '1': '0',
            '2': '1',
            '3': '2',
        }

        CameraSelectCmdString = '{{"request":{{"action":"camera_select","index":{0}}}}}\r'.format(ValueStateValues[value])
        self.__SetHelper('CameraSelect', CameraSelectCmdString, value, qualifier)

    def SetConference(self, value, qualifier):

        ValueStateValues = {
            'Create': 'create_conference',
            'Add To': 'add_to_conference',
        }

        if value in ValueStateValues:
            ConferenceCmdString = '{{"request":{{"action":"{0}"}}}}\r'.format(ValueStateValues[value])
            self.__SetHelper('Conference', ConferenceCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetConference'])

    def SetCameraControl(self, value, qualifier):

        ValueStateValues1 = {
            'Local': 'local',
            'Remote': 'remote',
        }

        ValueStateValues2 = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Zoom In': 'zoom-in',
            'Zoom Out': 'zoom-out',
        }

        cameraSelect = qualifier['Camera Select']
        durationSelect = qualifier['Duration']
        CameraControlCmdString = ''
        if value == 'Stop':
            CameraControlCmdString = '{{"request":{{"action":"camera_control","{0}":true,"stop":true}}}}\r'.format(ValueStateValues1[cameraSelect])
        else:
            CameraControlCmdString = '{{"request":{{"action":"camera_control","{0}":true,"direction":"{1}","duration":{2}}}}}\r'.format(ValueStateValues1[cameraSelect], ValueStateValues2[value], durationSelect)
        self.__SetHelper('CameraControl', CameraControlCmdString, value, qualifier)

    def SetCameraPreset(self, value, qualifier):
        ValueStateValues = {
            '0' : '0',
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4'
        }

        CameraPresetCmdString = '{{"request":{{"action":"camera_control","preset":{0}}}}}\r'.format(ValueStateValues[value])
        self.__SetHelper('CameraPreset', CameraPresetCmdString, value, qualifier)

    def SetDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        DoNotDisturbCmdString = '{{"request":{{"action":"do_not_disturb","dnd":{0}}}}}\r'.format(ValueStateValues[value])
        self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def UpdateDoNotDisturb(self, value, qualifier):

        DoNotDisturbValues = {
            'true': 'On',
            'false': 'Off'
        }

        DoNotDisturbCmdString = '{"request":{"action":"state","filter":"endpoint"}}\r'
        res = self.__UpdateHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)
        if res:
            try:
                tempValue = search(self.DoNotDisturbRex, res)
                DNDvalue = DoNotDisturbValues[tempValue.group(1).decode()]
                self.WriteStatus('DoNotDisturb', DNDvalue, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateDoNotDisturb'])

    def SetDTMF(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
        }

        DTMFCmdString = '{{"request":{{"action":"keypad","digits":"{0}"}}}}\r'.format(ValueStateValues[value])
        self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)

    def SetFavoriteNavigation(self, value, qualifier):
        self.Debug = True

        ValueStates = {
            0: 'Unknown',
            1: 'Available',
            2: 'In Call',
            3: 'Do Not Disturb',
            4: 'Calls Forwarded',
            5: 'Not Available',
            6 : 'Mobile',
            7 : '***End of list***'
        }

        if 'Page Up' == value:
            self.FavoriteStartingEntry -= self.NumberOfButton_Favorite
        elif 'Page Down' == value:
            self.FavoriteStartingEntry += self.NumberOfButton_Favorite

        if self.FavoriteStartingEntry >= len(self.faveList):
            self.FavoriteStartingEntry = len(self.faveList) - 1

        if self.FavoriteStartingEntry < 0:
            self.FavoriteStartingEntry = 0

        Button = 1
        for a in self.faveList[self.FavoriteStartingEntry:]:
            self.WriteStatus('FavoritePresence', ValueStates[a['presence']], {'Button': Button})
            self.WriteStatus('FavoriteNumber', a['number'], {'Button': Button})
            self.WriteStatus('FavoriteResult', a['display_name'], {'Button': Button})
            self.WriteStatus('FavoriteID', a['id'], {'Button': Button})
            Button += 1
            if Button == self.NumberOfButton_Favorite + 1:
                break
        if self.faveList:
            for a in range(Button,self.NumberOfButton_Favorite+1):
                self.Write('StatusFavoritePresence','', {'Button': a})
                self.Write('StatusFavoriteNumber','', {'Button': a})
                self.Write('StatusFavoriteID','',{'Button': a})
                self.Write('StatusFavoriteResult','', {'Button': a})

    def SetFavoriteSearch(self, value, qualifier):
        self.Debug = True

        FavoriteCmdString = '{"request":{"action":"state","filter":"favorites"}}\r'
        res = self.__UpdateHelper('FavoriteSearch', FavoriteCmdString, value, qualifier)
        if res:
            try:
                res = res.decode('iso-8859-1')
                parsed_json = json.loads(res)
                self.faveList = parsed_json['response']['favorites']['list']
                self.faveList.append({'id': '***End of list***', 'display_name': '***End of list***', 'presence': 7, 'number': '***End of list***', 'type': 0})
                self.SetFavoriteNavigation(None, None)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for SetFavoriteSearch'])

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Hang Up': 'hangup',
            'Answer': 'answer',
            'Reject': 'reject',
            'Ignore': 'ignore',
            'Hold': 'hold',
            'Resume': 'resume',
            'Join Now': 'scheduled_conference'
        }

        number = qualifier['Number']
        if 'Dial Number' in value and number:
            HookCmdString = '{{"request":{{"action":"dial","number":"{0}"}}}}\r'.format(number)
        elif 'Dial Favorite' in value and number:
            HookCmdString = '{{"request":{{"action":"dial","favourite":{0}}}}}\r'.format(number)
        elif 'Dial Scheduled Conference' in value and number:
            HookCmdString = '{{"request":{{"action":"dial","scheduled_conference":{0}}}}}\r'.format(number)
        elif 'Join Now' in value:
            HookCmdString = '{{"request":{{"action":"dial","number":"scheduled_conference"}}}}\r'
        else:
            HookCmdString = '{{"request":{{"action":"{0}"}}}}\r'.format(ValueStateValues[value])
        self.__SetHelper('Hook', HookCmdString, value, qualifier)

    def SetMicrophoneMute(self, value, qualifier):

        MicrophoneMuteValues = {
            'On': 'true',
            'Off': 'false'
        }

        MicrophoneMuteCmdString = '{{"request":{{"action":"audio_mute","mute":{0}}}}}\r'.format(MicrophoneMuteValues[value])
        self.__SetHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)

    def UpdateMicrophoneMute(self, value, qualifier):

        MicrophoneMuteValues = {
            'true': 'On',
            'false': 'Off'
        }

        MicrophoneMuteCmdString = '{"request":{"action":"state","filter":"audio"}}\r'
        res = self.__UpdateHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)
        if res:
            try:
                tempValue = search(self.AudioRex, res)
                audioMute = MicrophoneMuteValues[tempValue.group(1).decode()]
                self.WriteStatus('MicrophoneMute', audioMute, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateMicrophoneMute'])

    def SetParticipantAction(self, value, qualifier):
        self.Debug = True

        CallConstraints = {
            'Min': 1,
            'Max': 3
        }
        ValueStateValues = {
            'Mute': 'mute_participant',
            'Unmute': 'unmute_participant',
            'Kick': 'kick_participant'
        }

        Call = int(qualifier['Call'])
        if value in ValueStateValues and CallConstraints['Min'] <= Call <= CallConstraints['Max']:
            ParticipantID = qualifier['ID']
            if ParticipantID:
                ParticipantActionCmdString = '{{"request":{{"action":"{0}","partid":{1}}}}}\r'.format(ValueStateValues[value], ParticipantID)
                self.__SetHelper('ParticipantAction', ParticipantActionCmdString, value, qualifier)
            else:
                self.Error(['Invalid Command for SetParticipantAction'])
        else:
            self.Error(['Invalid Command for SetParticipantAction'])

    def SetParticipantNavigation(self, value, qualifier):
        self.Debug = True    

        CallConstraints = {
            'Min': 1,
            'Max': 3
        }

        Call = int(qualifier['Call'])
        if CallConstraints['Min'] <= Call <= CallConstraints['Max']:
            NumberOfAdvance = self.ParticipantStartingEntry[Call]

            if 'Page Up' == value:
                NumberOfAdvance -= self.NumberOfButton_Participant
            elif 'Page Down' == value:
                NumberOfAdvance += self.NumberOfButton_Participant

            if NumberOfAdvance >= len(self.partList[Call]):
                NumberOfAdvance = len(self.partList[Call]) - 1

            if NumberOfAdvance < 0:
                NumberOfAdvance = 0

            self.ParticipantStartingEntry[Call] = NumberOfAdvance

            Button = 1

            for a in self.partList[Call][NumberOfAdvance:]:
                self.WriteStatus('ParticipantResult', a['name'], {'Call': str(Call), 'Button': Button, 'Detail Type' : 'Name'})
                self.WriteStatus('ParticipantResult', str(a['id']), {'Call': str(Call), 'Button': Button, 'Detail Type' : 'ID'})
                Button += 1
                if Button == self.NumberOfButton_Participant + 1:
                    break
            if Button <= self.NumberOfButton_Participant and self.partList[Call]:
                for a in range(Button,self.NumberOfButton_Participant+1):
                    self.WriteStatus('ParticipantResult','', {'Call': str(Call), 'Button': a})
        else:
            self.Error(['Invalid Command for SetParticipantNavigation'])

    def SetParticipantUpdate(self, value, qualifier):
        self.Debug = True

        self.partList = {1: [], 2: [], 3: []}
        ParticipantUpdateCmdString = '{"request":{"action":"state","filter":"calls"}}\r'
        res = self.__UpdateHelper('ParticipantUpdate', ParticipantUpdateCmdString, value, qualifier)
        if res:
            try:
                tempValue = search(self.callStatusRex, res)
                parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))
                Call = 1
                for a in parsed_json['response']['calls']['list']:
                    self.partList[Call] = a['participants']
                    self.partList[Call].append({"id": "***End of list***", "state": "***End of list***",
                                                "name": "***End of list***","number": "***End of list***"})
                    self.SetParticipantNavigation(None, {'Call': str(Call)})
                    Call += 1
                    if Call == 4:
                        break
                for a in range(Call, 4):
                    self.partList[a] = []
                    self.SetParticipantNavigation(None, {'Call': str(a)})
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for SetParticipantUpdate'])

    def SetPCShare(self, value, qualifier):

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        if value in ValueStateValues:
            PCShareCmdString = '{{"request":{{"action":"share_pc","share":{0}}}}}\r'.format(ValueStateValues[value])
            self.__SetHelper('PCShare', PCShareCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetPCShare'])

    def UpdatePCShare(self, value, qualifier):
        self.UpdateVideoMute(None, None)

    def SetPhonebookNavigation(self, value, qualifier):
        self.Debug = True

        phonebookValues = {
            'Global': 'global',
            'Personal': 'personal',
            'Favorite': 'favorite',
        }

        phonebook_type = qualifier['Phonebook Type']
        
        searchName = qualifier.get('Name')
        if searchName:
            if 'Page Up' in value:
                NumberOfAdvance = self.SearchStartingEntry - self.NumberOfButton_PhonebookSearch
            else:
                NumberOfAdvance = self.SearchStartingEntry + self.NumberOfButton_PhonebookSearch
            if NumberOfAdvance < 0:
                NumberOfAdvance = 0
            PhonebookUpdateCmdString = '{{"request":{{"action":"contacts","type":"{0}","count":{1},"start":{2},"search":"{3}"}}}}\r'.format(phonebookValues[phonebook_type], self.NumberOfButton_PhonebookSearch, NumberOfAdvance, searchName)
        else:
            if 'Page Up' in value:
                NumberOfAdvance = self.StartingEntry - self.NumberOfButton_PhonebookSearch
            else:
                NumberOfAdvance = self.StartingEntry + self.NumberOfButton_PhonebookSearch
            if NumberOfAdvance < 0:
                NumberOfAdvance = 0
            PhonebookUpdateCmdString = '{{"request":{{"action":"contacts","type":"{0}","count":{1},"start":{2}}}}}\r'.format(phonebookValues[phonebook_type], self.NumberOfButton_PhonebookSearch, NumberOfAdvance)

        res = self.__UpdateHelper('PhonebookNavigation', PhonebookUpdateCmdString, value, qualifier)
        if res:
            try:
                tempValue = search(self.PhonebookRex, res)
                parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))

                self.nameList = []
                EntriestoDisplay = len(parsed_json['response']['results'])

                if searchName:
                    if 'Page Up' in value:
                        self.SearchStartingEntry = self.SearchStartingEntry - EntriestoDisplay
                    else:
                        self.SearchStartingEntry = self.SearchStartingEntry + EntriestoDisplay
                    if self.SearchStartingEntry < 0:
                        self.SearchStartingEntry = 0
                else:
                    if 'Page Up' in value:
                        self.StartingEntry = self.StartingEntry - EntriestoDisplay
                    else:
                        self.StartingEntry = self.StartingEntry + EntriestoDisplay
                    if self.StartingEntry < 0:
                        self.StartingEntry = 0

                button = 0
                while button < EntriestoDisplay:
                    name = parsed_json['response']['results'][button]['display_name']
                    self.nameList.append(name)
                    value = '{0}'.format(name)
                    self.WriteStatus('PhonebookSearchResult', value, {'Button': int(button + 1), 'Detail Type' : 'Name'})
                    button += 1

                if button <= self.NumberOfButton_PhonebookSearch and self.nameList:
                    self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button + 1, 'Detail Type' : 'Name'})
                    self.WriteStatus('PhonebookSearchResult', '', {'Button': button + 1, 'Detail Type' : 'Number'})
                    button += 1
                    for i in range(button, int(self.NumberOfButton_PhonebookSearch)):
                        self.WriteStatus('PhonebookSearchResult', '', {'Button': i + 1, 'Detail Type' : 'Name'})
                        self.WriteStatus('PhonebookSearchResult', '', {'Button': i + 1, 'Detail Type' : 'Number'})

            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for SetPhonebookNavigation'])

    def SetPhonebookSearchSet(self, value, qualifier):
        self.Debug = True

        ButtonConstraints = {
            'Min': 1,
            'Max': self.NumberOfButton_PhonebookSearch
        }
        phonebookValues = {
            'Global': 'global',
            'Personal': 'personal',
            'Favorite': 'favorite',
        }

        phonebook_type = qualifier['Phonebook Type']

        if ButtonConstraints['Min'] <= value <= ButtonConstraints['Max'] and len(self.nameList) >= value:
            PhonebookUpdateCmdString = '{{"request":{{"action":"contacts","type":"{0}","search":"{1}"}}}}\r'.format(phonebookValues[phonebook_type], self.nameList[value - 1])
            res = self.__UpdateHelper('PhonebookSearchSet', PhonebookUpdateCmdString, value, qualifier)
            Id = None
            if res:
                try:
                    tempValue = search(self.PhonebookRex, res)
                    parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))
                    Id = parsed_json['response']['results'][0]['id']
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Invalid/unexpected response for SetPhonebookSearchSet'])

            if Id:
                PhonebookUpdateCmdString = '{{"request":{{"action":"contacts","type":"{0}","search":"{1}","detail":true,"contactid":{2}}}}}\r'.format(phonebookValues[phonebook_type], self.nameList[value - 1], Id)
                res = self.__UpdateHelper('PhonebookSearchSet', PhonebookUpdateCmdString, value, qualifier)
                if res:
                    try:
                        tempValue = search(self.PhonebookRex, res)
                        parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))
                        number = parsed_json['response']['results'][0]['numbers'][0]['number']
                        self.WriteStatus('PhonebookSearchResult', number, {'Button': value, 'Detail Type' : 'Number'})
                    except (KeyError, IndexError, AttributeError):
                        self.Error(['Invalid/unexpected response for SetPhonebookSearchSet'])

        else:
            self.Error(['Invalid Command for SetPhonebookSearchSet'])

    def SetPhonebookUpdate(self, value, qualifier):
        self.Debug = True

        phonebookValues = {
            'Global': 'global',
            'Personal': 'personal',
            'Favorite': 'favorite',
        }

        phonebook_type = qualifier['Phonebook Type']
        searchName = qualifier.get('Name')
        if searchName:
            PhonebookUpdateCmdString = '{{"request":{{"action":"contacts","type":"{0}","search":"{1}"}}}}\r'.format(phonebookValues[phonebook_type], searchName)
        else:
            PhonebookUpdateCmdString = '{{"request":{{"action":"contacts","type":"{0}","count":{1},"start":0}}}}\r'.format(phonebookValues[phonebook_type], self.NumberOfButton_PhonebookSearch)
        res = self.__UpdateHelper('PhonebookUpdate', PhonebookUpdateCmdString, value, qualifier)
        if res:
            try:
                tempValue = search(self.PhonebookRex, res)
                parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))

                self.nameList = []
                self.StartingEntry = 0
                self.SearchStartingEntry = 0
                EntriestoDisplay = len(parsed_json['response']['results'])

                button = 0
                while button < EntriestoDisplay:
                    name = parsed_json['response']['results'][button]['display_name']
                    self.nameList.append(name)
                    value = '{0}'.format(name)
                    self.WriteStatus('PhonebookSearchResult', value, {'Button': int(button + 1), 'Detail Type' : 'Name'})
                    button += 1

                if button <= self.NumberOfButton_PhonebookSearch:
                    self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button + 1, 'Detail Type' : 'Name'})
                    button += 1
                    for i in range(button, int(self.NumberOfButton_PhonebookSearch) + 1):
                        self.WriteStatus('PhonebookSearchResult', '', {'Button': i + 1, 'Detail Type' : 'Name'})
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for SetPhonebookUpdate'])

    def SetSelfView(self, value, qualifier):

        ValueStateValues = {
            'Auto' : 'auto',
            'On'   : 'on',
            'Off'  : 'off'
        }

        SelfViewCmdString = '{{"request":{{"action":"self_view","{0}":true}}}}\r'.format(ValueStateValues[value])
        self.__SetHelper('SelfView', SelfViewCmdString, value, qualifier)

    def UpdateSelfView(self, value, qualifier):
        self.UpdateVideoMute(None, None)

    def SetTransfer(self, value, qualifier):

        ValueStateValues = {
            'Start': 'start_transfer',
            'End': 'complete_transfer'
        }

        if value in ValueStateValues:
            TransferCmdString = '{{"request":{{"action":"{0}"}}}}\r'.format(ValueStateValues[value])
            self.__SetHelper('Transfer', TransferCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetTransfer'])

    def SetVideoMute(self, value, qualifier):

        videomuteValues = {
            'On': 'true',
            'Off': 'false'
        }

        VideoMuteCmdString = '{{"request":{{"action":"video_mute","mute":{0}}}}}\r'.format(videomuteValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        videomuteValues = {
            'true': 'On',
            'false': 'Off'
        }

        SelfViewValues = {
            '0': 'Auto',
            '1': 'Off',
            '2': 'On'
        }

        PcSharingStatusValues = {
            '0': 'None',
            '1': 'Local',
            '2': 'Remote'
        }

        VideoMuteCmdString = '{"request":{"action":"state","filter":"video"}}\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                tempValue = search(self.videoMuteRex, res)
                value = videomuteValues[tempValue.group(1).decode()]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateVideoMute'])
            try:
                tempValue = search(self.SelfViewRex,res)
                value = SelfViewValues[tempValue.group(1).decode()]
                self.WriteStatus('SelfView', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateSelfView'])
            try:
                tempValue = search(self.PcShareStatusRex, res)
                value = PcSharingStatusValues[tempValue.group(1).decode()]
                self.WriteStatus('PCShare',value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdatePCShare'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 10
        }

        VolumeQualifierConstraints = {
            'Incall': 'incall',
            'Ringer': 'ringer',
            'Adjunct': 'adjunct',
        }

        volType = qualifier['Volume Select']

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '{{"request":{{"action":"volume","device":"{0}","absolute":{1}}}}}\r'.format(VolumeQualifierConstraints[volType], value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetVolume'])

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '{"request":{"action":"state","filter":"audio"}}\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                tempValue = search(self.AudioRex, res)
                audioIncall = int(tempValue.group(2))
                audioRiger = int(tempValue.group(3))
                audioAdjunct = int(tempValue.group(4))
                self.WriteStatus('Volume', audioIncall, {'Volume Select': 'Incall'})
                self.WriteStatus('Volume', audioRiger, {'Volume Select': 'Ringer'})
                self.WriteStatus('Volume', audioAdjunct, {'Volume Select': 'Adjunct'})
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateVolume'])

    def SetScheduledConferencesNavigation(self, value, qualifier):
        self.Debug = True

        ValueStates = {
            1 : 'Normal',
            2 : 'Soon',
            3 : 'Now',
            4 : 'Now Quiet'
        }

        if 'Page Up' == value:
            self.ScheduledConStartingEntry -= self.NumberOfButton_ScheduledConferences
        elif 'Page Down' == value:
            self.ScheduledConStartingEntry += self.NumberOfButton_ScheduledConferences

        if self.ScheduledConStartingEntry >= len(self.ScheduledConList):
            self.ScheduledConStartingEntry = len(self.ScheduledConList) - 1

        if self.ScheduledConStartingEntry < 0:
            self.ScheduledConStartingEntry = 0

        Button = 1
        for a in self.ScheduledConList[self.ScheduledConStartingEntry:]:
            self.WriteStatus('ScheduledConferencesID', a['id'], {'Button': Button})
            self.WriteStatus('ScheduledConferencesState', ValueStates[a['state']], {'Button': Button})
            self.WriteStatus('ScheduledConferencesStartTime', a['start_time'], {'Button': Button})
            self.WriteStatus('ScheduledConferencesEndTime', a['end_time'], {'Button': Button})
            self.WriteStatus('ScheduledConferencesResult', a['name'],{'Button': Button})
            Button += 1
            if Button == self.NumberOfButton_ScheduledConferences+1: break
        for a in range(Button,self.NumberOfButton_ScheduledConferences+1):
            self.WriteStatus('ScheduledConferencesID', '', {'Button': Button})
            self.WriteStatus('ScheduledConferencesState', 'Normal', {'Button': a})
            self.WriteStatus('ScheduledConferencesStartTime', '', {'Button': a})
            self.WriteStatus('ScheduledConferencesEndTime', '', {'Button': a})
            self.WriteStatus('ScheduledConferencesResult', '', {'Button': a})

    def SetScheduledConferencesSearch(self, value, qualifier):
        self.Debug = True

        ScheduledConferencesSearchCmdString = '{"request":{"action":"state","filter":"scheduled_conferences"}}\r'
        res = self.__UpdateHelper('ScheduledConferencesSearch', ScheduledConferencesSearchCmdString, value, qualifier)
        if res:
            try:
                res = res.decode()
                parsed_json = json.loads(res)

                self.ScheduledConList = parsed_json['response']['scheduled_conferences']['list']
                for Conference in self.ScheduledConList:
                    Conference['start_time'] = time.asctime(time.localtime(int(Conference['start_time'])))
                    Conference['end_time'] = time.asctime(time.localtime(int(Conference['end_time'])))
                self.ScheduledConList.append({"id": 1, "state": 1, "name": "***End of list***", "start_time": "***End of list***","end_time": "***End of list***"})
                self.SetScheduledConferencesNavigation(None,None)
            except (ValueError, KeyError, IndexError):
                self.Error(['Scheduled Conferences Search: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        response_encoded = response.encode(encoding='iso-8859-1')
        tempValue = search(self.ErrorRex, response_encoded)
        if tempValue:
            parsed_json = json.loads(response)
            self.Error([parsed_json['error']['error_message']])
            response_encoded = b''
        return response_encoded

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n').decode('iso-8859-1')
            if not res:
                return b''
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n').decode('iso-8859-1')
            if not res:
                return b''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected', None)
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected', None)
        self.connectionFlag = False

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

_0xffffffffL = 0xffffffff
def isunicode(s):
    return isinstance(s, str)
def isbytes(s):
    return isinstance(s, bytes)
def isinteger(n):
    return isinstance(n, int)
def b(s):
    return s.encode("latin-1")
def binxor(a, b):
    return bytes([x ^ y for (x, y) in zip(a, b)])

def b64encode(data, chars="+/"):
    if isunicode(chars):
        return _b64encode(data, chars.encode('utf-8')).decode('utf-8')
    else:
        return _b64encode(data, chars)

def b2a_hex(s):
    return _b2a_hex(s).decode('us-ascii')


class DeviceHTTPClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
 
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + _b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
 
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())
        self.Opener.add_handler(urllib.request.HTTPCookieProcessor())
        
        self.connectionCounter = 15

        self.IPAddress = ipAddress
        self.port = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AuthenticationRequired': {'Status': {}},
            'CallStatus': {'Parameters': ['Call'], 'Status': {}},
            'CameraControl': {'Status': {}},
            'CameraPreset': {'Status': {}},
            'CameraSelect': {'Status': {}},
            'Conference': {'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DTMF': {'Status': {}},
            'FavoriteID': {'Parameters': ['Button'], 'Status': {}},
            'FavoriteNavigation': {'Status': {}},
            'FavoriteNumber': {'Parameters': ['Button'], 'Status': {}},
            'FavoritePresence': {'Parameters': ['Button'], 'Status': {}},
            'FavoriteResult': {'Parameters': ['Button'], 'Status': {}},
            'FavoriteSearch': {'Status': {}},
            'Hook': {'Status': {}},
            'MicrophoneMute': {'Status': {}},
            'ParticipantAction': {'Status': {}},
            'ParticipantNavigation': {'Status': {}},
            'ParticipantResult': {'Parameters': ['Call', 'Button', 'Detail Type'], 'Status': {}},
            'ParticipantUpdate': {'Status': {}},
            'PCShare': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button', 'Detail Type'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'Transfer': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Parameters': ['Volume Select'], 'Status': {}},
            'ScheduledConferencesID': {'Parameters': ['Button'], 'Status': {}},
            'ScheduledConferencesNavigation': {'Status': {}},
            'ScheduledConferencesResult': {'Parameters': ['Button'], 'Status': {}},
            'ScheduledConferencesSearch': {'Status': {}},
            'ScheduledConferencesState': {'Parameters': ['Button'], 'Status': {}},
            'ScheduledConferencesEndTime': {'Parameters': ['Button'], 'Status': {}},
            'ScheduledConferencesStartTime': {'Parameters': ['Button'], 'Status': {}},
            'SelfView': {'Status': {}},
        }

        self.authenticationRex = compile(b'"serial":"(.*)","version":"(.*)","authenticated":false,"salt":"(.*)","iterations":1,"challenge":"(.*)"}')
        self.AudioRex = compile(b'"audio":{"counter":\d+,"mute":(true|false),"incall_volume":(\d+),"ringer_volume":(\d+),"adjunct_volume":(\d+)}')
        self.videoMuteRex = compile(b'"video":{"counter":\d+,"mute":(true|false),"')
        self.callStatusRex = compile(b'{"counter":\d+,"calls":{"counter":\d+,"list":\[.*\]}}')
        self.SelfViewRex = compile(b'"self_view":([0-2])')
        self.PcShareStatusRex = compile(b'"pc_share_status":([0-2])')
        self.DoNotDisturbRex = compile(b'"dnd":(true|false),')
        self.PhonebookRex = compile(b'{("view_sequence":\d+,"total_entries":\d+,)?"results":\[.*\]}')
        self.ErrorRex = compile(b'"error":{"error_code":(\d+),"')
        self.nameList = []
        self.faveList = []
        self.partList = {1: [], 2: [], 3: []}

        self.StartingEntry = 0
        self.FavoriteStartingEntry = 0
        self.SearchStartingEntry = 0
        self.ParticipantStartingEntry = {1: 0, 2: 0, 3: 0}

        self.ScheduledConList = []
        self.ScheduledConStartingEntry = 0

        self.NumberOfButton_Favorite = 5
        self.NumberOfButton_Participant = 5
        self.NumberOfButton_PhonebookSearch = 5
        self.NumberOfButton_ScheduledConferences = 5

    @property
    def NumberOfFavoriteSearch(self):
        return self.NumberOfButton_Favorite

    @NumberOfFavoriteSearch.setter
    def NumberOfFavoriteSearch(self, value):
        if 1 <= int(value) <= 15:
            self.NumberOfButton_Favorite = int(value)
        else:
            self.Discard('Invalid range for NumberOfFavoriteSearch.')

    @property
    def NumberOfParticipantSearch(self):
        return self.NumberOfButton_Participant

    @NumberOfParticipantSearch.setter
    def NumberOfParticipantSearch(self, value):
        if 1 <= int(value) <= 15:
            self.NumberOfButton_Participant = int(value)
        else:
            self.Discard('Invalid range for NumberOfParticipantSearch.')

    @property
    def NumberOfPhonebookSearch(self):
        return self.NumberOfButton_PhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        if 1 <= int(value) <= 15:
            self.NumberOfButton_PhonebookSearch = int(value)
        else:
            self.Discard('Invalid range for NumberOfPhonebookSearch.')

    @property
    def NumberOfScheduledConferencesSearch(self):
        return self.NumberOfButton_ScheduledConferences

    @NumberOfScheduledConferencesSearch.setter
    def NumberOfScheduledConferencesSearch(self, value):
        if 1 <= int(value) <= 15:
            self.NumberOfButton_ScheduledConferences = int(value)
        else:
            self.Discard('Invalid range for NumberOfScheduledConferencesSearch.')

    def UpdateAuthenticationRequired(self, value, qualifier):

        HeartbeatCmdString = '/auth'
        res = self.__UpdateHelper('AuthenticationRequired', value, qualifier, url=HeartbeatCmdString)
        if res:
            try:
                if b'"authenticated":false' in res:
                    authentication = search(self.authenticationRex, res)
                    salt = authentication.group(3).decode()
                    self.challenge = authentication.group(4).decode()
                    self.endpoint_api_key(self.devicePassword, salt, 1)

            except (TypeError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateAuthenticationRequired'])

    def endpoint_api_key(self, password, salt_hex, iterations):

        salt = unhexlify(salt_hex)
        key = PBKDF2(passphrase=password, salt=salt, iterations=iterations, digestmodule=hashlib.sha256, macmodule=HMAC)
        key_hex = key.hexread(32)
        self.endpoint_api_response(key_hex, self.challenge)

    def endpoint_api_response(self, key, challenge):

        key_bytes = unhexlify(key)
        challenge_bytes = str.encode(challenge)
        hash = HMAC.new(key_bytes, challenge_bytes, hashlib.sha256)
        response = hash.hexdigest()

        url = self.RootURL + 'auth?challenge={0}&response={1}'.format(self.challenge, response)
        req = urllib.request.Request(url=url, method='GET')
        res = self.Opener.open(req)

    def UpdateCallStatus(self, value, qualifier):

        callStatusStates = {
            '0': 'Inactive',
            '1': 'Dialing',
            '2': 'Waiting',
            '3': 'Ringing',
            '4': 'In Call',
            '5': 'On Hold',
            '6': 'Ended',
        }

        CallStatusCmdString = '/state?filter=calls'
        res = self.__UpdateHelper('CallStatus', value, qualifier, url=CallStatusCmdString)
        if res:
            try:
                tempValue = search(self.callStatusRex, res)
                parsed_json = json.loads(tempValue.group(0).decode())
                numberOfCalls = len(parsed_json['calls']['list'])

                if numberOfCalls == 0:
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '1'})
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '2'})
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '3'})
                elif numberOfCalls == 1:
                    callState1 = callStatusStates[str(parsed_json['calls']['list'][0]['state'])]
                    self.WriteStatus('CallStatus', callState1, {'Call': '1'})
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '2'})
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '3'})
                elif numberOfCalls == 2:
                    callState1 = callStatusStates[str(parsed_json['calls']['list'][0]['state'])]
                    callState2 = callStatusStates[str(parsed_json['calls']['list'][1]['state'])]
                    self.WriteStatus('CallStatus', callState1, {'Call': '1'})
                    self.WriteStatus('CallStatus', callState2, {'Call': '2'})
                    self.WriteStatus('CallStatus', 'Inactive', {'Call': '3'})
                else:
                    callState1 = callStatusStates[str(parsed_json['calls']['list'][0]['state'])]
                    callState2 = callStatusStates[str(parsed_json['calls']['list'][1]['state'])]
                    callState3 = callStatusStates[str(parsed_json['calls']['list'][2]['state'])]
                    self.WriteStatus('CallStatus', callState1, {'Call': '1'})
                    self.WriteStatus('CallStatus', callState2, {'Call': '2'})
                    self.WriteStatus('CallStatus', callState3, {'Call': '3'})
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateCallStatus'])

    def SetCameraSelect(self, value, qualifier):

        ValueStateValues = {
            '1': '0',
            '2': '1',
            '3': '2',
        }

        CameraSelectCmdString = '/action?action=camera_select&index={0}'.format(ValueStateValues[value])
        self.__SetHelper('CameraSelect', value, qualifier, url=CameraSelectCmdString)

    def SetConference(self, value, qualifier):

        ValueStateValues = {
            'Create': 'create_conference',
            'Add To': 'add_to_conference',
        }

        if value in ValueStateValues:
            ConferenceCmdString = '/action?action={0}'.format(ValueStateValues[value])
            self.__SetHelper('Conference', value, qualifier, url=ConferenceCmdString)
        else:
            self.Error(['Invalid Command for SetConference'])

    def SetCameraControl(self, value, qualifier):

        ValueStateValues1 = {
            'Local': 'local',
            'Remote': 'remote',
        }

        ValueStateValues2 = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Zoom In': 'zoom-in',
            'Zoom Out': 'zoom-out',
        }

        cameraSelect = qualifier['Camera Select']
        durationSelect = qualifier['Duration']
        CameraControlCmdString = ''
        if value == 'Stop':
            CameraControlCmdString = '/action?action=camera_control&{0}=true&stop=true'.format(ValueStateValues1[cameraSelect])
        else:
            CameraControlCmdString = '/action?action=camera_control&{0}=true&direction={1}&duration={2}'.format(ValueStateValues1[cameraSelect], ValueStateValues2[value], durationSelect)
        self.__SetHelper('CameraControl', value, qualifier, url=CameraControlCmdString)

    def SetCameraPreset(self, value, qualifier):
    
        ValueStateValues = {
            '0' : '0',
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4'
        }

        CameraPresetCmdString = '/action?action=camera_control&preset={0}'.format(ValueStateValues[value])
        self.__SetHelper('CameraPreset', value, qualifier, url=CameraPresetCmdString)

    def SetDoNotDisturb(self, value, qualifier):

        DoNotDisturbValues = {
            'On': 'on',
            'Off': 'off'
        }

        DoNotDisturbCmdString = '/action?action=do_not_disturb&{0}'.format(DoNotDisturbValues[value])
        self.__SetHelper('DoNotDisturb', value, qualifier, url=DoNotDisturbCmdString)

    def UpdateDoNotDisturb(self, value, qualifier):

        DoNotDisturbValues = {
            'true': 'On',
            'false': 'Off'
        }

        DoNotDisturbCmdString = '/state?filter=endpoint'
        res = self.__UpdateHelper('DoNotDisturb', value, qualifier, url=DoNotDisturbCmdString)
        if res:
            try:
                tempValue = search(self.DoNotDisturbRex, res)
                DNDvalue = DoNotDisturbValues[tempValue.group(1).decode()]
                self.WriteStatus('DoNotDisturb', DNDvalue, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateDoNotDisturb'])

    def SetDTMF(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
        }

        DTMFCmdString = '/action?action=keypad&digits={0}'.format(ValueStateValues[value])
        self.__SetHelper('DTMF', value, qualifier, url=DTMFCmdString)

    def SetFavoriteNavigation(self, value, qualifier):
        self.Debug = True

        ValueStates = {
            0: 'Unknown',
            1: 'Available',
            2: 'In Call',
            3: 'Do Not Disturb',
            4: 'Calls Forwarded',
            5: 'Not Available',
            6: 'Mobile',
            7: '***End of list***'
        }

        if 'Page Up' == value:
            self.FavoriteStartingEntry -= self.NumberOfButton_Favorite
        elif 'Page Down' == value:
            self.FavoriteStartingEntry += self.NumberOfButton_Favorite

        if self.FavoriteStartingEntry >= len(self.faveList):
            self.FavoriteStartingEntry = len(self.faveList) - 1

        if self.FavoriteStartingEntry < 0:
            self.FavoriteStartingEntry = 0

        Button = 1
        for a in self.faveList[self.FavoriteStartingEntry:]:
            self.WriteStatus('FavoriteID', a['id'],{'Button': Button})
            self.WriteStatus('FavoritePresence', ValueStates[a['presence']], {'Button': Button})
            self.WriteStatus('FavoriteNumber', a['number'], {'Button': Button})
            self.WriteStatus('FavoriteResult', a['display_name'], {'Button': Button})
            Button += 1
            if Button == self.NumberOfButton_Favorite + 1:
                break
        if self.faveList:
            for a in range(Button, self.NumberOfButton_Favorite + 1):
                self.WriteStatus('FavoriteID', '',{'Button': Button})
                self.WriteStatus('FavoritePresence', '', {'Button': a})
                self.WriteStatus('FavoriteNumber', '', {'Button': a})
                self.WriteStatus('FavoriteResult', '', {'Button': a})

    def SetFavoriteSearch(self, value, qualifier):
        self.Debug = True

        self.faveList = []
        FavoriteCmdString = '/state?filter=favorites'
        res = self.__UpdateHelper('FavoriteSearch', value, qualifier, url=FavoriteCmdString)
        if res:
            try:
                res = res.decode('iso-8859-1')
                parsed_json = json.loads(res)
                self.faveList = parsed_json['favorites']['list']
                self.faveList.append({'id': '***End of list***', 'display_name': '***End of list***', 'presence': 7, 'number': '***End of list***', 'type': 0})
                self.SetFavoriteNavigation(None, None)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for SetFavoriteSearch'])

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Hang Up': 'hangup',
            'Answer': 'answer',
            'Reject': 'reject',
            'Ignore': 'ignore',
            'Hold': 'hold',
            'Resume': 'resume',
            'Join Now': 'scheduled_conference'
        }

        number = qualifier['Number']

        if 'Dial Number' in value and number:
            HookCmdString = '/action?action=dial&number={0}'.format(number)
        elif 'Dial Favorite' in value and number:
            HookCmdString = '/action?action=dial&favorite={0}'.format(number)
        elif 'Dial Scheduled Conference' in value and number:
            HookCmdString = '/action?action=dial&scheduled_conference={0}'.format(number)
        elif 'Join Now' in value:
            HookCmdString = '/action?action=dial&scheduled_conference'
        else:
            HookCmdString = '/action?action={0}'.format(ValueStateValues[value])

        self.__SetHelper('Hook', value, qualifier, url=HookCmdString)

    def SetMicrophoneMute(self, value, qualifier):

        MicrophoneMuteValues = {
            'On': 'on',
            'Off': 'off'
        }

        MicrophoneMuteCmdString = '/action?action=audio_mute&{0}'.format(MicrophoneMuteValues[value])
        self.__SetHelper('MicrophoneMute', value, qualifier, url=MicrophoneMuteCmdString)

    def UpdateMicrophoneMute(self, value, qualifier):

        MicrophoneMuteValues = {
            'true': 'On',
            'false': 'Off'
        }

        MicrophoneMuteCmdString = '/state?filter=audio'
        res = self.__UpdateHelper('MicrophoneMute', value, qualifier, url=MicrophoneMuteCmdString)
        if res:
            try:
                tempValue = search(self.AudioRex, res)
                audioMute = MicrophoneMuteValues[tempValue.group(1).decode()]
                self.WriteStatus('MicrophoneMute', audioMute, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateMicrophoneMute'])

    def SetParticipantAction(self, value, qualifier):

        CallConstraints = {
            'Min': 1,
            'Max': 3
        }
        ValueStateValues = {
            'Mute': 'mute_participant',
            'Unmute': 'unmute_participant',
            'Kick': 'kick_participant'
        }

        Call = int(qualifier['Call'])
        if value in ValueStateValues and CallConstraints['Min'] <= Call <= CallConstraints['Max']:
            ParticipantID = qualifier['ID']
            if ParticipantID:
                ParticipantActionCmdString = '/action?action={0}&partid={1}'.format(ValueStateValues[value], ParticipantID)
                self.__SetHelper('ParticipantAction', value, qualifier, url=ParticipantActionCmdString)
            else:
                self.Error(['Invalid Command for SetParticipantAction'])
        else:
            self.Error(['Invalid Command for SetParticipantAction'])

    def SetParticipantNavigation(self, value, qualifier):
        self.Debug = True

        CallConstraints = {
            'Min': 1,
            'Max': 3
        }

        Call = int(qualifier['Call'])
        if CallConstraints['Min'] <= Call <= CallConstraints['Max']:
            NumberOfAdvance = self.ParticipantStartingEntry[Call]

            if 'Page Up' == value:
                NumberOfAdvance -= self.NumberOfButton_Participant
            elif 'Page Down' == value:
                NumberOfAdvance += self.NumberOfButton_Participant

            if NumberOfAdvance >= len(self.partList[Call]):
                NumberOfAdvance = len(self.partList[Call]) - 1

            if NumberOfAdvance < 0:
                NumberOfAdvance = 0

            self.ParticipantStartingEntry[Call] = NumberOfAdvance
            Button = 1
            for a in self.partList[Call][NumberOfAdvance:]:
                self.WriteStatus('ParticipantResult', a['name'], {'Call': str(Call), 'Button': Button, 'Detail Type' : 'Name'})
                self.WriteStatus('ParticipantResult', str(a['id']), {'Call': str(Call), 'Button': Button, 'Detail Type' : 'ID'})
                Button += 1
                if Button == self.NumberOfButton_Participant + 1:
                    break
            if Button <= self.NumberOfButton_Participant and self.partList[Call]:
                for a in range(Button, self.NumberOfButton_Participant + 1):
                    self.WriteStatus('ParticipantResult', '', {'Call': str(Call), 'Button': a, 'Detail Type' : 'Name'})
                    self.WriteStatus('ParticipantResult', '', {'Call': str(Call), 'Button': a, 'Detail Type' : 'ID'})
        else:
            self.Error(['Invalid Command for SetParticipantNavigation'])

    def SetParticipantUpdate(self, value, qualifier):
        self.Debug = True

        self.partList = {1: [], 2: [], 3: []}
        ParticipantUpdateCmdString = '/state?filter=calls'
        res = self.__UpdateHelper('ParticipantUpdate', value, qualifier, url=ParticipantUpdateCmdString)
        if res:
            try:
                tempValue = search(self.callStatusRex, res)
                parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))

                Call = 1
                if parsed_json['calls']['list']:
                    for a in parsed_json['calls']['list']:
                        self.partList[Call] = a['participants']
                        self.partList[Call].append({"id": "***End of list***", "state": "***End of list***",
                                                    "name": "***End of list***", "number": "***End of list***"})
                        self.SetParticipantNavigation(None, {'Call': str(Call)})
                        Call += 1
                        if Call == 4:
                            break
                    for a in range(Call, 4):
                        self.partList[a] = []
                        self.SetParticipantNavigation(None, {'Call': str(a)})
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for SetParticipantUpdate'])

    def SetPCShare(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        if value in ValueStateValues:
            PCShareCmdString = '/action?action=share_pc&{0}'.format(ValueStateValues[value])
            self.__SetHelper('PCShare', value, qualifier, url=PCShareCmdString)
        else:
            self.Error(['Invalid Command for SetPCShare'])

    def UpdatePCShare(self, value, qualifier):
        self.UpdateVideoMute(None, None)

    def SetPhonebookNavigation(self, value, qualifier):
        self.Debug = True

        phonebookValues = {
            'Global': 'global',
            'Personal': 'personal',
            'Favorite': 'favorite',
        }

        phonebook_type = qualifier['Phonebook Type']

        searchName = qualifier.get('Name')
        if searchName:
            if 'Page Up' in value:
                NumberOfAdvance = self.SearchStartingEntry - self.NumberOfButton_PhonebookSearch
            else:
                NumberOfAdvance = self.SearchStartingEntry + self.NumberOfButton_PhonebookSearch
            if NumberOfAdvance < 0:
                NumberOfAdvance = 0
            PhonebookUpdateCmdString = '/contacts?type={0}&count={1}&start={2}&search={3}'.format(phonebookValues[phonebook_type], self.NumberOfButton_PhonebookSearch, NumberOfAdvance, searchName.replace(' ', '%20'))
        else:
            if 'Page Up' in value:
                NumberOfAdvance = self.StartingEntry - self.NumberOfButton_PhonebookSearch
            else:
                NumberOfAdvance = self.StartingEntry + self.NumberOfButton_PhonebookSearch
            if NumberOfAdvance < 0:
                NumberOfAdvance = 0
            PhonebookUpdateCmdString = '/contacts?type={0}&count={1}&start={2}'.format(phonebookValues[phonebook_type], self.NumberOfButton_PhonebookSearch, NumberOfAdvance)

        res = self.__UpdateHelper('PhonebookNavigation', value, qualifier, url=PhonebookUpdateCmdString)
        if res:
            try:
                tempValue = search(self.PhonebookRex, res)
                parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))

                self.nameList = []
                EntriestoDisplay = len(parsed_json['results'])

                if searchName:
                    if 'Page Up' in value:
                        self.SearchStartingEntry = self.SearchStartingEntry - EntriestoDisplay
                    else:
                        self.SearchStartingEntry = self.SearchStartingEntry + EntriestoDisplay
                    if self.SearchStartingEntry < 0:
                        self.SearchStartingEntry = 0
                else:
                    if 'Page Up' in value:
                        self.StartingEntry = self.StartingEntry - EntriestoDisplay
                    else:
                        self.StartingEntry = self.StartingEntry + EntriestoDisplay
                    if self.StartingEntry < 0:
                        self.StartingEntry = 0

                button = 0
                while button < EntriestoDisplay and self.nameList:
                    name = parsed_json['results'][button]['display_name']
                    self.nameList.append(name)
                    self.WriteStatus('PhonebookSearchResult', value, {'Button': int(button + 1), 'Detail Type' : 'Name'})
                    button += 1

                if button <= self.NumberOfButton_PhonebookSearch:
                    self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button + 1, 'Detail Type' : 'Name'})
                    self.WriteStatus('PhonebookSearchResult', '', {'Button': button + 1, 'Detail Type' : 'Number'})
                    button += 1
                    for i in range(button, self.NumberOfButton_PhonebookSearch):
                        self.WriteStatus('PhonebookSearchResult', '', {'Button': i + 1, 'Detail Type' : 'Name'})
                        self.WriteStatus('PhonebookSearchResult', '', {'Button': i + 1, 'Detail Type' : 'Number'})

            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for SetPhonebookNavigation'])

    def SetPhonebookSearchSet(self, value, qualifier):
        self.Debug = True

        ButtonConstraints = {
            'Min': 1,
            'Max': self.NumberOfButton_PhonebookSearch
        }
        phonebookValues = {
            'Global': 'global',
            'Personal': 'personal',
            'Favorite': 'favorite',
        }

        phonebook_type = qualifier['Phonebook Type']
        
        if ButtonConstraints['Min'] <= value <= ButtonConstraints['Max'] and len(self.nameList) >= value:
            PhonebookUpdateCmdString = '/contacts?type={0}&search={1}'.format(phonebookValues[phonebook_type], self.nameList[value - 1].replace(' ', '%20'))
            res = self.__UpdateHelper('PhonebookSearchSet', value, qualifier, url=PhonebookUpdateCmdString)
            Id = None
            if res:
                try:
                    tempValue = search(self.PhonebookRex, res)
                    parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))
                    Id = parsed_json['results'][0]['id']
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Invalid/unexpected response for SetPhonebookSearchSet'])

            if Id:
                PhonebookUpdateCmdString = '/contacts?type={0}&search={1}&detail&contactid={2}'.format(phonebookValues[phonebook_type], self.nameList[value - 1].replace(' ', '%20'), Id)
                res = self.__UpdateHelper('PhonebookSearchSet', value, qualifier, url=PhonebookUpdateCmdString)
                if res:
                    try:
                        tempValue = search(self.PhonebookRex, res)
                        parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))
                        number = parsed_json['results'][0]['numbers'][0]['number']
                        self.WriteStatus('PhonebookSearchResult', number, {'Button': value, 'Detail Type' : 'Number'})
                    except (KeyError, IndexError, AttributeError):
                        self.Error(['Invalid/unexpected response for SetPhonebookSearchSet'])
        else:
            self.Error(['No contacts to select for SetPhonebookSearchSet'])

    def SetPhonebookUpdate(self, value, qualifier):
        self.Debug = True

        phonebookValues = {
            'Global': 'global',
            'Personal': 'personal',
            'Favorite': 'favorite',
        }

        phonebook_type = qualifier['Phonebook Type']

        searchName = qualifier.get('Name')
        if searchName:
            PhonebookUpdateCmdString = '/contacts?type={0}&search={1}'.format(phonebookValues[phonebook_type], searchName.replace(' ', '%20'))
        else:
            PhonebookUpdateCmdString = '/contacts?type={0}&count={1}&start=0'.format(phonebookValues[phonebook_type], self.NumberOfButton_PhonebookSearch)
        res = self.__UpdateHelper('PhonebookUpdate', value, qualifier, url=PhonebookUpdateCmdString)
        if res:
            try:
                tempValue = search(self.PhonebookRex, res)
                parsed_json = json.loads(tempValue.group(0).decode('iso-8859-1'))

                self.nameList = []
                self.StartingEntry = 0
                EntriestoDisplay = len(parsed_json['results'])

                button = 0
                while button < EntriestoDisplay:
                    name = parsed_json['results'][button]['display_name']
                    self.nameList.append(name)
                    value = '{0}'.format(name)
                    self.WriteStatus('PhonebookSearchResult', value, {'Button': int(button + 1), 'Detail Type' : 'Name'})
                    button += 1

                if button <= self.NumberOfButton_PhonebookSearch and self.nameList:
                    self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button + 1, 'Detail Type' : 'Name'})
                    button += 1
                    for i in range(button, self.NumberOfButton_PhonebookSearch):
                        self.WriteStatus('PhonebookSearchResult', '', {'Button': i + 1, 'Detail Type' : 'Name'})
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for SetPhonebookUpdate'])

    def SetSelfView(self, value, qualifier):

        ValueStateValues = {
            'Auto' : 'auto',
            'On'   : 'on',
            'Off'  : 'off'
        }

        SelfViewCmdString = '/action?action=self_view&{0}'.format(ValueStateValues[value])
        self.__SetHelper('SelfView', value, qualifier, url=SelfViewCmdString)

    def SetTransfer(self, value, qualifier):

        ValueStateValues = {
            'Start': 'start_transfer',
            'End': 'complete_transfer'
        }

        if value in ValueStateValues:
            TransferCmdString = '/action?action={0}'.format(ValueStateValues[value])
            self.__SetHelper('Transfer', value, qualifier, url=TransferCmdString)
        else:
            self.Error(['Invalid Command for SetTransfer'])

    def UpdateSelfView(self, value, qualifier):
        self.UpdateVideoMute(None, None)

    def SetVideoMute(self, value, qualifier):

        videomuteValues = {
            'On': 'on',
            'Off': 'off'
        }

        VideoMuteCmdString = '/action?action=video_mute&{0}'.format(videomuteValues[value])
        self.__SetHelper('VideoMute', value, qualifier, url=VideoMuteCmdString)

    def UpdateVideoMute(self, value, qualifier):

        videomuteValues = {
            'true': 'On',
            'false': 'Off'
        }

        SelfViewValues = {
            '0': 'Auto',
            '1': 'Off',
            '2': 'On'
        }

        PcSharingStatusValues = {
            '0': 'None',
            '1': 'Local',
            '2': 'Remote'
        }

        VideoMuteCmdString = '/state?filter=video'
        res = self.__UpdateHelper('VideoMute', value, qualifier, url=VideoMuteCmdString)
        if res:
            try:
                tempValue = search(self.videoMuteRex, res)
                value = videomuteValues[tempValue.group(1).decode()]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateVideoMute'])
            try:
                tempValue = search(self.SelfViewRex,res)
                value = SelfViewValues[tempValue.group(1).decode()]
                self.WriteStatus('SelfView', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateSelfView'])
            try:
                tempValue = search(self.PcShareStatusRex, res)
                value = PcSharingStatusValues[tempValue.group(1).decode()]
                self.WriteStatus('PCShare',value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdatePCShare'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 10
        }

        VolumeQualifierConstraints = {
            'Incall': 'incall',
            'Ringer': 'ringer',
            'Adjunct': 'adjunct',
        }

        volType = qualifier['Volume Select']

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '/action?action=volume&device={0}&absolute={1}'.format(VolumeQualifierConstraints[volType], value)
            self.__SetHelper('Volume', value, qualifier, url=VolumeCmdString)
        else:
            self.Error(['Invalid Command for SetVolume'])

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '/state?filter=audio'
        res = self.__UpdateHelper('Volume', value, qualifier, url=VolumeCmdString)
        if res:
            try:
                tempValue = search(self.AudioRex, res)
                audioIncall = int(tempValue.group(2))
                audioRiger = int(tempValue.group(3))
                audioAdjunct = int(tempValue.group(4))
                self.WriteStatus('Volume', audioIncall, {'Volume Select': 'Incall'})
                self.WriteStatus('Volume', audioRiger, {'Volume Select': 'Ringer'})
                self.WriteStatus('Volume', audioAdjunct, {'Volume Select': 'Adjunct'})
            except (ValueError, KeyError, IndexError, AttributeError):
                self.Error(['Invalid/unexpected response for UpdateVolume'])

    def SetScheduledConferencesNavigation(self, value, qualifier):
        self.Debug = True

        ValueStates = {
            1 : 'Normal',
            2 : 'Soon',
            3 : 'Now',
            4 : 'Now Quiet',
            0 : '***End of list***'
        }

        if 'Page Up' == value:
            self.ScheduledConStartingEntry -= self.NumberOfButton_ScheduledConferences
        elif 'Page Down' == value:
            self.ScheduledConStartingEntry += self.NumberOfButton_ScheduledConferences

        if self.ScheduledConStartingEntry >= len(self.ScheduledConList):
            self.ScheduledConStartingEntry = len(self.ScheduledConList) - 1

        if self.ScheduledConStartingEntry < 0:
            self.ScheduledConStartingEntry = 0

        Button = 1
        for a in self.ScheduledConList[self.ScheduledConStartingEntry:]:
            self.WriteStatus('ScheduledConferencesID', a['id'], {'Button': Button})
            self.WriteStatus('ScheduledConferencesState', ValueStates[a['state']], {'Button': Button})
            self.WriteStatus('ScheduledConferencesStartTime', a['start_time'], {'Button': Button})
            self.WriteStatus('ScheduledConferencesEndTime', a['end_time'], {'Button': Button})
            self.WriteStatus('ScheduledConferencesResult', a['name'],{'Button': Button})
            Button += 1
            if Button == self.NumberOfButton_ScheduledConferences+1: break
        for a in range(Button,self.NumberOfButton_ScheduledConferences+1):
            self.WriteStatus('ScheduledConferencesID', '', {'Button': Button})
            self.WriteStatus('ScheduledConferencesState', 'Normal', {'Button': a})
            self.WriteStatus('ScheduledConferencesStartTime', '', {'Button': a})
            self.WriteStatus('ScheduledConferencesEndTime', '', {'Button': a})
            self.WriteStatus('ScheduledConferencesResult', '', {'Button': a})

    def SetScheduledConferencesSearch(self, value, qualifier):
        self.Debug = True

        self.ScheduledConList = []
        ScheduledConferencesSearchCmdString = '/state?filter=scheduled_conferences'
        res = self.__UpdateHelper('ScheduledConferencesSearch', value, qualifier, url=ScheduledConferencesSearchCmdString)
        if res:
            try:
                res = res.decode('iso-8859-1')
                parsed_json = json.loads(res)
                self.ScheduledConList = parsed_json['scheduled_conferences']['list']
                for Conference in self.ScheduledConList:
                    Conference['start_time'] = time.asctime(time.localtime(int(Conference['start_time'])))
                    Conference['end_time'] = time.asctime(time.localtime(int(Conference['end_time'])))
                self.ScheduledConList.append({"id":"***End of list***","state":0,"name":"***End of list***","start_time":"***End of list***","end_time":"***End of list***"})
                self.SetScheduledConferencesNavigation(None,None)
            except (KeyError, IndexError):
                self.Error(['Scheduled Conferences Search: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True
        
        url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/html'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            res = b''
        except urllib.error.URLError as err:
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):
            
        url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/html'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = b''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = b''
        except Exception as err:
            res = b''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected', None)
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected', None)
        self.connectionFlag = False

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self._ipAddress, self._port)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self._port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')


class HTTPClass(DeviceHTTPClass):

    def __init__(self, ipAddress=None, port=80, deviceUsername='admin', devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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

###########################################################################
# pbkdf2 - PKCS#5 v2.0 Password-Based Key Derivation
#
# Copyright (C) 2007-2011 Dwayne C. Litzenberger <dlitz@dlitz.net>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Country of origin: Canada
#
###########################################################################
# Sample PBKDF2 usage:
#   from Crypto.Cipher import AES
#   from pbkdf2 import PBKDF2
#   import os
#
#   salt = os.urandom(8)    # 64-bit salt
#   key = PBKDF2("This passphrase is a secret.", salt).read(32) # 256-bit key
#   iv = os.urandom(16)     # 128-bit IV
#   cipher = AES.new(key, AES.MODE_CBC, iv)
#     ...
#
# Sample crypt() usage:
#   from pbkdf2 import crypt
#   pwhash = crypt("secret")
#   alleged_pw = raw_input("Enter password: ")
#   if pwhash == crypt(alleged_pw, pwhash):
#       print "Password good"
#   else:
#       print "Invalid password"
#
###########################################################################

class PBKDF2(object):
    """PBKDF2.py : PKCS#5 v2.0 Password-Based Key Derivation

    This implementation takes a passphrase and a salt (and optionally an
    iteration count, a digest module, and a MAC module) and provides a
    file-like object from which an arbitrarily-sized key can be read.

    If the passphrase and/or salt are unicode objects, they are encoded as
    UTF-8 before they are processed.

    The idea behind PBKDF2 is to derive a cryptographic key from a
    passphrase and a salt.

    PBKDF2 may also be used as a strong salted password hash.  The
    'crypt' function is provided for that purpose.

    Remember: Keys generated using PBKDF2 are only as strong as the
    passphrases they are derived from.
    """

    def __init__(self, passphrase, salt, iterations=1000, digestmodule=hashlib.sha1, macmodule=HMAC):
        self.__macmodule = macmodule
        self.__digestmodule = digestmodule
        self._setup(passphrase, salt, iterations, self._pseudorandom)

    def _pseudorandom(self, key, msg):
        """Pseudorandom function.  e.g. HMAC-SHA1"""
        return self.__macmodule.new(key=key, msg=msg,
            digestmod=self.__digestmodule).digest()

    def read(self, number_of_bytes):
        """Read the specified number of key bytes."""
        if self.closed:
            raise ValueError("file-like object is closed")

        size = len(self.__buf)
        blocks = [self.__buf]
        i = self.__blockNum
        while size < number_of_bytes:
            i += 1
            if i > _0xffffffffL or i < 1:
                # We could return "" here, but
                raise OverflowError("derived key too long")
            block = self.__f(i)
            blocks.append(block)
            size += len(block)
        buf = b("").join(blocks)
        retval = buf[:number_of_bytes]
        self.__buf = buf[number_of_bytes:]
        self.__blockNum = i
        return retval

    def __f(self, i):
        # i must fit within 32 bits
        assert 1 <= i <= _0xffffffffL
        U = self.__prf(self.__passphrase, self.__salt + pack("!L", i))
        result = U
        for _ in range(2, 1+self.__iterations):
            U = self.__prf(self.__passphrase, U)
            result = binxor(result, U)
        return result

    def hexread(self, octets):
        """Read the specified number of octets. Return them as hexadecimal.

        Note that len(obj.hexread(n)) == 2*n.
        """
        return b2a_hex(self.read(octets))

    def _setup(self, passphrase, salt, iterations, prf):
        # Sanity checks:

        # passphrase and salt must be str or unicode (in the latter
        # case, we convert to UTF-8)
        if isunicode(passphrase):
            passphrase = passphrase.encode("UTF-8")
        elif not isbytes(passphrase):
            raise TypeError("passphrase must be str or unicode")
        if isunicode(salt):
            salt = salt.encode("UTF-8")
        elif not isbytes(salt):
            raise TypeError("salt must be str or unicode")

        # iterations must be an integer >= 1
        if not isinteger(iterations):
            raise TypeError("iterations must be an integer")
        if iterations < 1:
            raise ValueError("iterations must be at least 1")

        # prf must be callable
        if not hasattr(prf, '__call__'):
            raise TypeError("prf must be callable")

        self.__passphrase = passphrase
        self.__salt = salt
        self.__iterations = iterations
        self.__prf = prf
        self.__blockNum = 0
        self.__buf = b("")
        self.closed = False

    def close(self):
        """Close the stream."""
        if not self.closed:
            del self.__passphrase
            del self.__salt
            del self.__iterations
            del self.__prf
            del self.__blockNum
            del self.__buf
            self.closed = True


def crypt(word, salt=None, iterations=None):
    """PBKDF2-based unix crypt(3) replacement.

    The number of iterations specified in the salt overrides the 'iterations'
    parameter.

    The effective hash length is 192 bits.
    """

    # Generate a (pseudo-)random salt if the user hasn't provided one.
    if salt is None:
        salt = _makesalt()

    # salt must be a string or the us-ascii subset of unicode
    if isunicode(salt):
        salt = salt.encode('us-ascii').decode('us-ascii')
    elif isbytes(salt):
        salt = salt.decode('us-ascii')
    else:
        raise TypeError("salt must be a string")

    # word must be a string or unicode (in the latter case, we convert to UTF-8)
    if isunicode(word):
        word = word.encode("UTF-8")
    elif not isbytes(word):
        raise TypeError("word must be a string or unicode")

    # Try to extract the real salt and iteration count from the salt
    if salt.startswith("$p5k2$"):
        (iterations, salt, dummy) = salt.split("$")[2:5]
        if iterations == "":
            iterations = 400
        else:
            converted = int(iterations, 16)
            if iterations != "%x" % converted:  # lowercase hex, minimum digits
                raise ValueError("Invalid salt")
            iterations = converted
            if not (iterations >= 1):
                raise ValueError("Invalid salt")

    # Make sure the salt matches the allowed character set
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./"
    for ch in salt:
        if ch not in allowed:
            raise ValueError("Illegal character %r in salt" % (ch,))

    if iterations is None or iterations == 400:
        iterations = 400
        salt = "$p5k2$$" + salt
    else:
        salt = "$p5k2$%x$%s" % (iterations, salt)
    rawhash = PBKDF2(word, salt, iterations).read(24)
    return salt + "$" + b64encode(rawhash, "./")

PBKDF2.crypt = staticmethod(crypt)

def _makesalt():
    """Return a 48-bit pseudorandom salt for crypt().

    This function is not suitable for generating cryptographic secrets.
    """
    binarysalt = b("").join([pack("@H", randint(0, 0xffff)) for _ in range(3)])
    return b64encode(binarysalt, "./")
