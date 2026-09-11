from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
            'AreaOff': {'Status': {}},
            'Level': {'Parameters': ['Channel', 'Area'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Area'], 'Status': {}},
            'RampLevel': {'Parameters': ['Channel', 'Area'], 'Status': {}},
            'StopFade': {'Parameters': ['Channel', 'Area'], 'Status': {}},
            'Version': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Reply with Channel Level ([0-9]{1,5}), ?([0-9]{1,5}), ?[0-9]{1,5}, ?(100|[1-9][0-9]|[0-9]),'), self.__MatchLevel, None)
            self.AddMatchString(re.compile(b'Reply with Current Preset ([0-9]{1,5}), ?([0-9]{1,5}),'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'Signon[\s\S]+, ?(v[\s\S]+)'), self.__MatchVersion, None)

    def SetAreaOff(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 65535
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AreaOffCmdString = 'Off {}'.format(value)
            self.__SetHelper('AreaOff', AreaOffCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAreaOff')

    def SetLevel(self, value, qualifier):

        ChannelConstraints = {
            'Min': 0,
            'Max': 65535
        }

        AreaConstraints = {
            'Min': 0,
            'Max': 65535
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        channel_val = qualifier['Channel']
        area_val = qualifier['Area']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']
                and ChannelConstraints['Min'] <= channel_val <= ChannelConstraints['Max']
                and AreaConstraints['Min'] <= area_val <= AreaConstraints['Max']):
            LevelCmdString = 'ChannelLevel {0} {1} {2}'.format(channel_val, value, area_val)
            self.__SetHelper('Level', LevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLevel')

    def UpdateLevel(self, value, qualifier):

        ChannelConstraints = {
            'Min': 0,
            'Max': 65535
        }

        AreaConstraints = {
            'Min': 0,
            'Max': 65535
        }
        channel_val = qualifier['Channel']
        area_val = qualifier['Area']
        if (ChannelConstraints['Min'] <= channel_val <= ChannelConstraints['Max'] and
                AreaConstraints['Min'] <= area_val <= AreaConstraints['Max']):
            LevelCmdString = 'RequestChannelLevel {0} {1}'.format(channel_val, area_val)
            self.__UpdateHelper('Level', LevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLevel')

    def __MatchLevel(self, match, tag):

        ChannelConstraints = {
            'Min': 0,
            'Max': 65535
        }

        AreaConstraints = {
            'Min': 0,
            'Max': 65535
        }

        channel_val = int(match.group(1).decode())
        area_val = int(match.group(2).decode())
        if (ChannelConstraints['Min'] <= channel_val <= ChannelConstraints['Max'] and
                AreaConstraints['Min'] <= area_val <= AreaConstraints['Max']):
            value = int(match.group(3).decode())
            self.WriteStatus('Level', value, {'Channel': channel_val, 'Area': area_val})

    def SetPresetRecall(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 65535
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 65279
        }

        area_val = qualifier['Area']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
                AreaConstraints['Min'] <= area_val <= AreaConstraints['Max']):
            PresetRecallCmdString = 'Preset {0} {1}'.format(value, area_val)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        AreaConstraints = {
            'Min': 0,
            'Max': 65535
        }
        area_val = qualifier['Area']
        if AreaConstraints['Min'] <= area_val <= AreaConstraints['Max']:
            PresetRecallCmdString = 'RequestCurrentPreset {0}'.format(area_val)
            self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresetRecall')

    def __MatchPresetRecall(self, match, tag):

        AreaConstraints = {
            'Min': 0,
            'Max': 65535
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 65279
        }
        area_val = int(match.group(1).decode())
        value = int(match.group(2).decode())
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
                AreaConstraints['Min'] <= area_val <= AreaConstraints['Max']):
            self.WriteStatus('PresetRecall', value, {'Area': area_val})

    def SetRampLevel(self, value, qualifier):

        ChannelConstraints = {
            'Min': 0,
            'Max': 65535
        }

        AreaConstraints = {
            'Min': 0,
            'Max': 65535
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        channel_val = qualifier['Channel']
        area_val = qualifier['Area']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
                ChannelConstraints['Min'] <= channel_val <= ChannelConstraints['Max'] and
                AreaConstraints['Min'] <= area_val <= AreaConstraints['Max']):
            RampLevelCmdString = 'RampLevel {0} {1} {2}'.format(channel_val, value, area_val)
            self.__SetHelper('RampLevel', RampLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRampLevel')

    def SetStopFade(self, value, qualifier):

        ChannelConstraints = {
            'Min': 0,
            'Max': 65535
        }

        AreaConstraints = {
            'Min': 0,
            'Max': 65535
        }

        channel_val = qualifier['Channel']
        area_val = qualifier['Area']
        if (ChannelConstraints['Min'] <= channel_val <= ChannelConstraints['Max'] and
                AreaConstraints['Min'] <= area_val <= AreaConstraints['Max']):
            StopFadeCmdString = 'StopFade {0} {1}'.format(channel_val, area_val)
            self.__SetHelper('StopFade', StopFadeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStopFade')

    def UpdateVersion(self, value, qualifier):

        VersionCmdString = 'Version'
        self.__UpdateHelper('Version', VersionCmdString, value, qualifier)

    def __MatchVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Version', value, None)

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

        # check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
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
