from extronlib.system import Timer
import base64
from json import loads
import urllib.error
import urllib.request

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
            self.EnableLogin = True
        else:
            self.authentication = None
            self.EnableLogin = False
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Debug = False
        self.sid = ''
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ClearRequestToSpeakListAndSpeakersList': {'Status': {}},
            'IndividualVotingResults': {'Parameters': ['Name'], 'Status': {}},
            'Login': {'Status': {}},
            'Microphone': {'Parameters': ['Mic'], 'Status': {}},
            'MicrophoneRequestStatus': {'Parameters': ['Mic'], 'Status': {}},
            'MicrophoneStatus': {'Parameters': ['Mic'], 'Status': {}},
            'Power': {'Status': {}},
            'RequestToSpeakList': {'Parameters': ['Index'], 'Status': {}},
            'SeatName': {'Parameters': ['Mic'], 'Status': {}},
            'SpeakersList': {'Parameters': ['Index'], 'Status': {}},
            'VotingResults': {'Parameters': ['Result'], 'Status': {}},
            'VotingState': {'Status': {}},
        }
        
    def __ConstraintChecker(self, *args):

        try:
            for x in args:
                if not(x['Min'] <= int(x['Value']) <= x['Max']):
                    return False
            return True
        except:
            return False

    def SetLogin(self, value, qualfier):
        Login = '{{"override": true,"username":"{}","password":"{}"}}'.format(self.deviceUsername, self.devicePassword)
        opener = self.Opener
        opener.add_handler(urllib.request.HTTPCookieProcessor())
        my_request = urllib.request.Request(''.join([self.RootURL, 'api/login']), data=Login.encode(), headers={'Content-Type': 'application/json'}, method='POST')
        print('HERE')
        try:
            res = opener.open(my_request, timeout=10)
            if res:
                res = res.getheaders()
                for i in res:
                    if i[0] == 'sid':
                        self.sid = i[1]
        except:
            self.Error(['Error obtaining sid'])

    def SetClearRequestToSpeakListAndSpeakersList(self, value, qualifier):

        self.__SetHelper('ClearRequestToSpeakListAndSpeakersList', value, qualifier, url='api/speakers', data=None, method='DELETE')

    def UpdateIndividualVotingResults(self, value, qualifier):

        Results = {
            'yes': 'Yes/For',
            'for': 'Yes/For',
            'yes/for': 'Yes/For',
            'no': 'No/Against',
            'against': 'No/Against',
            'no/against': 'No/Against',
            'abstain': 'Abstain',
            'dnpv': 'Dnpv',
            'present': 'Present',
            'notVoted': 'Not Voted',
            'notPresent': 'Not Present'
        }

        VotingResultsCmdString = 'api/voting/results'
        res = self.__UpdateHelper('IndividualVotingResults', value, qualifier, url=VotingResultsCmdString)
        if res:
            try:
                res = loads(res.read().decode())
                value = 'Not Available'
                for i in res['individuals']:
                    if i['name'] == qualifier['Name']:
                        value = Results[i['result']]
                self.WriteStatus('IndividualVotingResults', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Individual Voting Results: Invalid/unexpected response'])

    def SetMicrophone(self, value, qualifier):

        MicConstraints = {
            'Min': 1,
            'Max': 80,
            'Value': qualifier['Mic']
        }

        CmdStrings = {
            'Open': 'api/speakers',
            'Close': 'api/speakers/{0}'.format(qualifier['Mic'])
        }

        ValueStateValues = {
            'Open': '[{0}]'.format(MicConstraints['Value']).encode(),
            'Close': None
        }

        Methods = {
            'Open': 'POST',
            'Close': 'DELETE'
        }

        if self.__ConstraintChecker(MicConstraints):
            MicrophoneCmdString = CmdStrings[value]
            MicrophoneData = ValueStateValues[value]
            Method = Methods[value]
            self.__SetHelper('Microphone', value, qualifier, url=MicrophoneCmdString, data=MicrophoneData, method=Method)
        else:
            self.Discard('Invalid Command for SetMicrophone')

    def UpdateMicrophoneRequestStatus(self, value, qualifier):

        MicrophoneRequestStatusCmdString = 'api/waiting-list'
        res = self.__UpdateHelper('MicrophoneRequestStatus', value, qualifier, url=MicrophoneRequestStatusCmdString)
        if res:
            res = res.read().decode()
            Ids = {a['id'] for a in loads(res)}
            Difference = set(range(1, 81)) - Ids
            if Ids:
                self.WriteStatus('MicrophoneRequestStatus', 'First on Waiting', {'Mic': str(loads(res)[0]['id'])})
            for a in Ids:
                if a != loads(res)[0]['id']:
                    self.WriteStatus('MicrophoneRequestStatus', 'Waiting', {'Mic': str(a)})
            for a in Difference:
                self.WriteStatus('MicrophoneRequestStatus', 'Not Waiting', {'Mic': str(a)})
            for n in loads(res):
                self.WriteStatus('SeatName', n['seatName'], {'Mic': str(n['id'])})
        else:
            self.Error(['Microphone Request Status: Invalid/unexpected response'])

    def UpdateMicrophoneStatus(self, value, qualifier):

        MicrophoneStatusCmdString = 'api/speakers'
        res = self.__UpdateHelper('MicrophoneStatus', value, qualifier, url=MicrophoneStatusCmdString)
        if res:
            res = res.read().decode()
            Ids = {a['id'] for a in loads(res)}
            Difference = set(range(1, 81)) - Ids
            for a in Ids:
                self.WriteStatus('MicrophoneStatus', 'Active', {'Mic': str(a)})
            for a in Difference:
                self.WriteStatus('MicrophoneStatus', 'Inactive', {'Mic': str(a)})
            for n in loads(res):
                self.WriteStatus('SeatName', n['seatName'], {'Mic': str(n['id'])})
        else:
            self.Error(['Microphone Status: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '{"state":0}',
            'Off': '{"state":2}',
            'Standby': '{"state":1}'
        }

        PowerCmdString = 'api/system/status'
        PowerData = ValueStateValues[value]
        self.__SetHelper('Power', value, qualifier, url=PowerCmdString, data=PowerData.encode())

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0: 'On',
            2: 'Off',
            1: 'Standby'
        }

        PowerCmdString = 'api/system/status'
        res = self.__UpdateHelper('Power', value, qualifier, url=PowerCmdString)
        if res:
            try:
                res = loads(res.read().decode())
                value = ValueStateValues[res['state']]
                self.WriteStatus('Power', value, qualifier)
            except KeyError:
                self.Error(['Power: Invalid/unexpected response'])

    def UpdateVotingResults(self, value, qualifier):

        Results = {
            'Yes': 'yes',
            'For': 'for',
            'No': 'no',
            'Against': 'against',
            'Abstain': 'abstain',
            'Dnpv': 'dnpv',
            'Present': 'present',
            'Not Voted': 'notVoted'
        }

        VotingResultsCmdString = 'api/voting/results'
        res = self.__UpdateHelper('VotingResults', value, qualifier, url=VotingResultsCmdString)
        if res:
            try:
                res = loads(res.read().decode())
                value = 'Not Available'
                for i in res['results']:
                    if i['name'] == Results[qualifier['Result']]:
                        value = i['value']
                self.WriteStatus('VotingResults', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Voting Results: Invalid/unexpected response'])

    def SetVotingState(self, value, qualifier):

        ValueStateValues = {
            'On': '{"state":1}',
            'Off': '{"state":0}'
        }

        VotingData = ValueStateValues[value]
        self.__SetHelper('VotingState', value, qualifier, url='api/voting/state', data=VotingData.encode())

    def UpdateVotingState(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        res = self.__UpdateHelper('VotingState', value, qualifier, url='api/voting/state')
        if res:
            try:
                res = loads(res.read().decode())
                value = ValueStateValues[res['state']]
                self.WriteStatus('VotingState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Voting State: Invalid/unexpected response'])

    def UpdateRequestToSpeakList(self, value, qualifier):

        res = self.__UpdateHelper('RequestToSpeakList', value, qualifier, url='api/waiting-list')
        if res:

            try:
                res = res.read().decode()
                res = loads(res)

                for i in range(1, 26):
                    if i > len(res):
                        self.WriteStatus('RequestToSpeakList', '0', {'Index': str(i)})
                    else:
                        value = str(res[i - 1]['id'])
                        self.WriteStatus('RequestToSpeakList', value, {'Index': str(i)})
            except:
                self.Error(['Request To Speak List: Invalid/unexpected response'])


    def UpdateSpeakersList(self, value, qualifier):

        res = self.__UpdateHelper('SpeakersList', value, qualifier, url='api/speakers')
        if res:

            try:
                res = res.read().decode()
                res = loads(res)

                for i in range(1, 26):
                    if i > len(res):
                        self.WriteStatus('SpeakersList', '0', {'Index': str(i)})
                    else:
                        value = str(res[i - 1]['id'])
                        self.WriteStatus('SpeakersList', value, {'Index': str(i)})

            except:
                self.Error(['Speakers List: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, value, qualifier, url='', data=None, method='PUT'):
        self.Debug = True

        headers = {'Content-Type': 'application/json'}

        if command == 'Power':
            if self.sid == '':
                self.Error(['Set Power missing sid value'])
            else:
                headers['sid'] = self.sid

        my_request = urllib.request.Request(''.join([self.RootURL, url]), data=data, headers=headers, method=method)

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            if err.code == 401:
                self.SetLogin(None, None)
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
            elif res.status == 401:
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                self.SetLogin(None, None)
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        my_request = urllib.request.Request(''.join([self.RootURL, url]), data=data, headers={'Content-Type': 'application/json'})

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            if err.code == 401:
                self.SetLogin(None, None)
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
            elif res.status == 401:
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                self.SetLogin(None, None)
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
