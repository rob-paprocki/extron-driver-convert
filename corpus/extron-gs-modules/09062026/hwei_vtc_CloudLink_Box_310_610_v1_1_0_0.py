import time
import urllib.error
import urllib.request
from json import loads, dumps
from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog, GetUnverifiedContext

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self._context = None
        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._NumberOfPhonebookSearch = 5
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CallStatus': {'Status': {}},
            'CallTypeStatus': {'Status': {}},
            'ConferenceStatus': {'Status': {}},
            'ConferenceTypeStatus': {'Status': {}},
            'MicMute': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearch': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchResultSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'PhoneHook': {'Status': {}},
            'SleepMode': {'Status': {}},
            'Presentation': {'Status': {}},
            'RemoteMicrophoneStatus': {'Status': {}},
            'SpeakerMute': {'Status': {}},
            'SpeakerVolume': {'Status': {}},
        }

        self.SessionCookie = False
        self.acCSRFToken = None
        self.DialString = None
        self.PhoneBookList = {}
        self.Advance = True
        self.StartingEntry = 1
        self.EndEntry = 0
        self.addList = []

        self.Opener.add_handler(urllib.request.HTTPCookieProcessor())

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        if 1 <= int(value) <= 10:
            self._NumberOfPhonebookSearch = int(value)
        else:
            self.Error(['NumberOfPhonebookSearch Parameter set to an invalid value'])

    def SessionUpdate(self, value, qualifier):
        res = self.__UpdateHelper('SessionUpdate', value, qualifier, url='action.cgi?ActionID=WEB_RequestSessionIDAPI')
        if res:
            try:
                if res["success"] == 1:
                    self.SessionCookie = True
                    self.TokenUpdate(None, None)
                else:
                    raise ValueError
            except (KeyError, ValueError):
                self.SessionCookie = False
                self.Error(['Session Update: Invalid/unexpected response'])

    def TokenUpdate(self, value, qualifier):
        res = self.__UpdateHelper('TokenUpdate', value, qualifier, url='action.cgi?ActionID=WEB_RequestCertificateAPI', data={"user": self.deviceUsername, "password": self.devicePassword})
        if res:
            try:
                if res["success"] == 1:
                    self.acCSRFToken = res["data"]["acCSRFToken"]
                else:
                    raise ValueError
            except (KeyError, ValueError):
                self.acCSRFToken = None
                self.Error(['Token Update: Invalid/unexpected response'])
                self.SessionUpdate(None, None)

    def SetMicMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 'WEB_CloseMicAPI', 
            'Off': 'WEB_OpenMicAPI'
        }
        
        if value in ValueStateValues:
            MicMuteCmdString = 'action.cgi?ActionID={}'.format(ValueStateValues[value])
            data = {"acCSRFToken": self.acCSRFToken}
            self.__SetHelper('MicMute', value, qualifier, url=MicMuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMicMute')

    def UpdateMicMute(self, value, qualifier):

        MicStates = {
            0: 'On', 
            1: 'Off'
        }

        SpeakerStates = {
            1: 'On', 
            0: 'Off'
        }
        
        res = self.__UpdateHelper('MicMute', value, qualifier, url='action.cgi?ActionID=WEB_InitAudioCtrlParamsAPI', data={"acCSRFToken": self.acCSRFToken})
        if res:
            try:
                self.WriteStatus('MicMute', MicStates[res["data"]["MicSwitch"]], qualifier)
            except KeyError:
                self.Error(['Mic Mute: Invalid/unexpected response'])
            try:
                self.WriteStatus('SpeakerMute', SpeakerStates[res["data"]["SpeakerSwitch"]], qualifier)
            except KeyError:
                self.Error(['Speaker Mute: Invalid/unexpected response'])
            try:
                self.WriteStatus('SpeakerVolume', int(res["data"]["speakerValue"]), qualifier)
            except (KeyError, ValueError):
                self.Error(['Speaker Volume: Invalid/unexpected response'])

    def SetPhonebookNavigation(self, value, qualifier):

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if value == 'Up':
                self.StartingEntry -= 1
            elif value == 'Down':
                if self.Advance:
                    self.StartingEntry += 1
            elif value == 'Page Up':
                self.StartingEntry -= self._NumberOfPhonebookSearch
            elif value == 'Page Down':
                if self.Advance:
                    self.StartingEntry += self._NumberOfPhonebookSearch

            if self.StartingEntry < 1:
                self.StartingEntry = 1

            self.EndEntry = self.StartingEntry + self._NumberOfPhonebookSearch - 1

            number_of_names = len(self.addList)
            index = self.StartingEntry - 1
            button = 1
            self.Advance = True
            while index < number_of_names and index < self.EndEntry:
                self.WriteStatus('PhonebookSearchResult', self.addList[index], {'Button': button})
                button += 1
                index += 1

            if button <= self._NumberOfPhonebookSearch:
                self.Advance = False
                self.WriteStatus('PhonebookSearchResult', '*** End of list ***', {'Button': button})
                button += 1
                for idx in range(button, int(self._NumberOfPhonebookSearch) + 1):
                    self.WriteStatus('PhonebookSearchResult', '', {'Button': idx})
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookSearchResultSet(self, value, qualifier):

        if 1 <= value <= self._NumberOfPhonebookSearch:
            set_entry = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if set_entry not in ['', '*** Not Available ***', '*** End of list ***']:
                self.DialString = self.PhoneBookList[set_entry]
            else:
                self.Discard('Invalid Command for SetPhonebookSearchResultSet')
        else:
            self.Discard('Invalid Command for SetPhonebookSearchResultSet')

    def SetPhonebookUpdate(self, value, qualifier):

        param = ''
        if isinstance(qualifier, dict) and 'SearchString' in qualifier and qualifier['SearchString']:
            param = qualifier['SearchString']
        PhonebookUpdateCmdString = 'action.cgi?ActionID=WEB_SeachLdapAddrAPI'
        data = {"szKeyWords": param, "acCSRFToken": self.acCSRFToken}
        self.__SetHelper('PhonebookUpdate', value, qualifier, url=PhonebookUpdateCmdString, data=data)

        prev_time = time.monotonic()
        ctime = time.monotonic()
        while True:
            if ctime - prev_time > 3:
                break
            else:
                ctime = time.monotonic()

        PhonebookUpdateCmdString = 'action.cgi?ActionID=WEB_GetLdapAddrResultListAPI'
        data = {"acCSRFToken": self.acCSRFToken}
        res = self.__UpdateHelper('PhonebookUpdate', value, qualifier, url=PhonebookUpdateCmdString, data=data)
        if res:
            try:
                self.PhoneBookList = {}
                self.addList, ldap_list = [], res['data']['LdapList']
                button = 1
                for item in ldap_list:
                    self.addList.append(item['site'])
                    self.PhoneBookList[item['site']] = item['sipNum']
                    self.WriteStatus('PhonebookSearchResult', item['site'], {'Button': button})
                    button += 1
                if button <= self._NumberOfPhonebookSearch:
                    self.WriteStatus('PhonebookSearchResult', '*** End of list ***', {'Button': button})
                    button += 1
                    for idx in range(button, self._NumberOfPhonebookSearch + 1):
                        self.WriteStatus('PhonebookSearchResult', '', {'Button': idx})
            except KeyError:
                self.Error(['Phonebook Update: Invalid/unexpected response'])
        else:
            button = 1
            self.Advance = False
            self.WriteStatus('PhonebookSearchResult', '*** Not Available ***', {'Button': button})
            button = button + 1
            for idx in range(button, int(self._NumberOfPhonebookSearch) + 1):
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
            if value in ['Hangup', 'Cancel']:
                data = {"ucSiteHandle": 1, "acCSRFToken": self.acCSRFToken}
            elif value == 'Answer':
                data = {"ucValue": 1, "ucMediaType": 0, "ucSiteHandle": 1, "acCSRFToken": self.acCSRFToken}
            elif value == 'Reject':
                data = {"ucValue": 0, "ucMediaType": 0, "ucSiteHandle": 1, "acCSRFToken": self.acCSRFToken}
            elif self.DialString:
                data = {"szNumber": self.DialString, "acCSRFToken": self.acCSRFToken}
            else:
                self.Discard('Invalid Command for SetPhoneHook')
                return
            self.__SetHelper('PhoneHook', value, qualifier, url=PhoneHookCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPhoneHook')

    def SetSleepMode(self, value, qualifier):

        ValueStateValues = {
            'On' : 'WEB_StartTermSleepAPI', 
            'Off': 'WEB_SystemWakeUpAPI'
        }
        
        if value in ValueStateValues:
            SleepModeCmdString = 'action.cgi?ActionID={}'.format(ValueStateValues[value])
            data = {"acCSRFToken": self.acCSRFToken}
            self.__SetHelper('SleepMode', value, qualifier, url=SleepModeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetSleepMode')

    def UpdateSleepMode(self, value, qualifier):

        ValueStateValues = {
            'sleep'  : 'On', 
            'unsleep': 'Off'
        }

        SleepModeCmdString = 'action.cgi?ActionID=WEB_IsSystemSleepAPI'
        data = {"acCSRFToken": self.acCSRFToken}
        res = self.__UpdateHelper('SleepMode', value, qualifier, url=SleepModeCmdString, data=data)
        if res:
            try:
                value = ValueStateValues[res["data"]["isSystemSleep"]]
                self.WriteStatus('SleepMode', value, qualifier)
            except KeyError:
                self.Error(['Sleep Mode: Invalid/unexpected response'])

    def SetPresentation(self, value, qualifier):

        ValueStateValues = {
            'Start': 'WEB_StartSendAuxStreamAPI', 
            'Stop' : 'WEB_StopSendAuxStreamAPI'
        }
        
        if value in ValueStateValues:
            PresentationCmdString = 'action.cgi?ActionID={}'.format(ValueStateValues[value])
            data = {"acCSRFToken": self.acCSRFToken}
            self.__SetHelper('Presentation', value, qualifier, url=PresentationCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPresentation')

    def UpdatePresentation(self, value, qualifier):

        ValueStateValues = {
            'auxOpen' : 'Start', 
            'auxClose': 'Stop'
        }

        PresentationCmdString = 'action.cgi?ActionID=WEB_IsSendAuxStreamAPI'
        data = {"acCSRFToken": self.acCSRFToken}
        res = self.__UpdateHelper('Presentation', value, qualifier, url=PresentationCmdString, data=data)
        if res:
            try:
                value = ValueStateValues[res["data"]["isSendAux"]]
                self.WriteStatus('Presentation', value, qualifier)
            except KeyError:
                self.Error(['Presentation: Invalid/unexpected response'])

    def UpdateCallStatus(self, value, qualifier):

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

        CallStatusCmdString = 'action.cgi?ActionID=WEB_GetMailboxDataAPI'
        data = {"acCSRFToken": self.acCSRFToken}
        res = self.__UpdateHelper('CallStatus', value, qualifier, url=CallStatusCmdString, data=data)
        if res:
            try:
                branch = res['data']['state']
                value = CallStatusValues[branch['callstate']]
                self.WriteStatus('CallStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Call Status: Invalid/unexpected response'])
            try:
                value = CallTypeStatusValues[branch['calltype']]
                self.WriteStatus('CallTypeStatus', value, qualifier)
            except KeyError:
                self.Error(['Call Type Status: Invalid/unexpected response'])
            try:
                value = ConferenceStatusValues[branch['confstate']]
                self.WriteStatus('ConferenceStatus', value, qualifier)
            except KeyError:
                self.Error(['Conference Status: Invalid/unexpected response'])
            try:
                value = ConferenceTypeStatusValues[branch['conftype']]
                self.WriteStatus('ConferenceTypeStatus', value, qualifier)
            except KeyError:
                self.Error(['Conference Type Status: Invalid/unexpected response'])
            try:
                value = RemoteMicrophoneStatusValues[branch['RemoteMicStates']]
                self.WriteStatus('RemoteMicrophoneStatus', value, qualifier)
            except KeyError:
                self.Error(['Remote Microphone Status: Invalid/unexpected response'])

    def UpdateCallTypeStatus(self, value, qualifier):
        self.UpdateCallStatus(None, None)

    def UpdateConferenceStatus(self, value, qualifier):
        self.UpdateCallStatus(None, None)

    def UpdateConferenceTypeStatus(self, value, qualifier):
        self.UpdateCallStatus(None, None)

    def UpdateRemoteMicrophoneStatus(self, value, qualifier):
        self.UpdateCallStatus(None, None)

    def UpdateSpeakerMute(self, value, qualifier):
        self.UpdateMicMute(None, None)

    def SetSpeakerVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 15,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SpeakerVolumeCmdString = 'action.cgi?ActionID=WEB_SetSpeakVolumeAPI'
            data = {"speaker": 1, "speakerValue": value, "acCSRFToken": self.acCSRFToken}
            self.__SetHelper('SpeakerVolume', value, qualifier, url=SpeakerVolumeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetSpeakerVolume')

    def UpdateSpeakerVolume(self, value, qualifier):
        self.UpdateMicMute(None, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return loads(response.read().decode().replace('\\', '').replace('}"', '}').replace('"{', '{'))
        except Exception:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        
        if not self.SessionCookie:
            self.SessionUpdate(None, None)

        if self.acCSRFToken:
            self.Debug = True
            url = '{}{}'.format(self.RootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'
            if data is not None:
                data = dumps(data).encode()
            headers = {'Content-Type': 'application/json'}
            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

            try:
                res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
            except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
            except urllib.error.URLError as err: # received if can't reach the server (times out)
                self.Error(['{0} {1}'.format(command, err.reason)])
                res = ''
            except Exception as err: # includes HTTP status code 100 and any invalid status code
                res = ''
            else:
                if res.status not in (200, 202):
                    self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                    res = ''
                else:
                    res = self.__CheckResponseForErrors(command, res)
            return res
        else:
            self.Discard('Not Authenticated')

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if command not in ['SessionUpdate', 'TokenUpdate']:
            if not self.SessionCookie:
                self.SessionUpdate(None, None)

        if self.acCSRFToken or command in ['SessionUpdate', 'TokenUpdate']:
            url = '{}{}'.format(self.RootURL, url)
            if data is not None:
                data = dumps(data).encode()
            headers = {'Content-Type': 'application/json'}
            my_request = urllib.request.Request(url, data, headers=headers, method='POST')

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            try:
                res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
            except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
            except urllib.error.URLError as err: # received if can't reach the server (times out)
                self.Error(['{0} {1}'.format(command, err.reason)])
                res = ''
            except Exception as err: # includes HTTP status code 100 and any invalid status code
                res = ''
            else:
                if res.status not in (200, 202):
                    self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                    res = ''
                else:
                    res = self.__CheckResponseForErrors(command, res)
            return res
        else:
            self.Discard('Not Authenticated')

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.SessionCookie = False
        self.acCSRFToken = None
        self.PhoneBookList = {}
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
    def __init__(self, ipAddress, port, deviceUsername='api', devicePassword='Change_Me', Model=None, SSLVerifyMode='On'):
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
