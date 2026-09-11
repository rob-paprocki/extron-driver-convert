import base64
from json import loads, dumps
import urllib.error
import urllib.request
from extronlib.system import GetUnverifiedContext, ProgramLog
import time

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3 
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.num_of_phone_book_search = 5
        self.IPAddress = ipAddress
        self.port = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        
        if SSLVerifyMode == 'On':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        if self.port == 443: 
            self.RootURL = 'https://{0}:{1}'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                      urllib.request.HTTPSHandler(context=self._context))
        else: 
            self.RootURL = 'http://{0}:{1}'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        urllib.request.install_opener(self.Opener)
        
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioInput': {'Status': {}},
            'CallStatus': {'Status': {}},
            'CallTypeStatus': {'Status': {}},
            'CameraControl': {'Parameters': ['Camera'], 'Status': {}},
            'CameraPresetControl': {'Parameters': ['Camera', 'Action'], 'Status': {}},
            'ConferenceStatus': {'Status': {}},
            'ConferenceTypeStatus': {'Status': {}},
            'DialString': {'Status': {}},
            'InputGainStatus': {'Parameters': ['Type'], 'Status': {}},
            'InputMuteStatus': {'Parameters': ['Type'], 'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchResultSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'PhoneHook': {'Parameters': ['Call Type', 'H235 Policy'], 'Status': {}},
            'PointtoPointCall': {'Parameters': ['Number'], 'Status': {}},
            'Power': {'Status': {}},
            'Presentation': {'Status': {}},
            'RemoteMicrophoneStatus': {'Status': {}},
            'SessionID': {'Status': {}},
            'SpeakerStatus': {'Status': {}},
            'SpeakerVolume': {'Status': {}},
        }

        self.SessionID = None
        self.acCSRFToken = None
        self.lastAudioInputUpdate = 0
        self.SessionFlag = False
        self.AuthenticationFlag = False
        self.PhoneBookList = {}
        self.Advance = True
        self.StartingEntry = 1
        self.EndEntry = 0
        self.addList = []
    

    @property
    def NumberOfPhonebookSearch(self):
        return self.num_of_phone_book_search

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        num_of_phone_book_search = int(value)
        if 1 <= num_of_phone_book_search <= 10:
            self.num_of_phone_book_search = num_of_phone_book_search

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Mute all': 'Close',
            'Unmute all': 'Open',
        }

        if value in ValueStateValues:
            AudioInputCmdString = 'action.cgi?ActionID=WEB_{}MicAPI'.format(ValueStateValues[value])
            data = dumps({"acCSRFToken": self.acCSRFToken})
            self.__SetHelper('AudioInput', value, qualifier, url=AudioInputCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetAudioInput')

    def UpdateAudioInput(self, value, qualifier):

        AudioInputStateValues = {
            0: 'Mute all',
            1: 'Unmute all',
        }

        MuteStateValues = {
            0: 'On',
            1: 'Off',
        }

        SpeakerStatusStateValues = {
            0: 'Disable',
            1: 'Unmute',
        }
        
        AudioInputCmdString = 'action.cgi?ActionID=WEB_InitAudioCtrlParamsAPI'
        data = dumps({"acCSRFToken": self.acCSRFToken})
        res = self.__UpdateHelper('AudioInput', value, qualifier, url=AudioInputCmdString, data=data)
        if res and res['success'] == 1:
            temp = loads(res['data'])
            try:
                value = AudioInputStateValues[temp['MicSwitch']]
                self.WriteStatus('AudioInput', value, {})
            except (KeyError, IndexError):
                self.Error(['Audio Input: Invalid/unexpected response'])
            try:
                value = MuteStateValues[temp['mic1']]
                self.WriteStatus('InputMuteStatus', value, {'Type': 'XLR'})
            except (KeyError, IndexError):
                self.Error(['Input Mute Status: Invalid/unexpected response'])
            try:
                value = int(temp['mic1Value']) - 12
                self.WriteStatus('InputGainStatus', value, {'Type': 'XLR'})
            except (ValueError, IndexError):
                self.Error(['Input Gain Status: Invalid/unexpected response'])

            for input_num in ('1', '2'):
                for side_value in ('L', 'R'):
                    qualifier = {'Type': 'HDMI {} {}'.format(input_num, side_value)}
                    try:
                        value = MuteStateValues[temp['hdmi{}{}In'.format(input_num, side_value)]]
                        self.WriteStatus('InputMuteStatus', value, qualifier)
                    except (KeyError, IndexError):
                        self.Error(['Input Mute Status: Invalid/unexpected response'])
                    try:
                        value = int(temp['hdmi{}{}InValue'.format(input_num, side_value)]) - 12
                        self.WriteStatus('InputGainStatus', value, qualifier)
                    except (ValueError, IndexError):
                        self.Error(['Input Gain Status: Invalid/unexpected response'])

            for side_value in ('L', 'R'):
                qualifier = {'Type': 'RCA {}'.format(side_value)}
                try:
                    value = MuteStateValues[temp['rca{}In'.format(side_value)]]
                    self.WriteStatus('InputMuteStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input Mute Status: Invalid/unexpected response'])
                try:
                    value = int(temp['rca{}InValue'.format(side_value)]) - 12
                    self.WriteStatus('InputGainStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Input Gain Status: Invalid/unexpected response'])

            for array_num in ('1', '2'):
                qualifier = {'Type': 'Microphone Array {}'.format(array_num)}
                try:
                    value = int(temp['micArray{}_01Value'.format(array_num)]) - 12
                    self.WriteStatus('InputGainStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Input Gain Status: Invalid/unexpected response'])
            try:
                value = SpeakerStatusStateValues[temp['SpeakerSwitch']]
                self.WriteStatus('SpeakerStatus', value, {})
            except (KeyError, IndexError):
                self.Error(['Speaker Status: Invalid/unexpected response'])
            try:
                value = int(temp['speakerValue'])
                self.WriteStatus('SpeakerVolume', value, {})
            except (ValueError, IndexError):
                self.Error(['Speaker Volume: Invalid/unexpected response'])

    def SetCameraControl(self, value, qualifier):

        CameraStates = {
            'Local': 'localCam',
            'Remote': 'remoteCam',
        }

        ValueStateValues = {
            'Start moving to the right': 0,
            'Start moving to the left': 1,
            'Start tilting upward': 2,
            'Start tilting downward': 3,
            'Start zooming in': 4,
            'Start zooming out': 5,
            'Start focusing in': 6,
            'Start focusing out': 7,
            'Stop moving to the right': 8,
            'Stop moving to the left': 9,
            'Stop tilting upward': 10,
            'Stop tilting downward': 11,
            'Stop zooming in': 12,
            'Stop zooming out': 13,
            'Stop focusing in': 14,
            'Stop focusing out': 15,
            'Move to the home position': 16,
            'Autofocus': 17,
        }

        cam_type = qualifier['Camera']
        if cam_type in CameraStates and value in ValueStateValues:
            CameraControlCmdString = 'action.cgi?ActionID=WEB_CtrlCameraOpeateAPI'
            data = dumps({"camState": CameraStates[cam_type], "camAction": ValueStateValues[value], "camPos": 255,
                          "camSrc": 0, "acCSRFToken": self.acCSRFToken})
            self.__SetHelper('CameraControl', value, qualifier, url=CameraControlCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetCameraControl')

    def SetCameraPresetControl(self, value, qualifier):

        CameraStates = {
            'Local': 'localCam',
            'Remote': 'remoteCam',
        }

        ActionStates = {
            'Save': 18,
            'Activate': 19,
            'Clear': 20,
        }

        cam_type = qualifier['Camera']
        act_type = qualifier['Action']
        if cam_type in CameraStates and act_type in ActionStates and 1 <= int(value) <= 30:
            CameraPresetControlCmdString = 'action.cgi?ActionID=WEB_CtrlCameraOpeateAPI'
            data = dumps({"camState": CameraStates[cam_type], "camAction": ActionStates[act_type], "camPos": int(value),
                          "camSrc": 0, "acCSRFToken": self.acCSRFToken})
            self.__SetHelper('CameraPresetControl', value, qualifier, url=CameraPresetControlCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetCameraPresetControl')

    def SetDialString(self, value, qualifier):

        self.set_entry = value

    def UpdateInputGainStatus(self, value, qualifier):

        TypeStates = ('XLR', 'HDMI 1 L', 'HDMI 1 R', 'HDMI 2 L', 'HDMI 2 R', 'RCA L', 'RCA R',
                      'Microphone Array 1', 'Microphone Array 2')

        type_qualifier = qualifier['Type']
        if type_qualifier in TypeStates:
            self.UpdateAudioInput(None, None)
        else:
            self.Discard('Invalid Command for UpdateInputGainStatus')

    def UpdateInputMuteStatus(self, value, qualifier):

        TypeStates = ('XLR', 'HDMI 1 L', 'HDMI 1 R', 'HDMI 2 L', 'HDMI 2 R', 'RCA L', 'RCA R')

        type_qualifier = qualifier['Type']
        if type_qualifier in TypeStates:
            self.UpdateAudioInput(None, None)
        else:
            self.Discard('Invalid Command for UpdateInputMuteStatus')

    def SetPhonebookNavigation(self, value, qualifier):

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if value == 'Up':
                self.StartingEntry -= 1
            elif value == 'Down':
                if self.Advance:
                    self.StartingEntry += 1
            elif value == 'Page Up':
                self.StartingEntry -= self.num_of_phone_book_search
            elif value == 'Page Down':
                if self.Advance:
                    self.StartingEntry += self.num_of_phone_book_search

            if self.StartingEntry < 1:
                self.StartingEntry = 1

            self.EndEntry = self.StartingEntry + self.num_of_phone_book_search - 1

            number_of_names = len(self.addList)
            index = self.StartingEntry - 1
            button = 1
            self.Advance = True
            while index < number_of_names and index < self.EndEntry:
                self.WriteStatus('PhonebookSearchResult', self.addList[index], {'Button': button})
                button += 1
                index += 1

            if button <= self.num_of_phone_book_search:
                self.Advance = False
                self.WriteStatus('PhonebookSearchResult', '*** End of list ***', {'Button': button})
                button += 1
                for idx in range(button, int(self.num_of_phone_book_search) + 1):
                    self.WriteStatus('PhonebookSearchResult', '', {'Button': idx})
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookSearchResultSet(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': self.num_of_phone_book_search,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            set_entry = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if set_entry not in ['*** Not Available ***', '*** End of list ***']:
                self.set_entry = set_entry
        else:
            self.Discard('Invalid Command for SetPhonebookSearchResultSet')

    def SetPhonebookUpdate(self, value, qualifier):

        search_string = value
        param = '' if not search_string else search_string
        if self.SessionFlag and self.AuthenticationFlag:
            PhonebookUpdateCmdString = 'action.cgi?ActionID=WEB_SeachLdapAddrAPI'
            data = dumps({"szKeyWords": param, "acCSRFToken": self.acCSRFToken})
            self.__SetHelper('PhonebookUpdate', value, qualifier, url=PhonebookUpdateCmdString, data=data)
            prev_time = time.monotonic()
            ctime = time.monotonic()
            while True:
                if ctime - prev_time > 3:
                    break
                else:
                    ctime = time.monotonic()

            PhonebookUpdateCmdString = 'action.cgi?ActionID=WEB_GetLdapAddrResultListAPI'
            data = dumps({"acCSRFToken": self.acCSRFToken})
            res = self.__UpdateHelper('PhonebookUpdate', value, qualifier, url=PhonebookUpdateCmdString, data=data)
            if res:
                try:
                    self.PhoneBookList = {}
                    self.addList, ldap_list = [], loads(res['data'])['LdapList']
                    button = 1
                    for item in ldap_list:
                        self.addList.append(item['site'])
                        self.PhoneBookList[item['site']] = item['sipNum']
                        self.WriteStatus('PhonebookSearchResult', item['site'], {'Button': button})
                        button += 1
                    if button <= self.num_of_phone_book_search:
                        self.WriteStatus('PhonebookSearchResult', '*** End of list ***', {'Button': button})
                        button += 1
                        for idx in range(button, self.num_of_phone_book_search + 1):
                            self.WriteStatus('PhonebookSearchResult', '', {'Button': idx})
                except (KeyError, IndexError):
                    self.Error(['Phonebook Update: Invalid/unexpected response'])
            else:
                button = 1
                self.Advance = False
                self.WriteStatus('PhonebookSearchResult', '*** Not Available ***', {'Button': button})
                button = button + 1
                for idx in range(button, int(self.num_of_phone_book_search) + 1):
                    self.WriteStatus('PhonebookSearchResult', '', {'Button': idx})

    def SetPhoneHook(self, value, qualifier):

        ValueStateValues = {
            'Make Point to Point Call Site': 'WEB_CallNumberAPI',
            'Cancel':                        'WEB_CancelCallAPI',
            'Answer':                        'WEB_IncomingCallProcAPI',
            'Reject':                        'WEB_IncomingCallProcAPI',
            'Hangup':                        'WEB_HangupCallAPI',
        }
        
        if value in ValueStateValues:
            PhoneHookCmdString = 'action.cgi?ActionID={}'.format(ValueStateValues[value])
            data = None
            if value in ['Hangup', 'Cancel']:
                data = dumps({"ucSiteHandle": 1, "acCSRFToken": self.acCSRFToken})
            elif value == 'Answer':
                data = dumps({"ucValue": 1, "ucMediaType": 0, "ucSiteHandle": 1, "acCSRFToken": self.acCSRFToken})
            elif value == 'Reject':
                data = dumps({"ucValue": 0, "ucMediaType": 0, "ucSiteHandle": 1, "acCSRFToken": self.acCSRFToken})
            elif self.set_entry:
                data = dumps({"szNumber": self.set_entry, "acCSRFToken": self.acCSRFToken})
            else:
                return self.Discard('Invalid Command for SetPhoneHook')
            
            if data:
                self.__SetHelper('PhoneHook', value, qualifier, url=PhoneHookCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPhoneHook')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'WEB_SystemWakeUpAPI',
            'Off': 'WEB_StartTermSleepAPI',
        }

        if value in ValueStateValues:
            PowerCmdString = 'action.cgi?ActionID={}'.format(ValueStateValues[value])
            data = dumps({"acCSRFToken": self.acCSRFToken})
            self.__SetHelper('Power', value, qualifier, url=PowerCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'unsleep': 'On',
            'sleep': 'Off',
        }

        PowerCmdString = 'action.cgi?ActionID=WEB_IsSystemSleepAPI'
        data = dumps({"acCSRFToken": self.acCSRFToken})
        if self.SessionFlag and self.AuthenticationFlag:
            res = self.__UpdateHelper('Power', value, qualifier, url=PowerCmdString, data=data)
            if res:
                try:
                    temp = loads(res['data'])
                    value = ValueStateValues[temp['isSystemSleep']]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])

    def SetPresentation(self, value, qualifier):

        ValueStateValues = {
            'Start': 'WEB_StartSendAuxStreamAPI',
            'Stop': 'WEB_StopSendAuxStreamAPI',
        }

        if value in ValueStateValues:
            PresentationCmdString = 'action.cgi?ActionID={}'.format(ValueStateValues[value])
            data = dumps({"acCSRFToken": self.acCSRFToken})
            self.__SetHelper('Presentation', value, qualifier, url=PresentationCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPresentation')

    def UpdateRequiredPolling(self, value, qualifier):

        if not self.AuthenticationFlag:
            RequiredPollingCmdString = 'action.cgi?ActionID=WEB_RequestCertificateAPI'
            data = dumps({"user": self.deviceUsername, "password": self.devicePassword})
            res = self.__UpdateHelper('RequiredPolling', value, qualifier, url=RequiredPollingCmdString, data=data)
            if res:
                if res['success'] == 1:
                    self.AuthenticationFlag = True
                    self.acCSRFToken = (loads(res['data']))['acCSRFToken']
                elif res['success'] == 0:
                    self.AuthenticationFlag = False
                    self.UpdateSessionID( None, None)

        elif self.AuthenticationFlag:
                                                            
            CallStatusValues = {
                0: 'No Call',
                1: 'Calling',
                2: 'Disconnected',
            }

            CallTypeStatusValues = {
                0: 'ISDN call',
                1: 'V.35 call',
                2: 'E1 call',
                3: 'H.323 (IP) call',
                4: 'Phone call (audio only)',
                5: 'PSTN call (narrow band)',
                6: 'T1 call',
                7: '4E1 call',
                8: 'SIP (IP) call',
                9: 'SIP (phone) call',
                10: 'Automatic switch between call types',
            }

            ConferenceStatusValues = {
                0: 'Idle',
                1: 'Making a call',
                2: 'Answering a call',
                3: 'Rejecting a call',
                4: 'SiteCall',
                5: 'Scheduled call',
                6: 'Querying schedule',
                7: 'Deleting schedule',
            }

            ConferenceTypeStatusValues = {
                0: 'No call',
                1: 'Point-to-point call',
                2: 'Remote multipoint conference',
                3: 'Local multipoint conference',
                4: 'Cascaded conference',
            }

            RemoteMicrophoneStatusValues = {
                0: 'Unmuted',
                1: 'Muted',
            }
            RequiredPollingCmdString = 'action.cgi?ActionID=WEB_GetMailboxDataAPI'
            data = dumps({"acCSRFToken": self.acCSRFToken})
            res = self.__UpdateHelper('RequiredPolling', value, qualifier, url=RequiredPollingCmdString, data=data)
            if res:
                try:
                    if res['success'] == 1:
                        self.AuthenticationFlag = True
                        temp = loads(res['data'])['state']
                        try:
                            value = CallStatusValues[temp['callstate']]
                            self.WriteStatus('CallStatus', value, {})
                        except (KeyError, IndexError):
                            self.Error(['Call Status: Invalid/unexpected response'])
                        try:
                            value = CallTypeStatusValues[temp['calltype']]
                            self.WriteStatus('CallTypeStatus', value, {})
                        except (KeyError, IndexError):
                            self.Error(['Call Type Status: Invalid/unexpected response'])
                        try:
                            value = ConferenceStatusValues[temp['confstate']]
                            self.WriteStatus('ConferenceStatus', value, {})
                        except (KeyError, IndexError):
                            self.Error(['Conference Status: Invalid/unexpected response'])
                        try:
                            value = ConferenceTypeStatusValues[temp['conftype']]
                            self.WriteStatus('ConferenceTypeStatus', value, {})
                        except (KeyError, IndexError):
                            self.Error(['Conference Type Status: Invalid/unexpected response'])
                        try:
                            value = RemoteMicrophoneStatusValues[temp['RemoteMicStates']]
                            self.WriteStatus('RemoteMicrophoneStatus', value, {})
                        except (KeyError, IndexError):
                            self.Error(['Remote Microphone Status: Invalid/unexpected response'])
                    else:
                        self.SessionID = False
                        self.AuthenticationFlag = False
                        self.UpdateSessionID( None, None)
                except (KeyError, IndexError):
                    self.Error(['Required Polling: Invalid/unexpected response'])
                    
    def UpdateSessionID(self, value, qualifier):
        SessionIDCmdString = 'action.cgi?ActionID=WEB_RequestSessionIDAPI'
        data = ''
        res = self.__UpdateHelper('SessionID', value, qualifier, url=SessionIDCmdString, data=data)
        if res:
            if res['success'] == 1:
                try:
                    self.SessionID = (loads(res['data']))['acSessionId']
                    if len(self.SessionID) > 2:
                        self.SessionFlag = True
                        self.UpdateRequiredPolling( None, None)
                    else:
                        self.SessionFlag = False
                except (KeyError, IndexError):
                    self.Error(['Session ID: Invalid/unexpected response'])
                    
    def UpdateSpeakerStatus(self, value, qualifier):

        self.UpdateAudioInput( None, None)

    def SetSpeakerVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 21,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SpeakerVolumeCmdString = 'action.cgi?ActionID=WEB_SetSpeakVolumeAPI'
            data = dumps({"speaker": 1, "speakerValue": value, "acCSRFToken": self.acCSRFToken})
            self.__SetHelper('SpeakerVolume', value, qualifier, url=SpeakerVolumeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetSpeakerVolume')

    def UpdateSpeakerVolume(self, value, qualifier):

        self.UpdateAudioInput( None, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return loads(response.read().decode())

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True
        url = '{0}/{1}'.format(self.RootURL, url)
        try:
            if self.SessionFlag:
                url = '{0}/{1}'.format(self.RootURL, url)
                headers = {'Sessionid': self.SessionID, 'Content-Type': 'application/json'}
                my_request = urllib.request.Request(url, data.encode(), headers=headers)
                res = self.Opener.open(my_request, timeout=10)
            else:
                self.UpdateSessionID(None, None)
                return ''
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: 
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        try:
            if not self.SessionFlag:   # Obtain Session ID
                url = '{0}/{1}'.format(self.RootURL, url)
                res = self.Opener.open(urllib.request.Request(url, data.encode()), timeout=10)
            elif self.SessionFlag:
                url = '{0}/{1}'.format(self.RootURL, url)
                headers = {'Sessionid': self.SessionID, 'Content-Type': 'application/json'}
                my_request = urllib.request.Request(url, data.encode(), headers=headers)
                res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
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
        self.SessionID = None
        self.acCSRFToken = None
        self.lastAudioInputUpdate = 0
        self.SessionFlag = False
        self.AuthenticationFlag = False
        self.PhoneBookList = {}
        self.set_entry = ''
        self.Advance = True
        self.StartingEntry = 1
        self.EndEntry = 0
        self.addList = []

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
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
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

