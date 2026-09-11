import time
import urllib.error
import urllib.request
from json import loads
import base64
import hashlib
import binascii
from struct import pack
from re import compile, search, findall

try:
    from Crypto.Hash import HMAC, SHA as SHA1
except ImportError:
    import hmac as HMAC
    try:
        from hashlib import sha1 as SHA1
    except ImportError:
        import sha as SHA1

_0xffffffffL = 0xffffffff
def isunicode(s):
    return isinstance(s, str)
def isbytes(s):
    return isinstance(s, bytes)
def isinteger(n):
    return isinstance(n, int)
def callable(obj):
    return hasattr(obj, '__call__')
def b(s):
    return s.encode("latin-1")
def binxor(a, b):
    return bytes([x ^ y for (x, y) in zip(a, b)])
from base64 import b64encode as _b64encode
def b64encode(data, chars="+/"):
    if isunicode(chars):
        return _b64encode(data, chars.encode('utf-8')).decode('utf-8')
    else:
        return _b64encode(data, chars)
from binascii import b2a_hex as _b2a_hex
def b2a_hex(s):
    return _b2a_hex(s).decode('us-ascii')
xrange = range

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if self.deviceUsername is not None and self.devicePassword is not None:
            authentication = base64.b64encode(self.deviceUsername.encode() + b':' + self.devicePassword.encode())
        else:
            self.authentication = None

        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.session = ''
        self.schedList = []
        self.ScheduledConferenceStartingEntry = 0

        self.PhonebookNameList = []
        self.PhonebookIDList = []

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'CallStatus': {'Parameters':['Call'], 'Status': {}},
            'CameraMove': {'Parameters':['Seconds'], 'Status': {}},
            'CameraSelect': { 'Status': {}},
            'DoNotDisturb': { 'Status': {}},
            'Hook': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'PCInputStatus': { 'Status': {}},
            'PhonebookDetailResult': {'Parameters':['Type'], 'Status': {}},
            'PhonebookNavigation': { 'Status': {}},
            'PhonebookResults': {'Parameters':['Entry'], 'Status': {}},
            'PhonebookResultsSet': {'Parameters':['Entry'], 'Status': {}},
            'PhonebookSearch': { 'Status': {}},
            'StatusCommand': { 'Status': {}},
            'ScheduledConferenceEndDate': {'Parameters':['Button'], 'Status': {}},
            'ScheduledConferenceEndTime': {'Parameters':['Button'], 'Status': {}},
            'ScheduledConferenceNavigation': { 'Status': {}},
            'ScheduledConferenceResult': {'Parameters':['Button'], 'Status': {}},
            'ScheduledConferenceSearch': { 'Status': {}},
            'ScheduledConferenceSet': { 'Status': {}},
            'ScheduledConferenceStartDate': {'Parameters':['Button'], 'Status': {}},
            'ScheduledConferenceStartTime': {'Parameters':['Button'], 'Status': {}},
            'ScheduledConferenceState': {'Parameters':['Button'], 'Status': {}},
            'SelfView': { 'Status': {}},
            'SharePC': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': {'Parameters':['Device'], 'Status': {}},
            }

        self.schedList = []

        self._NumberofScheduledConferenceSearch = 5
        self._NumberOfPhonebookEntries = 5
        self.directory = Directory(self._NumberOfPhonebookEntries, filler='')

        self.CallStatusStates = {
            0 : 'Inactive',
            1 : 'Dialing',
            2 : 'Waiting',
            3 : 'Ringing',
            4 : 'In Call',
            5 : 'On Hold',
            6 : 'Ended',
        }

        self.PCInputStatusStates = {
            0 : 'Disconnected',
            1 : 'Active',
            2 : 'Asleep',
            3 : 'Invalid Video Mode',
        }

        # Must be set to the correct write function in the driver
        self.directory.write_status_function = self.WriteStatus

    @property
    def NumberofScheduledConferenceSearch(self):
        return self._NumberofScheduledConferenceSearch

    @NumberofScheduledConferenceSearch.setter
    def NumberofScheduledConferenceSearch(self, value):
        self._NumberofScheduledConferenceSearch= int(value)

    @property
    def NumberOfPhonebookEntries(self):
        return self._NumberOfPhonebookEntries

    @NumberOfPhonebookEntries.setter
    def NumberOfPhonebookEntries(self, value):
        self._NumberOfPhonebookEntries= int(value)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 'on', 
            'Off' : 'off', 
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'ecapi/action?action=audio_mute&{0}'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', value, qualifier, url=AudioMuteCmdString)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):
        self.UpdateStatusCommand(None, None)

    def UpdateCallStatus(self, value, qualifier):
        self.UpdateStatusCommand(None, None)

    def SetCameraMove(self, value, qualifier):

        Duration = (1,2,3,4,5,6,7,8,9,10)

        ValueStateValues = {
            'Up' : 'up', 
            'Down' : 'down', 
            'Left' : 'left', 
            'Right' : 'right', 
            'Zoom In' : 'zoom-in', 
            'Zoom Out' : 'zoom-out'
        }

        Seconds = int(qualifier['Seconds'])
        if value in ValueStateValues and Seconds in Duration:
            CameraMoveCmdString = 'ecapi/action?action=camera_control&direction={0}&duration={1}'.format(ValueStateValues[value],Seconds * 1000)
            self.__SetHelper('CameraMove', value, qualifier, url=CameraMoveCmdString)
        else:
            self.Discard('Invalid Command for SetCameraMove')

    def SetCameraSelect(self, value, qualifier):

        CameraNumbers = ('0', '1', '2')

        if value in CameraNumbers:
            CameraSelectCmdString = 'ecapi/action?action=camera_select&index={0}'.format(value)
            self.__SetHelper('CameraSelect', value, qualifier, url=CameraSelectCmdString)
        else:
            self.Discard('Invalid Command for SetCameraSelect')

    def SetDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'On' : 'on', 
            'Off' : 'off', 
        }

        if value in ValueStateValues:
            DoNotDisturbCmdString = 'ecapi/action?action=do_not_disturb&{0}'.format(ValueStateValues[value])
            self.__SetHelper('DoNotDisturb', value, qualifier, url=DoNotDisturbCmdString)
        else:
            self.Discard('Invalid Command for SetDoNotDisturb')

    def UpdateDoNotDisturb(self, value, qualifier):
        self.UpdateStatusCommand(None, None)

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Answer' : 'answer', 
            'Reject' : 'reject', 
            'Ignore' : 'ignore',
            'Hang Up' : 'hangup',
            'Hold' : 'hold',
            'Resume' : 'resume',
            'Join Now'  : 'scheduled_conference',
            'Scheduled Conference' : 'scheduled_conference_ID'
        }

        if value == 'Dial':
            number = qualifier['Number']
            HookCmdString = 'ecapi/action?action=dial&number={0}'.format(number)
        elif 'Join Now' in value:
            HookCmdString = 'ecapi/action?action=dial&scheduled_conference'
        elif 'Scheduled Conference' in value:
            number = qualifier['Number']
            HookCmdString = 'ecapi/action?action=dial&scheduled_conference={0}'.format(number)
        else:
            HookCmdString = 'ecapi/action?action={0}'.format(ValueStateValues[value])

        if HookCmdString:
            self.__SetHelper('Hook', value, qualifier, url=HookCmdString)

    def UpdatePCInputStatus(self, value, qualifier):
        self.UpdateStatusCommand(None, None)

    def SetKeypad(self, value, qualifier):

        Digits = ('0','1','2','3','4','5','6','7','8','9','*','#')

        if value in Digits:
            KeypadCmdString = 'ecapi/action?action=keypad&digits=%{0:X}'.format(ord(value))
            self.__SetHelper('Keypad', value, qualifier, url=KeypadCmdString)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetPhonebookNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.directory.scroll_up(1)
        elif value == 'Down':
            self.directory.scroll_down(1)
        elif value == 'Page Up':
            self.directory.scroll_up(self._NumberOfPhonebookEntries)
        elif value == 'Page Down':
            self.directory.scroll_down(self._NumberOfPhonebookEntries)

    def SetPhonebookSearch(self, value, qualifier):
        self.Debug = True

        SearchName = qualifier['Search Name']
        if self.session and SearchName:
            PhonebookSearchCmdString = 'ecapi/contacts?type=global&search={}&start=0'.format(SearchName.replace(' ', '%20'))
            res = self.__UpdateHelper('PhonebookSearch', value, qualifier, url=PhonebookSearchCmdString)
            if res:
                try:
                    self.PhonebookNameList = []
                    self.PhonebookIDList = []
                    res = res.decode('iso-8859-1')
                    jsonout = loads(res)
                    TotalEntries = jsonout['total_entries']
                    
                    if TotalEntries > 20:
                        PhonebookSearchResults = jsonout['results']

                        LengthofPhonebookSearchResults = len(PhonebookSearchResults)

                        for i in range(0, LengthofPhonebookSearchResults):
                            self.PhonebookNameList.append(PhonebookSearchResults[i]['display_name'])
                            self.PhonebookIDList.append(PhonebookSearchResults[i]['id'])

                        TotalPollingTimes = int(TotalEntries / 20)
                        if TotalEntries % 20 == 0:
                            TotalPollingTimes = TotalPollingTimes - 1
                            
                        for j in range(1, TotalPollingTimes + 1):
                            PhonebookSearchCmdString = 'ecapi/contacts?type=global&search={}&start={}'.format(SearchName.replace(' ', '%20'), j * 20)
                            res = self.__UpdateHelper('PhonebookSearch', value, qualifier, url=PhonebookSearchCmdString)
                            if res:
                                res = res.decode('iso-8859-1')
                                jsonout = loads(res)
                                PhonebookSearchResults = jsonout['results']
                                LengthofPhonebookSearchResults = len(PhonebookSearchResults)
                                for i in range(0, LengthofPhonebookSearchResults):
                                    self.PhonebookNameList.append(PhonebookSearchResults[i]['display_name'])
                                    self.PhonebookIDList.append(PhonebookSearchResults[i]['id'])

                        new_phonebook_data = ['{}'.format(entry[0]) for entry in zip(self.PhonebookNameList)]
                        new_phonebook_data.append('*** End of List ***')

                    else:
                        PhonebookSearchResults = jsonout['results']
                        LengthofPhonebookSearchResults = TotalEntries
                        for i in range(0, LengthofPhonebookSearchResults):
                            self.PhonebookNameList.append(PhonebookSearchResults[i]['display_name'])
                            self.PhonebookIDList.append(PhonebookSearchResults[i]['id'])
                        new_phonebook_data = ['{0}'.format(entry[0]) for entry in zip(self.PhonebookNameList)]
                        new_phonebook_data.append('*** End of List ***')
                    self.directory.reset(new_phonebook_data)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Phonebook Search: Invalid/unexpected response'])

    def SetPhonebookResultsSet(self, value, qualifier):
        self.Debug = True

        entry = qualifier['Entry']
        Email = 'N/A'
        WorkNum = 'N/A'
        Mobile = 'N/A'
        ID = None
        if 1 <= entry <= self._NumberOfPhonebookEntries:
            phonebook_entry = self.ReadStatus('PhonebookResults', {'Entry': entry})
            if phonebook_entry and phonebook_entry != '*** End of List ***':
                name = phonebook_entry.replace(' ', '%20')
                for i in range(0, len(self.PhonebookNameList)):
                    if self.PhonebookNameList[i] == phonebook_entry:
                        ID = self.PhonebookIDList[i]
                if ID:
                    PhonebookResultsSetCmdString = 'ecapi/contacts?type=global&search={}&detail&contactid={}'.format(name,ID)
                    res = self.__UpdateHelper('PhonebookResultsSet', value, qualifier, url=PhonebookResultsSetCmdString)
                    if res:
                        res = res.decode('iso-8859-1')
                        jsonout = loads(res)
                        Numbers = jsonout['results'][0]['numbers']
                        for i in range(0, len(Numbers)):
                            if Numbers[i]['type'] == 1:
                                Email = Numbers[i]['number']
                            elif Numbers[i]['type'] == 4:
                                WorkNum = Numbers[i]['number']
                            elif Numbers[i]['type'] == 3:
                                Mobile = Numbers[i]['number']
                        self.WriteStatus('PhonebookDetailResult', Email, {'Type': 'Email'})
                        self.WriteStatus('PhonebookDetailResult', WorkNum, {'Type': 'Work'})
                        self.WriteStatus('PhonebookDetailResult', Mobile, {'Type': 'Mobile'})

    def UpdateStatusCommand(self, value, qualifier):

        SelfViewValues = {
            0: 'Auto',
            1: 'Off',
            2: 'On'
        }
        try:
            if not self.session:
                StatusCommandCmdString = 'ecapi/auth'
                res = self.__UpdateHelper('StatusCommand', value, qualifier, url=StatusCommandCmdString)
                if res:
                    jsonout = loads(res.decode())
                    if not jsonout['authenticated']:
                        key = PBKDF2(passphrase=self.devicePassword,salt=binascii.unhexlify(jsonout['salt']),iterations=jsonout['iterations'],digestmodule=hashlib.sha256, macmodule=HMAC)
                        key_hex = key.hexread(32)
                        key_bytes = binascii.unhexlify(key_hex)
                        challenge = jsonout['challenge']
                        hash_ = HMAC.new(key_bytes, bytes(challenge,'ascii'), hashlib.sha256)
                        StatusCommandCmdString = 'ecapi/auth?challenge=' + challenge + '&response=' + hash_.hexdigest()
                        res = self.__UpdateHelper('StatusCommand', value, qualifier, url=StatusCommandCmdString)
                        if not res:
                            raise Exception
                        jsonout = loads(res.decode())

                    self.session = '='.join(['&session',jsonout['session']])
                else:
                    raise Exception
                    
            StatusCommandCmdString = 'ecapi/state?filter=endpoint,calls,audio,video'
            res = self.__UpdateHelper('StatusCommand', value, qualifier, url=StatusCommandCmdString)
            if res:
                jsonout = loads(res.decode())
                self.WriteStatus('DoNotDisturb', {True: 'On', False: 'Off'}[jsonout['endpoint']['dnd']], None)
                for a in range(1,17):
                    try:
                        self.WriteStatus('CallStatus', self.CallStatusStates[jsonout['calls']['list'][a-1]['state']], {'Call' : str(a)})
                    except:
                        self.WriteStatus('CallStatus', 'Inactive', {'Call' : str(a)})
                self.WriteStatus('AudioMute', {True: 'On', False: 'Off'}[jsonout['audio']['mute']], None)
                self.WriteStatus('Volume', jsonout['audio']['incall_volume'], {'Device' : 'In Call'})
                self.WriteStatus('Volume', jsonout['audio']['ringer_volume'], {'Device' : 'Ringer'})
                self.WriteStatus('VideoMute', {True: 'On', False: 'Off'}[jsonout['video']['mute']], None)
                self.WriteStatus('SelfView', SelfViewValues[jsonout['video']['self_view']], None)
                self.WriteStatus('PCInputStatus', self.PCInputStatusStates[jsonout['video']['pc_status']], None)
        except:
            self.Error(['Invalid/unexpected response'])

    def SetScheduledConferenceNavigation(self, value, qualifier):
        self.Debug = True
        
        ValueStateValues = {
            1 : 'Created',
            2 : 'Starts Soon', 
            3 : 'Started', 
            4 : 'Ongoing'
        }

        if 'Page Up' == value:
            self.ScheduledConferenceStartingEntry -= self._NumberofScheduledConferenceSearch
        elif 'Page Down' == value:
            self.ScheduledConferenceStartingEntry += self._NumberofScheduledConferenceSearch

        if self.ScheduledConferenceStartingEntry >= len(self.schedList):
            self.ScheduledConferenceStartingEntry = len(self.schedList) - 1

        if self.ScheduledConferenceStartingEntry < 0:
            self.ScheduledConferenceStartingEntry = 0

        Button = 1
        for index in self.schedList[self.ScheduledConferenceStartingEntry:]:
            self.WriteStatus('ScheduledConferenceState', ValueStateValues[index['state']], {'Button' : Button})
            self.WriteStatus('ScheduledConferenceResult', index['name'], {'Button' : Button})
            self.WriteStatus('ScheduledConferenceStartDate', time.strftime('%d/%m/%Y', time.localtime(int(index['start_time']))), {'Button' : Button})
            self.WriteStatus('ScheduledConferenceStartTime', time.strftime('%H:%M', time.localtime(int(index['start_time']))), {'Button' : Button})
            self.WriteStatus('ScheduledConferenceEndDate', time.strftime('%d/%m/%Y', time.localtime(int(index['end_time']))), {'Button' : Button})
            self.WriteStatus('ScheduledConferenceEndTime', time.strftime('%H:%M', time.localtime(int(index['end_time']))), {'Button' : Button})
            Button += 1
            if Button == self._NumberofScheduledConferenceSearch+1: break
        for index in range(Button,self._NumberofScheduledConferenceSearch+1):
            self.WriteStatus('ScheduledConferenceState', '<empty>', {'Button' : index})
            self.WriteStatus('ScheduledConferenceResult', '<empty>', {'Button' : index})
            self.WriteStatus('ScheduledConferenceStartDate', '<empty>', {'Button' : index})
            self.WriteStatus('ScheduledConferenceStartTime', '<empty>', {'Button' : index})
            self.WriteStatus('ScheduledConferenceEndDate', '<empty>', {'Button' : index})
            self.WriteStatus('ScheduledConferenceEndTime', '<empty>', {'Button' : index})

    def SetScheduledConferenceSearch(self, value, qualifier):

        if self.session:
            ScheduledConferenceSearchCmdString = 'ecapi/state?filter=scheduled_conferences'
            res = self.__UpdateHelper('ScheduledConferenceSearch', value, qualifier, url=ScheduledConferenceSearchCmdString)
            if res:
                try:
                    res = res.decode('iso-8859-1')
                    jsonout = loads(res)
                    self.schedList = jsonout['scheduled_conferences']['list']
                    self.ScheduledConferenceStartingEntry = 0
                    self.SetScheduledConferenceNavigation(None,None)
                    
                except (KeyError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for SetScheduledConferenceSearch')
            
    def SetScheduledConferenceSet(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 15
        }
        
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
            self.ScheduledConferenceStartingEntry+value <= len(self.schedList)):
            try:
                value = self.schedList[self.ScheduledConferenceStartingEntry+value-1]['id']
                self.Set('Hook', 'Scheduled Conference', {'Number': value})
            except (KeyError, IndexError):
                self.Discard('Invalid Command')
            
    def SetSelfView(self, value, qualifier):

        ValueStateValues = {
            'Auto' : 'auto',
            'On'   : 'on',
            'Off'  : 'off'
        }

        SelfViewCmdString = 'ecapi/action?action=self_view&{}'.format(ValueStateValues[value])
        self.__SetHelper('SelfView', value, qualifier, url=SelfViewCmdString)

    def UpdateSelfView(self, value, qualifier):
        self.UpdateStatusCommand(None, None)

    def SetSharePC(self, value, qualifier):

        ValueStateValues = {
            'On' : 'on', 
            'Off' : 'off', 
        }

        if value in ValueStateValues:
            SharePCCmdString = 'ecapi/action?action=share_pc&{0}'.format(ValueStateValues[value])
            self.__SetHelper('SharePC', value, qualifier, url=SharePCCmdString)
        else:
            self.Discard('Invalid Command for SetSharePC')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 'on', 
            'Off' : 'off', 
        }

        if value in ValueStateValues:
            VideoMuteCmdString = 'ecapi/action?action=video_mute&{0}'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', value, qualifier, url=VideoMuteCmdString)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):
        self.UpdateStatusCommand(None, None)

    def SetVolume(self, value, qualifier):

        DeviceStates = {
            'Ringer' : 'ringer', 
            'In Call' : 'incall'
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 10
            }

        Device = qualifier['Device']
        if Device in DeviceStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'ecapi/action?action=volume&device={0}&absolute={1}'.format(DeviceStates[Device],value)
            self.__SetHelper('Volume', value, qualifier, url=VolumeCmdString)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.UpdateStatusCommand(None, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        my_request = urllib.request.Request('{}{}{}'.format(self.RootURL, url, self.session), data=data, headers={'Content-Type' : 'text/html'})

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        my_request = urllib.request.Request('{}{}{}'.format(self.RootURL, url, self.session), data=data, headers={'Content-Type' : 'text/html'})

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
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
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)

        return res

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.session = ''
        self.schedList = []
        self.ScheduledConferenceStartingEntry = 0

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
            print(command, 'does not exist in the module')

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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
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


class PBKDF2(object):

    def __init__(self, passphrase, salt, iterations=1000, digestmodule=SHA1, macmodule=HMAC):
        self.__macmodule = macmodule
        self.__digestmodule = digestmodule
        self._setup(passphrase, salt, iterations, self._pseudorandom)

    def _pseudorandom(self, key, msg):

        return self.__macmodule.new(key=key, msg=msg,
            digestmod=self.__digestmodule).digest()

    def read(self, bytes):

        if self.closed:
            raise ValueError("file-like object is closed")

        size = len(self.__buf)
        blocks = [self.__buf]
        i = self.__blockNum
        while size < bytes:
            i += 1
            if i > _0xffffffffL or i < 1:
                raise OverflowError("derived key too long")
            block = self.__f(i)
            blocks.append(block)
            size += len(block)
        buf = b("").join(blocks)
        retval = buf[:bytes]
        self.__buf = buf[bytes:]
        self.__blockNum = i
        return retval

    def __f(self, i):
        assert 1 <= i <= _0xffffffffL
        U = self.__prf(self.__passphrase, self.__salt + pack("!L", i))
        result = U
        for j in xrange(2, 1+self.__iterations):
            U = self.__prf(self.__passphrase, U)
            result = binxor(result, U)
        return result

    def hexread(self, octets):

        return b2a_hex(self.read(octets))

    def _setup(self, passphrase, salt, iterations, prf):

        if isunicode(passphrase):
            passphrase = passphrase.encode("UTF-8")
        elif not isbytes(passphrase):
            raise TypeError("passphrase must be str or unicode")
        if isunicode(salt):
            salt = salt.encode("UTF-8")
        elif not isbytes(salt):
            raise TypeError("salt must be str or unicode")
        if not isinteger(iterations):
            raise TypeError("iterations must be an integer")
        if iterations < 1:
            raise ValueError("iterations must be at least 1")
        if not callable(prf):
            raise TypeError("prf must be callable")

        self.__passphrase = passphrase
        self.__salt = salt
        self.__iterations = iterations
        self.__prf = prf
        self.__blockNum = 0
        self.__buf = b("")
        self.closed = False

    def close(self):

        if not self.closed:
            del self.__passphrase
            del self.__salt
            del self.__iterations
            del self.__prf
            del self.__blockNum
            del self.__buf
            self.closed = True

def crypt(word, salt=None, iterations=None):

    if salt is None:
        salt = _makesalt()
    if isunicode(salt):
        salt = salt.encode('us-ascii').decode('us-ascii')
    elif isbytes(salt):
        salt = salt.decode('us-ascii')
    else:
        raise TypeError("salt must be a string")
    if isunicode(word):
        word = word.encode("UTF-8")
    elif not isbytes(word):
        raise TypeError("word must be a string or unicode")
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

    binarysalt = b("").join([pack("@H", randint(0, 0xffff)) for i in range(3)])
    return b64encode(binarysalt, "./")

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
        self.qualifier_name = 'Entry'

        # type of the 'Position' qualifier in Driver Studio. Either Enum or Number
        self._qualifier_type = 'Number'

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
            self.write_status_function('PhonebookResults', self.entry_function(entry[0]), {self.qualifier_name: position_value})
            
    def write_status_function(self, command, value, qualifier):
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
