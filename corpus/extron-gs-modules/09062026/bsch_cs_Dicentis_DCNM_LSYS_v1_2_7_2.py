from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import json
import base64
import struct
from base64 import encodebytes as base64encode
import random
import array
import re
from collections import OrderedDict
from extronlib import Version

try:
    from Extron import Platform
    platform = Platform()
except ImportError:
    platform = 'Pro'

minimumVersion = (3,4,6)
version = tuple(int(i) for i in Version().split('.'))

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
    return _d.tobytes()

class DeviceClass:
    
    def __init__(self, IPAddress):

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
        self.NumberofActiveMicrophones = 5
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveMicrophoneNameResults': {'Parameters': ['Position'], 'Status': {}},
            'ActiveMicrophoneNavigation': {'Status': {}},
            'ActiveMicrophoneParticipantIDResults': {'Parameters': ['Position'], 'Status': {}},
            'ActiveMicrophoneSeatIDResults': {'Parameters': ['Position'], 'Status': {}},
            'ActiveMicrophoneUpdate': {'Status': {}},
            'MeetingDescription': {'Status': {}},
            'MeetingEndDate': {'Status': {}},
            'MeetingStartDate': {'Status': {}},
            'MeetingState': {'Status': {}},
            'MeetingTitle': {'Status': {}},
            'MeetingUpdate': {'Status': {}},
            'MicrophoneState': {'Parameters': ['Seat ID'], 'Status': {}},
            'Power': {'Status': {}},
            'SeatInformation': {'Parameters': ['Seat ID', 'Type'], 'Status': {}},
            'VotingAnswers': {'Status': {}},
            'VotingDescription': {'Status': {}},
            'VotingID': {'Status': {}},
            'VotingInformationUpdate': {'Status': {}},
            'VotingReferenceNumber': {'Status': {}},
            'VotingResultAnswer': {'Parameters': ['Button'], 'Status': {}},
            'VotingResultCount': {'Parameters': ['Button'], 'Status': {}},
            'VotingResultUpdate': {'Status': {}},
            'VotingState': {'Status': {}},
            'VotingSubject': {'Status': {}},
        }

        self._active_microphones = {
            'seatName': '',
            'seatID': '',
            'participantId' : ''
        }

        self.handshake_initialized = False
        self.messageID = 0
        self.Authenticated = False
        self.ipAddress = IPAddress
        self.uri = '/DICENTIS/API'
        self._ReceiveSocketData = None
        self.ReceiveData = self.__ReceiveData
        self._receiveBuffer = None

        self._handshake = (
            "GET %(uri)s HTTP/1.1\r\n"
            "Host: %(ipAddress)s\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Origin: https://%(origin)s\r\n"
            "Sec-WebSocket-Key: %(randomstring)s\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "Sec-WebSocket-Protocol: DICENTIS_1_0\r\n"
            "\r\n"
        )

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{\s*\"meetingInfo\"\s*:\s*{.*?}\s*}', re.DOTALL), self.__MatchMeetingUpdate, 'Query')
            self.AddMatchString(re.compile(b'\"MeetingInfoChanged\"'), self.__MatchMeetingUpdate, 'Event')
            self.AddMatchString(re.compile(b'{\s*\"discussionList\"\s*:\s*\[.*?].*?}', re.DOTALL), self.__MatchMicrophoneState, 'Query')
            self.AddMatchString(re.compile(b'\"DiscussionListChanged\"'), self.__MatchMicrophoneState, 'Event')
            self.AddMatchString(re.compile(b'\"powerMode\"\s*:\s*\"powered(On|Off)\"'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'({\s*\"seats\"\s*:\s*\[.*?}\s*]\s*})', re.DOTALL), self.__MatchSeatInformation, None)
            self.AddMatchString(re.compile(b'{\s*\"votingInfo\"\s*:\s*{.*?}\s*}', re.DOTALL), self.__MatchVotingInfoUpdate, 'Query')
            self.AddMatchString(re.compile(b'\"VotingInfoChanged\"'), self.__MatchVotingInfoUpdate, 'Event')
            self.AddMatchString(re.compile(b'{\s*\"votingResults\"\s*:\s*\[.*?]\s*}', re.DOTALL), self.__MatchVotingResultUpdate, 'Query')
            self.AddMatchString(re.compile(b'\"VotingResultChanged\"'), self.__MatchVotingResultUpdate, 'Event')

            self.AddMatchString(re.compile(b'101 Switching Protocols\r|Please login first'), self.__MatchLoginHandShake, None)
            self.AddMatchString(re.compile(b'\"loggedIn\": (true|false)'), self.__MatchAuthenticated, None)
            self.AddMatchString(re.compile(b'{\s*\"operation\"\s*:\s*\"error\",:}'), self.__MatchError, None)

        self.initalFlag = {
            'MicrophoneState' : True
        }

        self.configuredMicrophoneStates = []

    @property
    def NumberofActiveMicrophones(self):
        return self._NumberofActiveMicrophones

    @NumberofActiveMicrophones.setter
    def NumberofActiveMicrophones(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofActiveMicrophones = int(value)
            self.microphone_directory_name = Directory('ActiveMicrophoneNameResults', self._NumberofActiveMicrophones, filler='')
            self.microphone_directory_name.write_status_function = self.WriteStatus

            self.microphone_directory_id = Directory('ActiveMicrophoneSeatIDResults', self._NumberofActiveMicrophones, filler='')
            self.microphone_directory_id.write_status_function = self.WriteStatus

            self.microphone_directory_part_id = Directory('ActiveMicrophoneParticipantIDResults', self._NumberofActiveMicrophones, filler='')
            self.microphone_directory_part_id.write_status_function = self.WriteStatus
        else:
            print('Number Of Active Microphones Parameter is outside of the range of allowable values.')

    def __MatchLoginHandShake(self, match, tag):

        self.Authenticated = True
        self.SetLogin( None, None)

    def SetLoginHandShake(self, value, qualifier):

        handshake = self._handshake % {'uri': self.uri, 'ipAddress': self.ipAddress, "origin": self.ipAddress, 'randomstring': self.generatestring()}
        self.Send(handshake)

    def __MatchAuthenticated(self, match, tag):
        if match.group(1).decode() == 'true':
            self.handshake_initialized = True
        else:
            self.handshake_initialized = False

    def SetLogin(self, value, qualifier):

        data = {
                "messageID": self.messageID,
                "operation": 'login',
                "parameters":
                    {
                        'user': self.deviceUsername,
                        'password': self.devicePassword
                    }
            }
        self.send_text(json.dumps(data))

    def SetActiveMicrophoneNavigation(self, value, qualifier):

        if value == 'Up':
            self.microphone_directory_name.scroll_up(1)
            self.microphone_directory_id.scroll_up(1)
            self.microphone_directory_part_id.scroll_up(1)
        elif value == 'Down':
            self.microphone_directory_name.scroll_down(1)
            self.microphone_directory_id.scroll_down(1)
            self.microphone_directory_part_id.scroll_down(1)
        elif value == 'Page Up':
            self.microphone_directory_name.scroll_up(self._NumberofActiveMicrophones)
            self.microphone_directory_id.scroll_up(self._NumberofActiveMicrophones)
            self.microphone_directory_part_id.scroll_up(self._NumberofActiveMicrophones)
        elif value == 'Page Down':
            self.microphone_directory_name.scroll_down(self._NumberofActiveMicrophones)
            self.microphone_directory_id.scroll_down(self._NumberofActiveMicrophones)
            self.microphone_directory_part_id.scroll_down(self._NumberofActiveMicrophones)
        else:
            self.Discard('Invalid Command for SetActiveMicrophoneNavigation')

    def SetActiveMicrophoneUpdate(self, value, qualifier):

        self.UpdateMicrophoneState(None, {})

    def SetMeetingUpdate(self, value, qualifier):

        data = {
            "messageID": self.messageID,
            "operation": "getMeetingInfo",
            "parameters": {}
        }
        MeetingUpdateCmdString = json.dumps(data)
        self.__SetHelper('MeetingUpdate', MeetingUpdateCmdString, value, qualifier)

    def __MatchMeetingUpdate(self, match, tag):

        if tag == 'Event':
            data = {
                "messageID": self.messageID,
                "operation": "getMeetingInfo",
                "parameters": {}
            }
            MeetingUpdateCmdString = json.dumps(data)
            self.__SetHelper('MeetingUpdate', MeetingUpdateCmdString, None, {}) # Use SetHelper to avoid error in log
        else:
            response = json.loads(match.group(0).decode())
            try:
                if response and response['meetingInfo']:
                    self.WriteStatus('MeetingTitle', response['meetingInfo']['title'], None)
                    self.WriteStatus('MeetingDescription', response['meetingInfo']['description'], None)
                    self.WriteStatus('MeetingStartDate', response['meetingInfo']['meetingStartDate'], None)
                    self.WriteStatus('MeetingEndDate', response['meetingInfo']['meetingEndDate'], None)
                    self.WriteStatus('MeetingState', response['meetingInfo']['state'], None)
            except(TypeError, KeyError, IndexError):
                    self.Error(['Meeting Update: Invalid/unexpected response'])

        # Re-register the event after every match
        # Events need to be registered everytime again after it is returned
        data = {
            "messageID": self.messageID,
            "operation": "RegisterEvents",
            "parameters": {
                "events": ["MeetingInfoChanged"]
            }
        }

        query = json.dumps(data)
        self.__SetHelper('MeetingUpdate', query, None, {})

    def SetMicrophoneState(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'AddSeatToSpeakers',
            'Off' : 'RemoveSeatFromDiscussionList',
        }

        if value in ValueStateValues and qualifier['Seat ID']:
            data = {
                "messageID" : self.messageID,
                "operation" : ValueStateValues[value],
                "parameters" : {
                    "seatId": qualifier['Seat ID']
                }
            }

            MicrophoneStateCmdString = json.dumps(data)
            self.__SetHelper('MicrophoneState', MicrophoneStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneState')

    def UpdateMicrophoneState(self, value, qualifier):

        if qualifier:

            if qualifier['Seat ID'] and qualifier['Seat ID'] not in self.configuredMicrophoneStates:
                self.configuredMicrophoneStates.append(qualifier['Seat ID'])

        data = {
            "messageID": self.messageID,
            "operation": "getDiscussionList",
            "parameters": {}
        }

        MicrophoneStateCmdString = json.dumps(data)
        self.__UpdateHelper('MicrophoneState', MicrophoneStateCmdString, value, qualifier)

    def __MatchMicrophoneState(self, match, tag):


        if tag == 'Event': # If a change is made to the microphone states (unsolicited), send Update to get list of microphones
            data = {
                "messageID": self.messageID,
                "operation": "getDiscussionList",
                "parameters": {}
            }

            self.__UpdateHelper('MicrophoneState', json.dumps(data), None, {})

        else: # List of microphones returned
            response = json.loads(match.group(0).decode())
            if response:
                activeMicDict = OrderedDict()

                if response['discussionList']:
                    for res in response['discussionList']:
                        tempList = [res['screenLine'], res['speakerType'], res['participantId']]
                        activeMicDict[res['seatId']] = tempList
                name_list = []
                id_list = []
                part_id_list = []
                for configuredID in self.configuredMicrophoneStates:
                    if configuredID in activeMicDict:
                        if activeMicDict[configuredID][1] == 'isSpeaker': # Write On for isSpeaker mics
                            self.WriteStatus('MicrophoneState', 'On', {'Seat ID' : configuredID})
                        else:
                            self.WriteStatus('MicrophoneState', 'Waiting', {'Seat ID': configuredID})
                    else:
                        self.WriteStatus('MicrophoneState', 'Off', {'Seat ID': configuredID})

                if activeMicDict:
                    for activeMic in activeMicDict:
                        if activeMicDict[activeMic][1] == 'isSpeaker':
                            name_list.append(activeMicDict[activeMic][0])
                            id_list.append(activeMic)
                            part_id_list.append(activeMicDict[activeMic][2])
                self._active_microphones['seatName'] = name_list.copy()
                name_list.append('*** End of Microphone Name ***')
                name_list.append('')
                self.microphone_directory_name.reset(name_list)

                self._active_microphones['seatID'] = id_list.copy()
                id_list.append('*** End of Seat ID ***')
                id_list.append('')
                self.microphone_directory_id.reset(id_list)

                self._active_microphones['participantId'] = part_id_list.copy()
                part_id_list.append('*** End of Participant ID ***')
                part_id_list.append('')
                self.microphone_directory_part_id.reset(part_id_list)

            data = {
                "messageID": self.messageID,
                "operation": "RegisterEvents",
                "parameters": {
                    "events": ["DiscussionListChanged"]
                }
            }

            query = json.dumps(data)
            self.__UpdateHelper('MicrophoneState', query, None, {})
            self.initalFlag['MicrophoneState'] = False

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'poweredOn',
            'Off': 'poweredOff'
        }

        if value in ValueStateValues:
            data = {
                "messageID": self.messageID,
                "operation": "setsystempowermode",
                "parameters": {
                    "powerMode": ValueStateValues[value]
                }
            }

            PowerCmdString = json.dumps(data)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):


        data = {
            "messageID": self.messageID,
            "operation": "getsystempowermode",
            "parameters": {}
        }

        PowerCmdString = json.dumps(data)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):


        value = match.group(1).decode()
        self.WriteStatus('Power', value, None)

    def UpdateSeatInformation(self, value, qualifier):

        if qualifier['Seat ID'] and qualifier['Type'] in ['Seat Name', 'Screen Line', 'Participant ID']:
            data = {
                "messageID"     : self.messageID,
                "operation"     : "getSeats",
                "parameters"    : {}
            }

            SeatInformationCmdString = json.dumps(data)
            self.__UpdateHelper('SeatInformation', SeatInformationCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateSeatInformation')

    def __MatchSeatInformation(self, match, tag):

        res = json.loads(match.group(1).decode())   
        if res:
            try:
                for index in res['seats']:
                    self.WriteStatus('SeatInformation',index['seatName'] if index['seatName'] else 'None', 
                                                {'Seat ID' : index['seatId'], 'Type' : 'Seat Name'})
                    self.WriteStatus('SeatInformation',index['screenLine'] if index['screenLine'] else 'None',
                                                    {'Seat ID': index['seatId'], 'Type': 'Screen Line'})
                    self.WriteStatus('SeatInformation',index['seatedParticipantId'] if index['seatedParticipantId'] else 'None',
                                                {'Seat ID': index['seatId'], 'Type': 'Participant ID'})
            except(TypeError, KeyError, IndexError):
                    self.Error(['Seat Information: Invalid/unexpected response'])

    def SetVotingInformationUpdate(self, value, qualifier):

        data = {
                "messageID": self.messageID,
                "operation": "getVotingInfo",
                "parameters": {}
        }

        VotingInformationUpdateCmdString = json.dumps(data)
        self.__SetHelper('VotingInformationUpdate', VotingInformationUpdateCmdString, value, qualifier)

    def __MatchVotingInfoUpdate(self, match, tag):

        if tag == 'Event':
            data = {
                "messageID": self.messageID,
                "operation": "getVotingInfo",
                "parameters": {}
            }

            VotingInformationUpdateCmdString = json.dumps(data)
            self.__SetHelper('VotingInformationUpdate', VotingInformationUpdateCmdString, None, {}) # Use SetHelper to avoid error in log
        else:
            response = json.loads(match.group(0).decode())
            try:
                if response and response['votingInfo']:
                    self.WriteStatus('VotingID', response['votingInfo']['votingId'], None)
                    self.WriteStatus('VotingReferenceNumber', response['votingInfo']['referenceNumber'], None)
                    self.WriteStatus('VotingSubject', response['votingInfo']['subject'], None)
                    self.WriteStatus('VotingDescription', response['votingInfo']['description'], None)
                    self.WriteStatus('VotingState', response['votingInfo']['state'], None)
                    self.WriteStatus('VotingAnswers', str(response['votingInfo']['votingAnswers']), None)
            except(TypeError, KeyError, IndexError):
                    self.Error(['Voting Information: Invalid/unexpected response'])

        # Re-register the event after every match
        # Events need to be registered everytime again after it is returned
        data = {
            "messageID": self.messageID,
            "operation": "RegisterEvents",
            "parameters": {
                "events": ["VotingInfoChanged"]
            }
        }

        query = json.dumps(data)
        self.__SetHelper('VotingInformationUpdate', query, None, {})

    def SetVotingResultUpdate(self, value, qualifier):

        data = {
                "messageID": self.messageID,
                "operation": "getVotingResults",
                "parameters": {}
        }

        VotingResultUpdateCmdString = json.dumps(data)
        self.__SetHelper('VotingResultUpdate', VotingResultUpdateCmdString, value, qualifier)

    def __MatchVotingResultUpdate(self, match, tag):

        if tag == 'Event':
            data = {
                "messageID": self.messageID,
                "operation": "getVotingResults",
                "parameters": {}
            }
            VotingResultUpdateCmdString = json.dumps(data)
            self.__SetHelper('VotingResultUpdate', VotingResultUpdateCmdString, None, {}) # Use SetHelper to avoid error in log
        else:
            try:
                response = json.loads(match.group(0).decode())
                if response and len(response['votingResults']) <= 4:
                    response['votingResults'].append({'count': '*** End of Voting Result Count ***', 'answer': '*** End of Voting Result Answer ***'})
                    i = 1
                    for val in response['votingResults']:
                        self.WriteStatus('VotingResultAnswer', val['answer'], {'Button': str(i)})
                        self.WriteStatus('VotingResultCount', val['count'], {'Button': str(i)})
                        i = i+1
                    while i < 5:
                        self.WriteStatus('VotingResultAnswer', '', {'Button': str(i)})
                        self.WriteStatus('VotingResultCount', '', {'Button': str(i)})
                        i = i+1
                else:
                    self.WriteStatus('VotingResultAnswer', '*** End of Voting Result Answer ***', {'Button': '1'})
                    self.WriteStatus('VotingResultCount', '*** End of Voting Result Count ***', {'Button': '1'})
                    for i in range(2, 5):
                        self.WriteStatus('VotingResultAnswer', '', {'Button': str(i)})
                        self.WriteStatus('VotingResultCount', '', {'Button': str(i)})
            except(TypeError, KeyError, IndexError):
                    self.Error(['Voting Result: Invalid/unexpected response'])

        # Re-register the event after every match
        # Events need to be registered everytime again after it is returned
        data = {
            "messageID": self.messageID,
            "operation": "RegisterEvents",
            "parameters": {
                "events": ["VotingResultChanged"]
            }
        }

        query = json.dumps(data)
        self.__SetHelper('VotingResultUpdate', query, None, {})

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        self.messageID += 1
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

            self.messageID += 1
            if self.handshake_initialized:
                self.send_text(commandstring)
            else:
                self.SetLoginHandShake(None, None)

    def __MatchError(self, match, tag):

        self.counter = 0

        value = match.group(0).decode().split(':')
        self.Error([value[1]])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        #self.SetLoginHandShake(None, None)

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.handshake_initialized = False
        self._active_microphones = {
            'seatName' : '',
            'seatID' : '',
            'participantId' : ''
        }

        self.configuredMicrophoneStates = []

        self.initalFlag = {
            'MicrophoneState': True
        }

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

    def ReceiveSocketData(self):
        return self._ReceiveSocketData

    def ReceiveSocketData(self, value):
        if callable(value):
            self._ReceiveSocketData = value

    def send_pong(self, message):
        self.send_text(message, PONG)

    def SendSocket(self, message):
        if self.Authenticated:
            self.send_text(message)
        else:
            handshake = self._handshake % {'uri': self.uri, 'ipAddress': self.ipAddress, "origin": self.ipAddress, 'randomstring': self.generatestring()}
            self.Send(handshake)

    def _get_masked(self, mask_key, message):
        s = self.mask(mask_key, message)
        return mask_key + s

    def send_text(self, message, masked=True, opcode=TEXT):

        if isinstance(message, bytes):
            message = self.try_decode_UTF8(message)  # this is slower but ensures we have UTF-8
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

    def read_bytes(self, num):
        tempt = self._receiveBuffer[:num]
        self._receiveBuffer = self._receiveBuffer[num:]
        return tempt[:num]

    def read_message(self, data):
        self._receiveBuffer = data
        try:
            b1, b2 = self.read_bytes(2)
        except ValueError as e:
            b1, b2 = 0, 0

        fin = b1 & FIN
        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN
        if masked:
            if payload_length == 126:
                payload_length = struct.unpack(">H", self.read_bytes(2))[0]
            elif payload_length == 127:
                payload_length = struct.unpack(">Q", self.read_bytes(8))[0]

            masks = self.read_bytes(4)

            decoded = ""
            for char in self.read_bytes(payload_length):
                char ^= masks[len(decoded) % 4]
                decoded += chr(char)

            if opcode == TEXT:
                if callable(self.ReceiveSocketData):
                    self.ReceiveSocketData(decoded)
            elif opcode == PING:
                self.send_text(decoded, PONG)
        else:
            if opcode == TEXT:
                if callable(self.ReceiveSocketData):
                    self.ReceiveSocketData(self._receiveBuffer)
            elif opcode == PING:
                self.send_text("", PONG)

    def authentication_check(self, hashdata):
        pass
            
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
        print('Incoming:', data)
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

        if platform == 'Pro' and version < minimumVersion:
            self.Error(['Minimum API version not met. Needs to be >= 3.4.6'])
        else:
            EthernetClientInterface.SSLWrap(self, certificate=None, cert_reqs='CERT_NONE', ssl_version='TLSv2', ca_certs= None)
            
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self, Hostname)
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
        
def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_module()
        return res

    return wrapper

class Directory:
    def __init__(self, write_function_name, display_count, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Position'
        self._qualifier_type = 'Enum'
        self._write_function_name = write_function_name
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

    def write_to_module(self):

        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Number':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            self.write_status_function(self._write_function_name, self.entry_function(entry[0]), {self.qualifier_name: position_value})

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
            self._start_index = len(self.entry_list) - 1  # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1