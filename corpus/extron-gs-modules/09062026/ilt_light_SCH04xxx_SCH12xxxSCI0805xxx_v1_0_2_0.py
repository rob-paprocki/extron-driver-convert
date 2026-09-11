from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, search


class DeviceClass:
    def __init__(self):

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AreaLevelAdjust': {'Parameters': ['Number', 'Direction', 'Channel'], 'Status': {}},
            'AreaStopFading': {'Parameters': ['Number', 'Channel'], 'Status': {}},
            'Channel': {'Parameters': ['Number', 'Area'], 'Status': {}},
            'Scene': {'Parameters': ['Area'], 'Status': {}},
            'SceneSave': {'Parameters': ['Number', 'Area'], 'Status': {}},
            'Sequence': {'Parameters': ['Number', 'Segment', 'Node', 'Action'], 'Status': {}},
            'SetAllChannel': {'Parameters': ['Area'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'@RL(\d\d):A(\d\d):L([A-Fa-f0-9)]{2})\r'), self.__MatchChannel, None)
            self.AddMatchString(compile(b'@RE(\d\d):A(\d\d)\r'), self.__MatchScene, None)

        self.FadeTimeRegEx = compile('^\d{1,2}$|^$')

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    @staticmethod
    def __scale_range_change(old_value, old_min=0, old_max=100, new_min=0, new_max=255):
        old_span = old_max - old_min
        if old_span == 0:
            new_value = new_min
        else:
            new_span = new_max - new_min
            new_value = float((old_value - old_min) * new_span) / float(old_span) + new_min
        return new_value

    @staticmethod
    def __round_value(old_value):
        dist = round(old_value % 0.4, 1)
        if 0.1 <= dist <= 0.3:
            new_value = round(old_value - dist if dist <= 0.2 else old_value + 0.4 - dist, 1)
        else:
            new_value = round(old_value, 1)
        return new_value

    def SetAreaLevelAdjust(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        DirectionStates = {
            'Increment level by 1%': 'R',
            'Decrement level by 1%': 'L'
        }

        ChannelConstraints = {
            'Min': 0,
            'Max': 99,
        }

        try:
            if qualifier['Channel'] == 'All':
                ChannelConstraints['Value'] = 0
            else:
                ChannelConstraints['Value'] = int(qualifier['Channel']) if qualifier['Channel'].isdigit() else -1
        except (ValueError, KeyError):
            ChannelConstraints['Value'] = -1

        direction = qualifier['Direction']
        if self.__constraint_checker(NumberConstraints, ChannelConstraints) and direction in DirectionStates:
            AreaLevelAdjustCmdString = '@C{}{:02}:A{:02}\r'.format(DirectionStates[direction],
                                                                   ChannelConstraints['Value'],
                                                                   NumberConstraints['Value'])
            self.__SetHelper('AreaLevelAdjust', AreaLevelAdjustCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAreaLevelAdjust')

    def SetAreaStopFading(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        ChannelConstraints = {
            'Min': 0,
            'Max': 99
        }

        try:
            if qualifier['Channel'] == 'All':
                ChannelConstraints['Value'] = 0
            else:
                ChannelConstraints['Value'] = int(qualifier['Channel']) if qualifier['Channel'].isdigit() else -1
        except (ValueError, KeyError):
            ChannelConstraints['Value'] = -1

        if self.__constraint_checker(NumberConstraints, ChannelConstraints):
            AreaStopFadingCmdString = '@SF{:02}:A{:02}\r'.format(ChannelConstraints['Value'],
                                                                 NumberConstraints['Value'])
            self.__SetHelper('AreaStopFading', AreaStopFadingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAreaStopFading')

    def SetChannel(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        AreaConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Area']) if qualifier['Area'].isdigit() else -1
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
            'Value': value
        }

        fade_time = qualifier['Fade Time']
        if not self.FadeTimeRegEx.match(fade_time):
            fade_time = '-1'

        FadeTimeConstraints = {
            'Min': 0,
            'Max': 99,
            'Value': int(fade_time) if fade_time.isdigit() else -1
        }

        if self.__constraint_checker(NumberConstraints, AreaConstraints, ValueConstraints, FadeTimeConstraints):
            level = int(self.__scale_range_change(ValueConstraints['Value']))
            ChannelCmdString = '@SC{:02}:A{:02}:L{:02X}:F{:02}\r'.format(NumberConstraints['Value'],
                                                                         AreaConstraints['Value'],
                                                                         level,
                                                                         FadeTimeConstraints['Value'])
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def UpdateChannel(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        AreaConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Area']) if qualifier['Area'].isdigit() else -1
        }

        if self.__constraint_checker(NumberConstraints, AreaConstraints):
            ChannelCmdString = '@RC{:02}:A{:02}\r'.format(NumberConstraints['Value'],
                                                          AreaConstraints['Value'])
            self.__UpdateHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannel')

    def __MatchChannel(self, match, tag):

        qualifier = dict()
        qualifier['Number'] = match.group(1).decode().lstrip('0')
        qualifier['Area'] = match.group(2).decode().lstrip('0')
        value = self.__scale_range_change(int(match.group(3).decode(), 16), old_max=255, new_max=100)
        value = self.__round_value(value)
        self.WriteStatus('Channel', value, qualifier)

    def SetScene(self, value, qualifier):

        AreaConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Area']) if qualifier['Area'].isdigit() else -1
        }

        ValueStateConstraints = {
            'Min': 0,
            'Max': 99
        }

        try:
            if value == 'OFF':
                ValueStateConstraints['Value'] = 0
            else:
                ValueStateConstraints['Value'] = int(value) if value.isdigit() else -1
        except ValueError:
            ValueStateConstraints['Value'] = -1

        fade_time = qualifier['Fade Time']
        if not self.FadeTimeRegEx.match(fade_time):
            fade_time = '-1'

        FadeTimeConstraints = {
            'Min': 0,
            'Max': 99,
            'Value': int(fade_time) if fade_time.isdigit() else -1
        }

        if self.__constraint_checker(AreaConstraints, ValueStateConstraints, FadeTimeConstraints):
            SceneCmdString = '@SS{:02}:A{:02}:F{:02}\r'.format(ValueStateConstraints['Value'],
                                                               AreaConstraints['Value'],
                                                               FadeTimeConstraints['Value'])
            self.__SetHelper('Scene', SceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScene')

    def UpdateScene(self, value, qualifier):

        AreaConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Area']) if qualifier['Area'].isdigit() else -1
        }

        if self.__constraint_checker(AreaConstraints):
            SceneCmdString = '@RS{:02}\r'.format(AreaConstraints['Value'])
            self.__UpdateHelper('Scene', SceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateScene')

    def __MatchScene(self, match, tag):

        qualifier = dict()
        qualifier['Area'] = match.group(2).decode().lstrip('0')
        value = match.group(1).decode().lstrip('0')
        value = value if value else 'OFF'
        self.WriteStatus('Scene', value, qualifier)

    def SetSceneSave(self, value, qualifier):

        NumberConstraints = {
            'Min': 0,
            'Max': 99
        }

        try:
            if qualifier['Number'] == 'Current':
                NumberConstraints['Value'] = 0
            else:
                NumberConstraints['Value'] = int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        except (ValueError, KeyError):
            NumberConstraints['Value'] = -1

        AreaConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Area']) if qualifier['Area'].isdigit() else -1
        }

        if self.__constraint_checker(NumberConstraints, AreaConstraints):
            SceneSaveCmdString = '@SA{:02}:A{:02}\r'.format(NumberConstraints['Value'], AreaConstraints['Value'])
            self.__SetHelper('SceneSave', SceneSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneSave')

    def SetSequence(self, value, qualifier):

        NumberConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Number']) if qualifier['Number'].isdigit() else -1
        }

        SegmentConstraints = {
            'Min': 1,
            'Max': 253,
            'Value': int(qualifier['Segment']) if qualifier['Segment'].isdigit() else -1
        }

        NodeConstraints = {
            'Min': 1,
            'Max': 253,
            'Value': int(qualifier['Node']) if qualifier['Node'].isdigit() else -1
        }

        ActionConstraints = {
            'Min': 0,
            'Max': 253
        }

        try:
            if qualifier['Action'] in ('None', 'Resume'):
                ActionConstraints['Value'] = 0
            else:
                ActionConstraints['Value'] = int(qualifier['Action']) if qualifier['Action'].isdigit() else -1
        except (ValueError, KeyError):
            ActionConstraints['Value'] = 0

        ValueStateValues = {
            'Start': 'S',
            'Pause': 'P',
            'Stop': 'T'
        }

        if (self.__constraint_checker(NumberConstraints, SegmentConstraints, NodeConstraints, ActionConstraints) and
                value in ValueStateValues):
            SequenceCmdString = None
            if value == 'Start' and qualifier['Action'] != 'None':
                SequenceCmdString = '@QS{:02}:S{:03}:N{:03}:A{:03}\r'.format(NumberConstraints['Value'],
                                                                             SegmentConstraints['Value'],
                                                                             NodeConstraints['Value'],
                                                                             ActionConstraints['Value'])
            elif value in ('Pause', 'Stop'):
                SequenceCmdString = '@Q{}{:02}:S{:03}:N{:03}\r'.format(ValueStateValues[value],
                                                                       NumberConstraints['Value'],
                                                                       SegmentConstraints['Value'],
                                                                       NodeConstraints['Value'])
            else:
                self.Discard('Invalid Command for SetSequence')

            if SequenceCmdString:
                self.__SetHelper('Sequence', SequenceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequence')

    def SetSetAllChannel(self, value, qualifier):

        AreaConstraints = {
            'Min': 1,
            'Max': 99,
            'Value': int(qualifier['Area']) if qualifier['Area'].isdigit() else -1
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
            'Value': value
        }

        fade_time = qualifier['Fade Time']
        if not self.FadeTimeRegEx.match(fade_time):
            fade_time = '-1'

        FadeTimeConstraints = {
            'Min': 0,
            'Max': 99,
            'Value': int(fade_time) if fade_time.isdigit() else -1
        }

        if self.__constraint_checker(AreaConstraints, ValueConstraints, FadeTimeConstraints):
            level = int(self.__scale_range_change(ValueConstraints['Value']))
            SetAllChannelCmdString = '@SC00:A{:02}:L{:02X}:F{:02}\r'.format(AreaConstraints['Value'],
                                                                            level,
                                                                            FadeTimeConstraints['Value'])
            self.__SetHelper('SetAllChannel', SetAllChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetAllChannel')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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

            self.Send(commandstring)

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
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS485', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
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
