from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
            'FirmwareVersion': {'Status': {}},
            'MasterPresetRecall': {'Parameters': ['Target'], 'Status': {}},
            'ScreenPresetRecall': {'Parameters': ['Target', 'Screen'], 'Status': {}},
        }

        FirmwareRegex = re.compile(b'{"path":"DeviceObject/system/version/@props/updater","value":"(.*?)"}\x04')
        MasterPresetRegex = re.compile(b'{"path":"DeviceObject/masterPresetBank/status/lastUsed/\$presetMode/@items/(PROGRAM|PREVIEW)/@props/memoryId","value":(1[0-5]|[1-9])}\x04')
        ScreenPresetRegex = re.compile(b'{"path":"DeviceObject/\$screen/@items/S(2[0-4]|1[0-9]|[1-9])/\$preset/@items/(A|B)/presetId/status/@props/id","value":(1[0-5]|[1-9])}\x04')
        ErrorRegex = re.compile(b'{"error":{"code":"E(09|10|11|12|13)","message":.*?}}\x04')

        if self.Unidirectional == 'False':
            self.AddMatchString(FirmwareRegex, self.__MatchFirmwareVersion, None)
            self.AddMatchString(MasterPresetRegex, self.__MatchMasterPresetRecall, None)
            self.AddMatchString(ScreenPresetRegex, self.__MatchScreenPresetRecall, None)
            self.AddMatchString(ErrorRegex, self.__MatchError, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '{"op":"get","path":"DeviceObject/system/version/@props/updater"}\x04'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetMasterPresetRecall(self, value, qualifier):

        TargetStates = ('Preview', 'Program')

        target_val = qualifier['Target']

        if target_val in TargetStates and 1 <= int(value) <= 15:
            MasterPresetRecallCmdString = ''.join(['{"op":"replace","path":"DeviceObject/masterPresetBank/control/load/$slot/@items/',
                                                   value, '/$preset/@items/', target_val.upper(), '/@props/xRequest","value":true}\x04'])
            self.__SetHelper('MasterPresetRecall', MasterPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterPresetRecall')

    def UpdateMasterPresetRecall(self, value, qualifier):

        TargetStates = ('Preview', 'Program')

        target_val = qualifier['Target']

        if target_val in TargetStates:
            MasterPresetRecallCmdString = ''.join(['{"op":"get","path":"DeviceObject/masterPresetBank/status/lastUsed/$presetMode/@items/',
                                                   target_val.upper(), '/@props/memoryId"}\x04'])
            self.__UpdateHelper('MasterPresetRecall', MasterPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMasterPresetRecall')

    def __MatchMasterPresetRecall(self, match, tag):

        qualifier = {}
        qualifier['Target'] = match.group(1).decode().title()
        value = match.group(2).decode()
        self.WriteStatus('MasterPresetRecall', value, qualifier)

    def SetScreenPresetRecall(self, value, qualifier):

        TargetStates = ('Preview', 'Program')

        screen_val = qualifier['Screen']
        target_val = qualifier['Target']

        if target_val in TargetStates and 1 <= int(screen_val) <= 24 and 1 <= int(value) <= 15:
            ScreenPresetRecallCmdString = ''.join(['{"op":"replace","path":"DeviceObject/presetBank/control/load/$slot/@items/',
                                                   value, '/$screen/@items/S', screen_val, '/$preset/@items/', target_val.upper(),
                                                   '/@props/xRequest","value":true}\x04'])
            self.__SetHelper('ScreenPresetRecall', ScreenPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenPresetRecall')

    def UpdateScreenPresetRecall(self, value, qualifier):

        TargetStates = {
            'Preview': 'B',
            'Program': 'A',
        }

        screen_val = qualifier['Screen']
        target_val = qualifier['Target']

        if target_val in TargetStates and 1 <= int(screen_val) <= 24:
            ScreenPresetRecallCmdString = ''.join(['{"op":"get","path":"DeviceObject/$screen/@items/S', screen_val,
                                                   '/$preset/@items/', TargetStates[target_val], '/presetId/status/@props/id"}\x04'])
            self.__UpdateHelper('ScreenPresetRecall', ScreenPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateScreenPresetRecall')

    def __MatchScreenPresetRecall(self, match, tag):

        TargetStates = {
            'B': 'Preview',
            'A': 'Program',
        }

        qualifier = {}
        qualifier['Target'] = TargetStates[match.group(2).decode()]
        qualifier['Screen'] = match.group(1).decode()
        value = match.group(3).decode()
        self.WriteStatus('ScreenPresetRecall', value, qualifier)

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

    def __MatchError(self, match, tag):

        self.counter = 0

        ErrorStates = {
            '09': 'Error: Unexpected command JSON token.',
            '10': 'Error: Unexpected keywords.',
            '11': 'Error: Unexpected operator.',
            '12': 'Error: Unexpected path.',
            '13': 'Error: Unexpected value.',
        }

        self.Error([ErrorStates[match.group(1).decode()]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def AsciiHexToAscii(value):

        return int(value, 16)

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