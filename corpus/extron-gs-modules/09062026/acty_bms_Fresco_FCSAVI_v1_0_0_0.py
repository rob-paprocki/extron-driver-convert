from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, search


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelLevel': {'Parameters': ['ID', 'Area', 'Room', 'Fade'], 'Status': {}},
            'ChannelLevelStatus': {'Parameters': ['ID', 'Area', 'Room'], 'Status': {}},
            'Heartbeat': {'Status': {}},
            'InputLevel': {'Parameters': ['ID'], 'Status': {}},
            'InputShadeControl': {'Parameters': ['ID'], 'Status': {}},
            'RoomLinkCommand': {'Status': {}},
            'RoomUnlinkCommand': {'Status': {}},
            'SceneLevel': {'Parameters': ['ID', 'Area', 'Room'], 'Status': {}},
            'ZoneIntensity': {'Parameters': ['ID', 'Fade'], 'Status': {}},
        }


        self.reg0 = compile(b'\?\r\nabout\x20\x20\x20\x09channel\x20\x09input\x20\x20\x20\x09link\x20\x20\x20\x20\r\nscene\x20\x20\x20\x09status\x20\x20\x09unlink\x20\x20\x09zone\x20\x20\x20\x20\r\n\?\?\x20\x20\x20\x20\x20\x20\x09\?\x20\x20\x20\x20\x20\x20\x20\x09\r\n|Fail\r\n')
        self.reg1 = compile(b'status channel (all|ALL)( [0-9]{1,3})?( [A-X])?\r\n([0-9]{1,3} ){1,36}\r\n|Fail\r\n')
        self.reg2 = compile(b'status input (all|ALL)\r\n([0-9]{1,3} ){1,36}\r\n|Fail\r\n')
        self.reg3 = compile(b'status scene (all|ALL)( [0-9]{1,3})?( [A-X])?\r\n([0-9]{1,3} ){1,36}\r\n|Fail\r\n')
        self.regLink = compile('link [A-X]{2,24}')
        self.regUnlink = compile('unlink [A-X]{2,24}')

    def SetChannelLevel(self, value, qualifier):

        FadeConstraints = {
            'Min': 0,
            'Max': 1000
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and \
                FadeConstraints['Min'] <= qualifier['Fade'] <= FadeConstraints['Max'] and \
                1 <= int(qualifier['ID']) <= 36 and \
                (qualifier['Area'] == 'Current Area' or 1 <= int(qualifier['Area']) <= 255) and \
                (qualifier['Room'] == 'Current Room' or 'A' <= qualifier['Room'] <= 'X'):

            if qualifier['Area'] != 'Current Area' and qualifier['Room'] != 'Current Room':
                ChannelLevelCmdString = 'channel {0} {1} {2} {3} {4}\r\n'.format(qualifier['ID'], value, qualifier['Area'], qualifier['Room'], qualifier['Fade'])
            elif qualifier['Area'] != 'Current Area' and qualifier['Room'] == 'Current Room':
                ChannelLevelCmdString = 'channel {0} {1} {2} {3}\r\n'.format(qualifier['ID'], value, qualifier['Area'], qualifier['Fade'])
            elif qualifier['Area'] == 'Current Area' and qualifier['Room'] != 'Current Room':
                ChannelLevelCmdString = 'channel {0} {1} {2} {3}\r\n'.format(qualifier['ID'], value, qualifier['Room'], qualifier['Fade'])
            else:
                ChannelLevelCmdString = 'channel {0} {1} {2}\r\n'.format(qualifier['ID'], value, qualifier['Fade'])
            self.__SetHelper('ChannelLevel', ChannelLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelLevel')

    def UpdateChannelLevelStatus(self, value, qualifier):

        if qualifier['Area'] != 'Current Area' and qualifier['Room'] != 'Current Room':
            ChannelLevelStatusCmdString = 'status channel ALL {0} {1}\r\n'.format(qualifier['Area'], qualifier['Room'])
        elif qualifier['Area'] != 'Current Area' and qualifier['Room'] == 'Current Room':
            ChannelLevelStatusCmdString = 'status channel ALL {0}\r\n'.format(qualifier['Area'])
        elif qualifier['Area'] == 'Current Area' and qualifier['Room'] != 'Current Room':
            ChannelLevelStatusCmdString = 'status channel ALL {0}\r\n'.format(qualifier['Room'])
        else:
            ChannelLevelStatusCmdString = 'status channel ALL\r\n'
        res = self.__UpdateHelper('ChannelLevelStatus', ChannelLevelStatusCmdString, value, qualifier)
        if res:
            try:
                value = findall('(\d+)', res)
                if qualifier['Area'] != 'Current Area':
                    value = value[1:]
                if len(value) <= 36:
                    for i in range(0, len(value)):
                        self.WriteStatus('ChannelLevelStatus', int(value[i]), {'ID': str(i + 1), 'Area': qualifier['Area'], 'Room': qualifier['Room']})
                else:
                    self.Error(['Channel Level Status: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Channel Level Status: Invalid/unexpected response'])

    def SetInputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['ID']) <= 36:
            InputLevelCmdString = 'input {0} {1}\r\n'.format(qualifier['ID'], value)
            self.__SetHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        InputLevelCmdString = 'status input ALL\r\n'
        res = self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
        if res:
            try:
                value = findall('(\d+)', res)
                if len(value) <= 36:
                    for i in range(0, len(value)):
                        self.WriteStatus('InputLevel', int(value[i]), {'ID': str(i + 1)})
                else:
                    self.Error(['Input Level: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Input Level: Invalid/unexpected response'])

    def SetInputShadeControl(self, value, qualifier):

        ValueStateValues = {
            'Raise': 'raise',
            'Lower': 'lower',
            'Stop': 'stop'
        }
        if 1 <= int(qualifier['ID']) <= 36:
            InputShadeControlCmdString = 'input {0} {1}\r\n'.format(qualifier['ID'], ValueStateValues[value])
            self.__SetHelper('InputShadeControl', InputShadeControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputShadeControl')

    def SetRoomLinkCommand(self, value, qualifier):

        pattern = self.regLink        
        string = str(value)
        if pattern.match(string):
            RoomLinkCommandCmdString = pattern.match(string).group(0)
            self.__SetHelper('RoomLinkCommand', RoomLinkCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomLinkCommand')

    def SetRoomUnlinkCommand(self, value, qualifier):

        pattern = self.regUnlink        
        string = str(value)
        if pattern.match(string):
            RoomUnlinkCommandCmdString = pattern.match(string).group(0)
            self.__SetHelper('RoomUnlinkCommand', RoomUnlinkCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomUnlinkCommand')

    def SetSceneLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and \
                1 <= int(qualifier['ID']) <= 36 and \
                (qualifier['Area'] == 'Current Area' or 1 <= int(qualifier['Area']) <= 255) and \
                (qualifier['Room'] == 'Current Room' or 'A' <= qualifier['Room'] <= 'X'):

            if qualifier['Area'] != 'Current Area' and qualifier['Room'] != 'Current Room':
                SceneLevelCmdString = 'scene {0} {1} {2} {3}\r\n'.format(qualifier['ID'], str(value), qualifier['Area'], qualifier['Room'])
            elif qualifier['Area'] != 'Current Area' and qualifier['Room'] == 'Current Room':
                SceneLevelCmdString = 'scene {0} {1} {2}\r\n'.format(qualifier['ID'], str(value), qualifier['Area'])
            elif qualifier['Area'] == 'Current Area' and qualifier['Room'] != 'Current Room':
                SceneLevelCmdString = 'scene {0} {1} {2}\r\n'.format(qualifier['ID'], str(value), qualifier['Room'])
            else:
                SceneLevelCmdString = 'scene {0} {1}\r\n'.format(qualifier['ID'], str(value))
            self.__SetHelper('SceneLevel', SceneLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneLevel')

    def UpdateSceneLevel(self, value, qualifier):

        if qualifier['Area'] != 'Current Area' and qualifier['Room'] != 'Current Room':
            SceneLevelCmdString = 'status scene ALL {0} {1}\r\n'.format(qualifier['Area'], qualifier['Room'])
        elif qualifier['Area'] != 'Current Area' and qualifier['Room'] == 'Current Room':
            SceneLevelCmdString = 'status scene ALL {0}\r\n'.format(qualifier['Area'])
        elif qualifier['Area'] == 'Current Area' and qualifier['Room'] != 'Current Room':
            SceneLevelCmdString = 'status scene ALL {0}\r\n'.format(qualifier['Room'])
        else:
            SceneLevelCmdString = 'status scene ALL\r\n'
        res = self.__UpdateHelper('SceneLevel', SceneLevelCmdString, value, qualifier)
        if res:
            try:
                value = findall('(\d+)', res)
                if qualifier['Area'] != 'Current Area':
                    value = value[1:]
                if len(value) <= 36:
                    for i in range(0, len(value)):
                        self.WriteStatus('SceneLevel', int(value[i]), {'ID': str(i + 1), 'Area': qualifier['Area'], 'Room': qualifier['Room']})
                else:
                    self.Error(['Scene Level: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Scene Level: Invalid/unexpected response'])

    def SetZoneIntensity(self, value, qualifier):

        IDConstraints = {
            'Min': 1,
            'Max': 65535
        }

        FadeConstraints = {
            'Min': 0,
            'Max': 1000
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and IDConstraints['Min'] <= qualifier['ID'] <= IDConstraints['Max'] and FadeConstraints['Min'] <= qualifier['Fade'] <= FadeConstraints['Max']:
            ZoneIntensityCmdString = 'zone {0} {1} {2}\r\n'.format(qualifier['ID'], value, qualifier['Fade'])
            self.__SetHelper('ZoneIntensity', ZoneIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneIntensity')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'Fail\r\n' in response:
            self.Error(['{0}: Invalid Command.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        Regex = {
            'ChannelLevelStatus': self.reg1,
            'InputLevel': self.reg2,
            'SceneLevel': self.reg3
        }
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=Regex[command])
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

            
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
