import urllib.error
import urllib.request
import json

class DeviceClass:
    def __init__(self, ipAddress, port):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActivateVideoConfigurationByID': { 'Status': {}},
            'DisableDelegateScreen': { 'Status': {}},
            'LEDSet': {'Parameters': ['Seat Number', 'LED'], 'Status': {}},
            'MaxActiveMicrophone': { 'Status': {}},
            'MicrophoneMode': {'Parameters': ['Mode', 'Microphone Active', 'Microphone Request'], 'Status': {}},
            'MicrophoneState': {'Parameters': ['Microphone'], 'Status': {}},
            'RoomVolume': {'Parameters':['Room'], 'Status': {}},
            'ServerVersion': { 'Status': {}},
            'VideoStreamGroupCommand': {'Parameters':['Type','Stream ID'], 'Status': {}},
            'VotingState': { 'Status': {}}
        }

        self.__MinMics = 1
        self.__MaxMics = 200

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))
    
    def SetActivateVideoConfigurationByID(self, value, qualifier):

        if 0 <= value:
            ActivateVideoConfigurationByIDCmdString = '/Video/ActivateVideoConfigurationById?PresetId={}'.format(value)
            self.__SetHelper('ActivateVideoConfigurationByID', value, qualifier, url=ActivateVideoConfigurationByIDCmdString)
        else:
            self.Discard('Invalid Command for SetActivateVideoConfigurationByID')

    def SetDisableDelegateScreen(self, value, qualifier):

        ValueStateValues = {
            'On':  'true',
            'Off': 'false'
            }

        if value in ValueStateValues:
            DisableDelegateScreenCmdString = '/Interactive/DisableDelegateScreen/?Disable={}'.format(ValueStateValues[value])
            self.__SetHelper('DisableDelegateScreen', value, qualifier, url=DisableDelegateScreenCmdString)
        else:
            self.Discard('Invalid Command for SetDisableDelegateScreen')

    def SetLEDSet(self, value, qualifier):

        SeatNumberConstraints = {
            'Min': self.__MinMics,
            'Max': self.__MaxMics,
            'Value': int(qualifier['Seat Number']) if qualifier['Seat Number'].isdigit() else (
                -1 if qualifier['Seat Number'] != 'All' else 9999),
        }

        LEDConstraints = {
            'Min': 1,
            'Max': 5,
            'Value': int(qualifier['LED']) if qualifier['LED'].isdigit() else -1,
        }

        ValueStateValues = ('On', 'Off', 'Blinking')

        if (value in ValueStateValues and
                (SeatNumberConstraints['Value'] == 9999 and self.__constraint_checker(LEDConstraints)) or
                (self.__constraint_checker(SeatNumberConstraints, LEDConstraints))):
            LEDSetCmdString = '/ButtonLED_Event/SetLED/?SeatNr={0}&LEDNr={1}&State={2}'.format(
                SeatNumberConstraints['Value'], LEDConstraints['Value'], value)
            self.__SetHelper('LEDSet', value, qualifier, url=LEDSetCmdString)
        else:
            self.Discard('Invalid Command for SetLEDSet')

    def UpdateMaxActiveMicrophone(self, value, qualifier):

        self.UpdateMicrophoneState( None, {'Microphone': value})

    def SetMicrophoneMode(self, value, qualifier):

        ModeStates = {
            'Operator':     'Operator',
            'Direct Speak': 'DirectSpeak',
            'Request':      'Request',
            'Vox':          'Vox',
            'Only Request': 'OnlyRequest',
        }

        MicActiveConstraints = {
            'Min': self.__MinMics,
            'Max': self.__MaxMics,
            'Value': int(qualifier['Microphone Active']) if qualifier['Microphone Active'].isdigit() else -1
        }

        MicRequestConstraints = {
            'Min': self.__MinMics,
            'Max': self.__MaxMics,
            'Value': int(qualifier['Microphone Request']) if qualifier['Microphone Request'].isdigit() else -1
        }

        mic_mode = qualifier['Mode']

        if mic_mode in ModeStates and self.__constraint_checker(MicActiveConstraints, MicRequestConstraints):
            MicrophoneModeCmdString = '/Microphone/SetMicrophoneMode/?Mode={0}&MaxNrActive={1}&MaxNrRequest={2}'.format(
                ModeStates[mic_mode], MicActiveConstraints['Value'], MicRequestConstraints['Value'])
            self.__SetHelper('MicrophoneMode', value, qualifier, url=MicrophoneModeCmdString)
        else:
            self.Discard('Invalid Command for SetMicrophoneMode')

    def SetMicrophoneState(self, value, qualifier):

        MicConstraints = {
            'Min': self.__MinMics,
            'Max': self.__MaxMics,
            'Value': int(qualifier['Microphone']) if qualifier['Microphone'].isdigit() else -1
        }

        ValueStateValues = ('On', 'Off', 'Request')

        if value in ValueStateValues and self.__constraint_checker(MicConstraints):
            MicrophoneStateCmdString = '/Microphone/SetState/?State={0}&SeatNr={1}'.format(value, MicConstraints['Value'])
            self.__SetHelper('MicrophoneState', value, qualifier, url=MicrophoneStateCmdString)
        else:
            self.Discard('Invalid Command for SetMicrophoneState')

    def UpdateMicrophoneState(self, value, qualifier):
            
        MicrophoneStateCmdString = '/Microphone/Get'
        res = self.__UpdateHelper('MicrophoneState', value, qualifier, url=MicrophoneStateCmdString)
        if res:
            try:

                res = json.loads(res.decode())
                state_reply = json.loads(res)
                mic_list = set(range(self.__MinMics, self.__MaxMics + 1))
                for idx in state_reply['Get']['State']['Speakers']:
                    self.WriteStatus('MicrophoneState', 'On', {'Microphone': str(idx)})
                    mic_list.discard(idx)
                for idx in state_reply['Get']['State']['Requests']:
                    self.WriteStatus('MicrophoneState', 'Request', {'Microphone': str(idx)})
                    mic_list.discard(idx)
                for idx in mic_list:
                    self.WriteStatus('MicrophoneState', 'Off', {'Microphone': str(idx)})
                max_mic_active = state_reply['Get']['MicrophoneMode']['MaxNrActive']
                if self.__MinMics <= max_mic_active <= self.__MaxMics:
                    self.WriteStatus('MaxActiveMicrophone', str(max_mic_active), None)
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['Microphone State: Invalid/unexpected response'])

    def SetRoomVolume(self, value, qualifier):

        if 1 <= int(qualifier['Room']) <= 10 and 0 <= value <= 25:
            RoomVolumeCmdString = '/CoCon/Room/SetVolumeForRoom/?Room={0}&Volume={1}'.format(qualifier['Room'], value)
            self.__SetHelper('RoomVolume', value, qualifier, url=RoomVolumeCmdString)
        else:
            self.Discard('Invalid Command for SetRoomVolume')

    def UpdateServerVersion(self, value, qualifier):

        ServerVersionCmdString = '/GetCoconServerVersion'
        res = self.__UpdateHelper('ServerVersion', value, qualifier, url=ServerVersionCmdString)
        if res:
            try:
                res = json.loads(res.decode())
                reply = json.loads(res)
                value = reply['GetCoconServerVersion']['Version']
                self.WriteStatus('ServerVersion', value, qualifier)
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['Server Version: Invalid/unexpected response'])

    def SetVideoStreamGroupCommand(self, value, qualifier):

        TypeStates = [
            'Input',
            'Output'
        ]
        type_ = qualifier['Type']
        stream_id = qualifier['Stream ID']
        group = value

        if type_ in TypeStates and 1 <= stream_id and group is not None:
            VideoStreamGroupCommandCmdString = ''

            if type_ == 'Input':
                try:
                    group = int(group)

                    if group >= -1:
                        VideoStreamGroupCommandCmdString = '/Video/SetVideoStreamInputGroup?VideoStreamId={}&VInputGroupId={}'.format(stream_id, group)
                except:
                    pass
            else:
                groups = set()
                for group in group.split(','):
                    try:
                        group = int(group)
                        if group >= 1:
                            groups.add(str(group))
                        else:
                            break
                    except:
                        pass
                else:
                    VideoStreamGroupCommandCmdString = '/Video/SetVideoStreamOutputGroup?VideoStreamId={}&VOutputGroupIds={}'.format(stream_id, ','.join(groups))

            if VideoStreamGroupCommandCmdString:
                self.__SetHelper('VideoStreamGroupCommand', value, qualifier, url=VideoStreamGroupCommandCmdString)
            else:
                self.Discard('Invalid Command for SetVideoStreamGroupCommand')
        else:
            self.Discard('Invalid Command for SetVideoStreamGroupCommand')

    def SetVotingState(self, value, qualifier):

        ValueStateValues = {
            'Start': 'Start',
            'Stop': 'Stop',
            'Pause': 'Pause',
            'Resume': 'Resume',
            'Restart': 'Restart',
            'Clear (Idle)': 'Clear'
            }

        if value in ValueStateValues:
            VotingStateCmdString = '/Voting/SetVotingState/?State={}'.format(ValueStateValues[value])
            if value not in ['Resume', 'Restart']:
                self.__SetHelper('VotingState', value, qualifier, url=VotingStateCmdString)
        else:
            self.Discard('Invalid Command for SetVotingState')

    def UpdateVotingState(self, value, qualifier):

        ValueStateValues = {
            'Start': 'Start',
            'Started': 'Start',
            'Stop': 'Stop',
            'Stopped': 'Stop',
            'Pause': 'Pause',
            'Paused': 'Pause',
            'Clear': 'Clear (Idle)',
            'Idle': 'Clear (Idle)',
            'Retrieve': 'Retrieve'
        }
        
        VotingStateCmdString = '/Voting/GetVotingState'
        res = self.__UpdateHelper('VotingState', value, qualifier, url=VotingStateCmdString)
        if res:
            try:
                res = json.loads(res.decode())
                reply = json.loads(res)
                value = ValueStateValues[reply['GetVotingState']['State'].replace('Voting', '')]
                self.WriteStatus('VotingState', value, qualifier)
            except (json.decoder.JSONDecodeError, KeyError):
                self.Error(['Voting State: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        response = response.read()
        if b'ER1' in response:
            self.Error(['{}: Unsupported command'.format(sourceCmdName)])
            response = b''
        elif b'ER2' in response:
            self.Error(['{}: Busy status'.format(sourceCmdName)])
            response = b''
        elif b'ER3' in response:
            self.Error(['{}: Outside acceptable range'.format(sourceCmdName)])
            response = b''
        return response

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}CoCon{}'.format(self.RootURL, url)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=1)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = b''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
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

        url = '{}CoCon{}'.format(self.RootURL, url)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=1)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = b''
        else:
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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port)
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