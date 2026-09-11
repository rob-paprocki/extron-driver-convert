from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'BrightnessStatus': {'Parameters': ['Module ID', 'Port'], 'Status': {}},
            'DimmingPort': {'Parameters': ['Module ID', 'Port'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Module ID'], 'Status': {}},
            'PresetSave': {'Parameters': ['Module ID'], 'Status': {}},
            'SetBrightness': {'Parameters': ['Module ID', 'Port', 'Gradient'], 'Status': {}},
            'VersionNumber': {'Parameters': ['Module ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'V\d\.\d+'), self.__MatchVersionNumber, None)
            self.AddMatchString(re.compile(b'\xCA\xB0([\x01-\x80])\x02([\x80-\xFF])([\x80-\xFF])\xAC'), self.__MatchBrightnessStatus, None)


    def UpdateBrightnessStatus(self, value, qualifier):

        ModuleID = 0xFE if qualifier['Module ID'] is 'Broadcast' else int(qualifier['Module ID'])

        if 1 <= ModuleID <= 128 or ModuleID == 0xFE:
            CmdString = b'\xCA\x20' + bytes([ModuleID]) + b'\x20\x01\x01\xAC'
            self.__UpdateHelper('BrightnessStatus', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBrightnessStatus')

    def __MatchBrightnessStatus(self, match, tag):

        ModuleID = str(match.group(1)[0])
        self.WriteStatus('BrightnessStatus', match.group(2)[0] - 0x80, {'Module ID': ModuleID, 'Port': '1'})
        self.WriteStatus('BrightnessStatus', match.group(3)[0] - 0x80, {'Module ID': ModuleID, 'Port': '2'})

    def SetDimmingPort(self, value, qualifier):

        ModuleID = 0xFE if qualifier['Module ID'] is 'Broadcast' else int(qualifier['Module ID'])
        Port = int(qualifier['Port'])

        States = {
            'Open': 1,
            'Close': 0,
            'Invert': 2
        }

        if (1 <= ModuleID <= 128 or ModuleID == 0xFE) and 1 <= Port <= 2:
            CmdString = bytes([0xCA, 0x20, ModuleID, 0x18, 0x02, Port, States[value], 0xAC])
            self.__SetHelper('DimmingPort', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimmingPort')

    def SetPresetRecall(self, value, qualifier):
        ModuleID = 0xFE if qualifier['Module ID'] is 'Broadcast' else int(qualifier['Module ID'])
        if (1 <= ModuleID <= 128 or ModuleID == 0xFE) and 0 <= int(value) <= 9:
            CmdString = b'\xCA\x20' + bytes(ModuleID) + b'\x35' + bytes([1 + int(value)]) + b'\xAC'
            self.__SetHelper('PresetRecall', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        ModuleID = 0xFE if qualifier['Module ID'] is 'Broadcast' else int(qualifier['Module ID'])

        if (1 <= ModuleID <= 128 or ModuleID == 0xFE) and 0 <= int(value) <= 9:
            CmdString = b'\xCA\x20' + bytes(ModuleID) + b'\x36' + bytes([1 + int(value)]) + b'\xAC'
            self.__SetHelper('PresetSave', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetSetBrightness(self, value, qualifier):

        ModuleID = 0xFE if qualifier['Module ID'] is 'Broadcast' else int(qualifier['Module ID'])
        Port = int(qualifier['Port'])
        Grad = int(qualifier['Gradient'])

        if (1 <= ModuleID <= 128 or ModuleID == 0xFE) and 1 <= Port <= 2 and 0 <= Gradient <= 255 and 0 <= value <= 127:
            CmdString = bytes([0xCA, 0x20, ModuleID, 0x32, 0x03, Port, value, Grad, 0xAC])
            self.__SetHelper('SetBrightness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetBrightness')

    def UpdateVersionNumber(self, value, qualifier):
        ModuleID = 0xFE if qualifier['Module ID'] is 'Broadcast' else int(qualifier['Module ID'])
        if 1 <= ModuleID <= 128 or ModuleID == 0xFE:
            CmdString = b'\xCA\x20' + bytes(ModuleID) + b'\xBB\x01\x01\xAC'
            self.__UpdateHelper('VersionNumber', CmdString, value, qualifier)

    def __MatchVersionNumber(self, match, tag):
        self.WriteStatus('VersionNumber', match.group(0).decode(), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif qualifier['Module ID'] == 'Broadcast':
            self.Discard('Inappropriate Command {}, qualifier for Update was set to Broadcast'.format(command))
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
