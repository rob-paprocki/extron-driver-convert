from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'PresetStatus': {'Parameters': ['Area'], 'Status': {}},
            'RecallPreset': {'Parameters': ['Area', 'Fade'], 'Status': {}},
            'ResetPreset': {'Parameters': ['Area', 'Fade'], 'Status': {}},
            'SavePreset': {'Parameters': ['Area'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x1C([\x00-\xFF])([\x00-\xA9])\x62\x00\x00\xFF[\x00-\xFF]'), self.__MatchPresetStatus, None)

    def UpdatePresetStatus(self, value, qualifier):

        area = int(qualifier['Area'])
        if 1 <= area <= 255:

            chksum = 0x1C + area + 0x63 + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            PresetStatusCmdString = pack('>8B', 0x1C, area, 0x00, 0x63, 0x00, 0x00, 0xFF, chksum)
            self.__UpdateHelper('PresetStatus', PresetStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresetStatus')

    def __MatchPresetStatus(self, match, tag):

        qualifier = {'Area': str(ord(match.group(1).decode('iso-8859-1')))}
        value = str(ord(match.group(2).decode('iso-8859-1')) + 1)
        self.WriteStatus('PresetStatus', value, qualifier)

    def SetRecallPreset(self, value, qualifier):

        FadeConstraints = {
            'Min': 0.0,
            'Max': 25.5
        }

        area = int(qualifier['Area'])
        fade = float(qualifier['Fade'])
        if FadeConstraints['Min'] <= fade <= FadeConstraints['Max'] and 1 <= area <= 255:

            fade = int(fade / 0.1)

            chksum = 0x1C + area + 0x67 + fade + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

            RecallPresetCmdString = pack('>8B', 0x1C, area, 0x00, 0x67, 0x00, fade, 0xFF, chksum)
            self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')

    def SetResetPreset(self, value, qualifier):

        FadeConstraints = {
            'Min': 0.00,
            'Max': 1310.00
        }

        area = int(qualifier['Area'])
        fade = float(qualifier['Fade'])
        if FadeConstraints['Min'] <= fade <= FadeConstraints['Max'] and 1 <= area <= 255:

            fade = int(fade / 0.02)
            fade_low = pack('>H', fade)[1]
            fade_high = pack('>H', fade)[0]

            chksum = 0x1C + area + fade_low + 0x0F + fade_high + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

            ResetPresetCmdString = pack('>8B', 0x1C, area, fade_low, 0x0F, fade_high, 0x00, 0xFF, chksum)
            self.__SetHelper('ResetPreset', ResetPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResetPreset')

    def SetSavePreset(self, value, qualifier):

        area = int(qualifier['Area'])
        if 1 <= area <= 255:

            chksum = 0x1C + area + 0x08 + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF

            SavePresetCmdString = pack('>8B', 0x1C, area, 0x00, 0x66, 0x00, 0x00, 0xFF, chksum)
            self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSavePreset')

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
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
