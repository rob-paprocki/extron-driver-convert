import re
import base64
import urllib.error
import urllib.request
import extronlib.standard.exml.etree.ElementTree as ET


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

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
            'GrabStill': {'Status': {}},
            'MediaPlayer': {'Parameters': ['Input'], 'Status': {}},
            'PlayMacroByName': {'Status': {}},
            'Recording': {'Status': {}},
            'SessionName': {'Status': {}},
            'Streaming': {'Status': {}},
            'TallySet': {'Parameters': ['Input', 'Channel'], 'Status': {}},
            'TallyStatus': {'Parameters': ['Input', 'Channel'], 'Status': {}},
            'TransitionAction': {'Parameters': ['Delegate'], 'Status': {}},
            'TransitionEffect': {'Parameters': ['Delegate'], 'Status': {}},
        }

    def SetGrabStill(self, value, qualifier):

        GrabStillCmdString = '/shortcut?name=grab_still'
        self.__SetHelper('GrabStill', value, qualifier, url=GrabStillCmdString)

    def SetMediaPlayer(self, value, qualifier):

        InputStates = {
            'DDR 1': 'ddr1',
            'DDR 2': 'ddr2',
            'GFX 1': 'gfx1',
            'GFX 2': 'gfx2',
            'Sound': 'sound'
        }

        ValueStateValues = {
            'Play': 'play',
            'Stop': 'stop',
            'Next': 'forward',
            'Previous': 'back'
        }

        if qualifier['Input'] in InputStates and value in ValueStateValues:
            MediaPlayerCmdString = '/shortcut?name={}_{}'.format(InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('MediaPlayer', value, qualifier, url=MediaPlayerCmdString)
        else:
            self.Discard('Invalid Command for SetMediaPlayer')

    def UpdateMediaPlayer(self, value, qualifier):

        self.UpdateRecording(value, qualifier)

    def SetPlayMacroByName(self, value, qualifier):

        macro_name = value
        if macro_name:
            PlayMacroByNameCmdString = '/shortcut?name=play_macro_byname&value={}'.format(macro_name.replace(' ', '%20'))
            self.__SetHelper('PlayMacroByName', value, qualifier, url=PlayMacroByNameCmdString)
        else:
            self.Discard('Invalid Command for SetPlayMacroByName')

    def SetRecording(self, value, qualifier):

        ValueStateValues = {
            'Start': '1',
            'Stop': '0'
        }

        if value in ValueStateValues:
            RecordingCmdString = '/shortcut?name=record_toggle&value={}'.format(ValueStateValues[value])
            self.__SetHelper('Recording', value, qualifier, url=RecordingCmdString)
        else:
            self.Discard('Invalid Command for SetRecording')

    def UpdateRecording(self, value, qualifier):

        rec_stream_state_values = {
            '1': 'Start',
            '0': 'Stop'
        }

        media_player_input_values = {
            'ddr1': 'DDR 1',
            'ddr2': 'DDR 2',
            'gfx1': 'GFX 1',
            'gfx2': 'GFX 2',
            'sound': 'Sound'
        }

        transition_delegate_values = {
            'background': 'Background',
            'dsk1': 'DSK 1',
            'dsk2': 'DSK 2',
            'dsk3': 'DSK 3',
            'dsk4': 'DSK 4'
        }

        RecordingCmdString = '/dictionary?key=shortcut_states'
        res = self.__UpdateHelper('Recording', value, qualifier, url=RecordingCmdString)
        if res:
            root = None
            try:
                root = ET.fromstring(res)
            except BaseException:
                self.Error(['Recording / Streaming / Media Player / Transition Effect: Invalid/unexpected response'])

            if root:
                try:
                    value = rec_stream_state_values[root.find('./shortcut_state/[@name="record_toggle"]').get('value')]
                    self.WriteStatus('Recording', value, None)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Recording: Invalid/unexpected response'])
                try:
                    value = rec_stream_state_values[root.find('./shortcut_state/[@name="streaming_toggle"]').get('value')]
                    self.WriteStatus('Streaming', value, None)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Streaming: Invalid/unexpected response'])
                try:
                    for selected_input in media_player_input_values.keys():
                        qualifier = {'Input': media_player_input_values[selected_input]}
                        play_state = root.find('./shortcut_state/[@name="{}_play"]'.format(selected_input)).get('value')
                        value = 'Play' if play_state == 'true' else 'Stop'
                        self.WriteStatus('MediaPlayer', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Media Player: Invalid/unexpected response'])
                try:
                    for selected_delegate in transition_delegate_values.keys():
                        qualifier = {'Delegate': transition_delegate_values[selected_delegate]}
                        fade_state = root.find('./shortcut_state/[@name="main_{}_select_fade"]'.format(selected_delegate)).get('value')
                        value = 'Fade' if fade_state == 'true' else 'Trans'
                        self.WriteStatus('TransitionEffect', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Transition Effect: Invalid/unexpected response'])

    def UpdateSessionName(self, value, qualifier):

        SessionNameCmdString = '/version'
        res = self.__UpdateHelper('SessionName', value, qualifier, url=SessionNameCmdString)
        if res:
            try:
                root = ET.fromstring(res)
                value = root.find('session_name').text
                self.WriteStatus('SessionName', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Session Name: Invalid/unexpected response'])

    def SetStreaming(self, value, qualifier):

        ValueStateValues = {
            'Start': '1',
            'Stop': '0'
        }

        if value in ValueStateValues:
            StreamingCmdString = '/shortcut?name=streaming_toggle&value={}'.format(ValueStateValues[value])
            self.__SetHelper('Streaming', value, qualifier, url=StreamingCmdString)
        else:
            self.Discard('Invalid Command for SetStreaming')

    def UpdateStreaming(self, value, qualifier):

        self.UpdateRecording(value, qualifier)

    def SetTallySet(self, value, qualifier):

        InputStates = {
            'Input 1': '0',
            'Input 2': '1',
            'Input 3': '2',
            'Input 4': '3',
            'Input 5': '4',
            'Input 6': '5',
            'Input 7': '6',
            'Input 8': '7',
            'Input 9': '8',
            'Input 10': '9',
            'Input 11': '10',
            'Input 12': '11',
            'Input 13': '12',
            'Input 14': '13',
            'Input 15': '14',
            'Input 16': '15',
            'Buffer 1': '16',
            'Buffer 2': '17',
            'Buffer 3': '18',
            'Buffer 4': '19',
            'Buffer 5': '20',
            'Buffer 6': '21',
            'Buffer 7': '22',
            'Buffer 8': '23',
            'Buffer 9': '24',
            'Buffer 10': '25',
            'Buffer 11': '26',
            'Buffer 12': '27',
            'Buffer 13': '28',
            'Buffer 14': '29',
            'Buffer 15': '30',
            'DDR 1': '39',
            'DDR 1a': '31',
            'DDR 1b': '32',
            'DDR 2': '40',
            'DDR 2a': '33',
            'DDR 2b': '34',
            'GFX 1': '41',
            'GFX 1a': '35',
            'GFX 1b': '36',
            'GFX 2': '42',
            'GFX 2a': '37',
            'GFX 2b': '38',
            'v1': '43',
            'v2': '44',
            'v3': '45',
            'v4': '46',
            'Preview': '47',
            'Me Preview': '48',
            'Me Follow': '49',
            'Previz': '50',
            'Web Follow': '51',
            'Sound': '-2',
            'Black': '-1'
        }

        ChannelStates = {
            'Program': 'a',
            'Preview': 'b'
        }

        if qualifier['Input'] in InputStates and qualifier['Channel'] in ChannelStates:
            TallySetCmdString = '/shortcut?name=main_{}_row&value={}'.format(ChannelStates[qualifier['Channel']], InputStates[qualifier['Input']])
            self.__SetHelper('TallySet', value, qualifier, url=TallySetCmdString)
        else:
            self.Discard('Invalid Command for SetTallySet')

    def UpdateTallyStatus(self, value, qualifier):

        InputStates = {
            '0': 'Input 1',
             '1': 'Input 2',
             '2': 'Input 3',
             '3': 'Input 4',
             '4': 'Input 5',
             '5': 'Input 6',
             '6': 'Input 7',
             '7': 'Input 8',
             '8': 'Input 9',
             '9': 'Input 10',
             '10': 'Input 11',
             '11': 'Input 12',
             '12': 'Input 13',
             '13': 'Input 14',
             '14': 'Input 15',
             '15': 'Input 16',
             '16': 'Buffer 1',
             '17': 'Buffer 2',
             '18': 'Buffer 3',
             '19': 'Buffer 4',
             '20': 'Buffer 5',
             '21': 'Buffer 6',
             '22': 'Buffer 7',
             '23': 'Buffer 8',
             '24': 'Buffer 9',
             '25': 'Buffer 10',
             '26': 'Buffer 11',
             '27': 'Buffer 12',
             '28': 'Buffer 13',
             '29': 'Buffer 14',
             '30': 'Buffer 15',
             '39': 'DDR 1',
             '31': 'DDR 1a',
             '32': 'DDR 1b',
             '40': 'DDR 2',
             '33': 'DDR 2a',
             '34': 'DDR 2b',
             '41': 'GFX 1',
             '35': 'GFX 1a',
             '36': 'GFX 1b',
             '42': 'GFX 2',
             '37': 'GFX 2a',
             '38': 'GFX 2b',
             '43': 'v1',
             '44': 'v2',
             '45': 'v3',
             '46': 'v4',
             '47': 'Preview',
             '48': 'Me Preview',
             '49': 'Me Follow',
             '50': 'Previz',
             '51': 'Web Follow',
             '-2': 'Sound',
             '-1': 'Black'
        }

        ChannelStates = ['Program', 'Preview']

        ValueStateValues = {
            'true': 'Displayed',
            'false': 'Not Displayed'
        }

        selected_input = qualifier['Input']
        selected_channel = qualifier['Channel']
        if selected_input in InputStates.values() and selected_channel in ChannelStates:
            TallyStatusCmdString = '/dictionary?key=tally'
            res = self.__UpdateHelper('TallyStatus', value, qualifier, url=TallyStatusCmdString)
            if res:
                try:
                    root = ET.fromstring(res)
                    for child in root:
                        qualifier1 = {'Input': InputStates[child.attrib['index']], 'Channel': 'Program'}
                        value = ValueStateValues[child.attrib['on_pgm']]
                        self.WriteStatus('TallyStatus', value, qualifier1)
                        qualifier2 = {'Input': InputStates[child.attrib['index']], 'Channel': 'Preview'}
                        value = ValueStateValues[child.attrib['on_prev']]
                        self.WriteStatus('TallyStatus', value, qualifier2)
                except (KeyError, IndexError):
                    self.Error(['Tally Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTallyStatus')

    def SetTransitionAction(self, value, qualifier):

        DelegateStates = {
            'Background': 'background',
            'DSK 1': 'dsk1',
            'DSK 2': 'dsk2',
            'DSK 3': 'dsk3',
            'DSK 4': 'dsk4'
        }

        ValueStateValues = {
            'Take': 'take',
            'Auto': 'auto'
        }

        if qualifier['Delegate'] in DelegateStates and value in ValueStateValues:
            TransitionActionCmdString = '/shortcut?name=main_{}_{}&value=true'.format(DelegateStates[qualifier['Delegate']], ValueStateValues[value])
            self.__SetHelper('TransitionAction', value, qualifier, url=TransitionActionCmdString)
        else:
            self.Discard('Invalid Command for SetTransitionAction')

    def SetTransitionEffect(self, value, qualifier):

        DelegateStates = {
            'Background': 'background',
            'DSK 1': 'dsk1',
            'DSK 2': 'dsk2',
            'DSK 3': 'dsk3',
            'DSK 4': 'dsk4'
        }

        ValueStateValues = {
            'Fade': 'select_fade',
            'Trans': 'select_saved_nonfade_transition'
        }

        if qualifier['Delegate'] in DelegateStates and value in ValueStateValues:
            TransitionEffectCmdString = '/shortcut?name=main_{}_{}'.format(DelegateStates[qualifier['Delegate']], ValueStateValues[value])
            self.__SetHelper('TransitionEffect', value, qualifier, url=TransitionEffectCmdString)
        else:
            self.Discard('Invalid Command for SetTransitionEffect')

    def UpdateTransitionEffect(self, value, qualifier):

        self.UpdateRecording(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = None
        if response:
            res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/v1{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/xml'}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}/v1{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/xml'}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
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