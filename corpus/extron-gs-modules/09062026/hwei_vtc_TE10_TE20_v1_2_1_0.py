from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, GetUnverifiedContext
from json import loads, dumps
import urllib.request
import urllib.error
import base64


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.port = port

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        if self.port == 443:  # HTTPS
            self.RootURL = 'https://{0}:{1}/'.format(ipAddress, self.port)
            if deviceUsername is not None and devicePassword is not None:
                self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
            else:
                self.authentication = None

            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                      urllib.request.HTTPSHandler(context=self._context))
        else:  # HTTP
            self.RootURL = 'http://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        urllib.request.install_opener(self.Opener)

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
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
            'InputGainStatus': {'Parameters': ['Type'], 'Status': {}},
            'InputMuteStatus': {'Parameters': ['Type'], 'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookResultSet': {'Status': {}},
            'PhonebookSearch': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Index'], 'Status': {}},
            'PhoneHook': {'Parameters': ['Call Type', 'H235 Policy', 'Type'], 'Status': {}},
            'PointtoPointCallCommand': {'Status': {}},
            'Power': {'Status': {}},
            'Presentation': {'Status': {}},
            'RemoteControl': {'Status': {}},
            'RemoteMicrophoneStatus': {'Status': {}},
            'RequiredPolling': {'Status': {}},
            'SessionID': {'Status': {}},
            'SpeakerMuteStatus': {'Status': {}},
            'SpeakerVolume': {'Status': {}},
        }

        self.ID = ''
        self.CSRFToken = ''
        self.set_entry = ''
        self.Flag = False
        self.Authentication = False
        self.lastVolumeUpdate = 0
        self.lastAudioInputUpdate = 0
        self.Advance = True
        self.StartingEntry = 1
        self.EndEntry = 0
        self.addList = []
        self.Addressbook = {}
        self.NumberOfButton = 0


    @property
    def NumberOfPhonebookSearch(self):
        return self.NumberOfButton

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        if 1 <= int(value) <= 15:
            self.NumberOfButton = int(value)

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Mute': 'Close',
            'Unmute': 'Open',
        }

        url = 'action.cgi?ActionID=WEB_{}MicAPI'.format(ValueStateValues[value])
        data = dumps({"acCSRFToken": self.CSRFToken})
        self.__SetHelper('AudioInput', value, qualifier, url, data.encode())

    def UpdateAudioInput(self, value, qualifier):

        AudioInputStateValues = {
            0: 'Mute',
            1: 'Unmute',
        }

        MuteStateValues = {
            0: 'On',
            1: 'Off',
        }

        url = 'action.cgi?ActionID=WEB_InitAudioCtrlParamsAPI'
        data = dumps({"acCSRFToken": self.CSRFToken})
        res = self.__UpdateHelper('AudioInput', value, qualifier, url, data.encode())
        if res:
            try:
                res['success'] == 1
            except KeyError:
                self.Error(['Speaker Volume: Invalid/unexpected response'])
            else:
                temp = loads(res['data'])
                try:
                    value = AudioInputStateValues[temp['MicSwitch']]
                    self.WriteStatus('AudioInput', value, None)
                except (KeyError, IndexError):
                    self.Error(['Audio Input: Invalid/unexpected response'])
    
                for mic_numb in range(1, 4):
                    qualifier = {'Type': 'Mic {}'.format(mic_numb)}
                    try:
                        value = MuteStateValues[temp['mic{}'.format(mic_numb)]]
                        self.WriteStatus('InputMuteStatus', value, qualifier)
                    except (KeyError, IndexError):
                        self.Error(['Input Mute Status: Invalid/unexpected response'])
                    try:
                        value = int(temp['mic{}Value'.format(mic_numb)]) - 12
                        self.WriteStatus('InputGainStatus', value, qualifier)
                    except (ValueError, IndexError):
                        self.Error(['Input Gain Status: Invalid/unexpected response'])
    
                for side_value in ('L', 'R'):
                    qualifier = {'Type': 'HDMI {} In'.format(side_value)}
                    try:
                        value = MuteStateValues[temp['hdmi{}In'.format(side_value)]]
                        self.WriteStatus('InputMuteStatus', value, qualifier)
                    except (KeyError, IndexError):
                        self.Error(['Input Mute Status: Invalid/unexpected response'])
                    try:
                        value = int(temp['hdmi{}InValue'.format(side_value)]) - 12
                        self.WriteStatus('InputGainStatus', value, qualifier)
                    except (ValueError, IndexError):
                        self.Error(['Input Gain Status: Invalid/unexpected response'])
                try:
                    value = MuteStateValues[temp['SpeakerSwitch']]
                    self.WriteStatus('SpeakerMuteStatus', value, {})
                except (KeyError, IndexError):
                    self.Error(['Speaker Mute Status: Invalid/unexpected response'])
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
            url = 'action.cgi?ActionID=WEB_CtrlCameraOpeateAPI'
            data = dumps({"camState": CameraStates[cam_type], "camAction": ValueStateValues[value], "camPos": 255,
                          "camSrc": 0, "acCSRFToken": self.CSRFToken})
            self.__SetHelper('CameraControl', value, qualifier, url, data.encode())
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
            url = 'action.cgi?ActionID=WEB_CtrlCameraOpeateAPI'
            data = dumps({"camState": CameraStates[cam_type], "camAction": ActionStates[act_type], "camPos": int(value),
                          "camSrc": 0, "acCSRFToken": self.CSRFToken})
            self.__SetHelper('CameraPresetControl', value, qualifier, url, data.encode())
        else:
            self.Discard('Invalid Command for SetCameraPresetControl')

    def UpdateInputGainStatus(self, value, qualifier):

        TypeStates = ('Mic 1', 'Mic 2', 'Mic 3', 'HDMI L In', 'HDMI R In')

        type_qualifier = qualifier['Type']
        if type_qualifier in TypeStates:
            self.UpdateAudioInput(None, None)
        else:
            self.Discard('Invalid Command for UpdateInputGainStatus')

    def UpdateInputMuteStatus(self, value, qualifier):

        TypeStates = ('Mic 1', 'Mic 2', 'Mic 3', 'HDMI L In', 'HDMI R In')

        type_qualifier = qualifier['Type']
        if type_qualifier in TypeStates:
            self.UpdateAudioInput(None, None)
        else:
            self.Discard('Invalid Command for UpdateInputMuteStatus')

    def SetPhonebookNavigation(self, value, qualifier):

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if 'Page' in value:
                NumberOfAdvance = self.NumberOfButton
            else:
                NumberOfAdvance = 1

            if 'Down' in value:
                if self.Advance:
                    self.StartingEntry += NumberOfAdvance
            elif 'Up' in value:
                self.StartingEntry -= NumberOfAdvance

            if self.StartingEntry < 1:
                self.StartingEntry = 1

            self.EndEntry = self.StartingEntry + self.NumberOfButton - 1

            numOfName = len(self.addList)
            index = self.StartingEntry - 1
            button = 1
            self.Advance = True
            while index < numOfName and index < self.EndEntry:
                Name = self.addList[index]
                self.WriteStatus('PhonebookSearchResult', Name['szName'], {'Index': str(button)})
                button = button + 1
                index = index + 1

            if button <= self.NumberOfButton:
                self.Advance = False
                self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Index': str(button)})
                button = button + 1
                for i in range(button, int(self.NumberOfButton) + 1):
                    self.WriteStatus('PhonebookSearchResult', '', {'Index': str(i)})
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookResultSet(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': self.NumberOfButton
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            set_entry = self.ReadStatus('PhonebookSearchResult', {'Index': str(value)})
            if set_entry not in ['***Not Available***', '***End of list***']:
                self.set_entry = set_entry
        else:
            self.Discard('Invalid Command for SetPhonebookResultSet')

    def SetPhonebookSearch(self, value, qualifier):

        self.Addressbook = {}
        url = 'action.cgi?ActionID=WEB_GetSiteListAPI'
        data = dumps({"ParamIntArray": [], "acCSRFToken": self.CSRFToken})
        print('~~~~~ SetPhonebookSearch flag: {}, auth: {}'.format(self.Flag, self.Authentication))
        if self.Flag and self.Authentication:
            res = self.__UpdateHelper('PhonebookSearch', value, qualifier, url, data.encode())
            if res:
                print('~~~~~ SetPhonebookSearch res: {}'.format(res))
                try:
                    if res['success'] == 1:
                        print('~~~~~ SetPhonebookSearch success: {}'.format(res['success']))
                        temp = loads(res['data'])
                        addressbook = (temp['astSites'])
                        self.addList = addressbook[0:]
                        button = 1
                        for val in range(0, len(addressbook)):
                            Name = self.addList[button - 1]
                            self.Addressbook[Name['szName']] = self.addList[button - 1]
                            self.WriteStatus('PhonebookSearchResult', Name['szName'], {'Index': str(button)})
                            button = button + 1
                        if button <= self.NumberOfButton:
                            self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Index': str(button)})
                            button = button + 1
                            for i in range(button, self.NumberOfButton + 1):
                                self.WriteStatus('PhonebookSearchResult', '', {'Index': str(i)})
                    else:
                        self.Flag = False
                        self.Authentication = False
                        self.UpdateSessionID(None, None)
                except (KeyError, IndexError):
                    self.Error(['Phonebook Search: Invalid/unexpected response'])
            else:
                self.__MatchNoContact(None, None)
        else:
            self.__MatchNoContact(None, None)

    def __MatchNoContact(self, match, tag):
        button = 1
        self.Advance = False
        self.WriteStatus('PhonebookSearchResult', '***Not Available***', {'Button': button})
        button = button + 1
        for i in range(button, int(self.NumberOfButton) + 1):
            self.WriteStatus('PhonebookSearchResult', '', {'Button': str(i)})

    def SetPhoneHook(self, value, qualifier):

        CallTypeStates = {
            'Common': 0,
            'Video': 1,
        }

        H235PolicyStates = {
            'Enable': 1,
            'Disable': 0,
        }

        ValueStateValues = {
            'Make Point to Point Call Site': 'action.cgi?ActionID=WEB_CallSiteAPI',
            'Cancel': 'action.cgi?ActionID=WEB_CancelCallAPI',
            'Answer': 'action.cgi?ActionID=WEB_IncomingCallProcAPI',
            'Reject': 'action.cgi?ActionID=WEB_IncomingCallProcAPI',
            'Hangup': 'action.cgi?ActionID=WEB_HangupCallAPI',
        }

        call_type = qualifier['Call Type']
        policy_type = qualifier['H235 Policy']
        url = ValueStateValues[value]
        data = ''

        if value in ['Hangup', 'Cancel']:
            data = dumps({"ucSiteHandle": 1,
                          "acCSRFToken": self.CSRFToken})
        elif value == 'Answer' and call_type in CallTypeStates:
            data = dumps({"ucValue": 1, "ucMediaType": CallTypeStates[call_type], "ucSiteHandle": 1,
                          "acCSRFToken": self.CSRFToken})
        elif value == 'Reject' and call_type in CallTypeStates:
            data = dumps({"ucValue": 0, "ucMediaType": CallTypeStates[call_type], "ucSiteHandle": 1,
                          "acCSRFToken": self.CSRFToken})
        elif self.set_entry and call_type in CallTypeStates and policy_type in H235PolicyStates:
            data = dumps({"bIsLdapCall": 0, "bIsVideoCall": CallTypeStates[call_type], "ucEnableH239": 1,
                          "stSiteInfo": self.Addressbook[self.set_entry], "ucH235Policy": H235PolicyStates[policy_type],
                          "acCSRFToken": self.CSRFToken})
        if data:
            self.__SetHelper('PhoneHook', value, qualifier, url, data.encode())

    def SetPointtoPointCallCommand(self, value, qualifier):

        sz_numb = value
        if sz_numb:
            url = 'action.cgi?ActionID=WEB_CallNumberAPI'
            data = dumps({"szNumber": sz_numb, "acCSRFToken": self.CSRFToken})
            self.__SetHelper('PointtoPointCallCommand', value, qualifier, url, data.encode())

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'action.cgi?ActionID=WEB_SystemWakeUpAPI',
            'Off': 'action.cgi?ActionID=WEB_StartTermSleepAPI',
        }

        url = ValueStateValues[value]
        data = dumps({"acCSRFToken": self.CSRFToken})
        self.__SetHelper('Power', value, qualifier, url, data.encode())

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'unsleep': 'On',
            'sleep': 'Off',
        }

        url = 'action.cgi?ActionID=WEB_IsSystemSleepAPI'
        data = dumps({"acCSRFToken": self.CSRFToken})
        if self.Flag and self.Authentication:
            res = self.__UpdateHelper('Power', value, qualifier, url, data.encode())
            if res:
                try:
                    temp = loads(res['data'])
                    value = ValueStateValues[temp['isSystemSleep']]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])

    def SetPresentation(self, value, qualifier):

        ValueStateValues = {
            'Start': 'action.cgi?ActionID=WEB_StartSendAuxStreamAPI',
            'Stop': 'action.cgi?ActionID=WEB_StopSendAuxStreamAPI',
        }

        url = ValueStateValues[value]
        data = dumps({"acCSRFToken": self.CSRFToken})
        self.__SetHelper('Presentation', value, qualifier, url, data.encode())

    def SetRemoteControl(self, value, qualifier):

        ValueStateValues = {
            '0': 7,
            '1': 8,
            '2': 9,
            '3': 10,
            '4': 11,
            '5': 12,
            '6': 13,
            '7': 14,
            '8': 15,
            '9': 16,
            'Star': 17,
            'Pound': 18,
            'Up': 19,
            'Down': 20,
            'Left': 21,
            'Right': 22,
            'Back': 4,
            'OK': 66,
            'Menu': 82,
            'Power': 26,
            'Volume Up': 24,
            'Volume Down': 25,
            'Mute': 164,
        }

        url = 'action.cgi?ActionID=WEB_EmuRemoteKeyAPI'
        data = dumps({"keyState": 0, "keyCode": ValueStateValues[value], "acCSRFToken": self.CSRFToken})
        self.__SetHelper('RemoteControl', value, qualifier, url, data.encode())

    def UpdateRequiredPolling(self, value, qualifier):

        if not self.Authentication:
            url = 'action.cgi?ActionID=WEB_RequestCertificateAPI'
            data = dumps({"user": self.deviceUsername, "password": self.devicePassword})
            res = self.__UpdateHelper('RequiredPolling', value, qualifier, url, data.encode())
            if res:
                if res['success'] == 1:
                    self.Authentication = True
                    self.CSRFToken = (loads(res['data']))['acCSRFToken']
                elif res['success'] == 0:
                    self.Authentication = False
                    self.UpdateSessionID(None, None)

        elif self.Authentication:

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

            url = 'action.cgi?ActionID=WEB_GetMailboxDataAPI'
            data = dumps({"acCSRFToken": self.CSRFToken})
            res = self.__UpdateHelper('RequiredPolling', value, qualifier, url, data.encode())
            if res:
                try:
                    if res['success'] == 1:
                        self.Authentication = True
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
                        self.Flag = False
                        self.Authentication = False
                        self.UpdateSessionID(None, None)
                except (KeyError, IndexError):
                    self.Error(['Required Polling: Invalid/unexpected response'])

    def UpdateSessionID(self, value, qualifier):

        url = 'action.cgi?ActionID=WEB_RequestSessionIDAPI'
        data = ''
        res = self.__UpdateHelper('SessionID', value, qualifier, url, data.encode())
        if res:
            try:
                self.ID = (loads(res['data']))['acSessionId']
                if len(self.ID) > 2:
                    self.Flag = True
                    self.UpdateRequiredPolling(None, None)
                else:
                    self.Flag = False
            except (KeyError, IndexError):
                self.Error(['Session ID: Invalid/unexpected response'])

    def UpdateSpeakerMuteStatus(self, value, qualifier):

        self.UpdateAudioInput(None, None)

    def SetSpeakerVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 21,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            url = 'action.cgi?ActionID=WEB_SetSpeakVolumeAPI'
            data = dumps({"speaker": 1, "speakerValue": value, "acCSRFToken": self.CSRFToken})
            self.__SetHelper('SpeakerVolume', value, qualifier, url, data.encode())
        else:
            self.Discard('Invalid Command for SetSpeakerVolume')

    def UpdateSpeakerVolume(self, value, qualifier):

        self.UpdateAudioInput(None, None)

    def __CheckResponseForErrors(self, sourceCmdName, res):

        return loads(res.read().decode())

    def __SetHelper(self, command, value, qualifier, resource, data=None):
        self.Debug = True        
        try:
            if self.Flag:
                url = '{0}{1}'.format(self.RootURL, resource)
                my_request = urllib.request.Request(url, data, headers={'Sessionid': self.ID, 'Content-Type': 'application/json'})
                res = self.Opener.open(my_request, timeout=10)
            else:
                self.UpdateSessionID(None, None)
                return ''
        except urllib.error.HTTPError as err:
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

    def __UpdateHelper(self, command, value, qualifier, resource, data):
    
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        try:
            if self.Flag:
                url = '{0}{1}'.format(self.RootURL, resource)
                my_request = urllib.request.Request(url, data, headers={'Sessionid': self.ID, 'Content-Type': 'application/json'})
                res = self.Opener.open(my_request, timeout=10)
            else:   # get session ID
                url = '{0}{1}'.format(self.RootURL, resource)
                self.Flag = True
                res = self.Opener.open(urllib.request.Request(url, data), timeout=10)
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
