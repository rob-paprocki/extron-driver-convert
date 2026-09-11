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
            'ChannelBank': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'MuteStatus': {'Status': {}},
            'Power': {'Status': {}},
            'Teletext': {'Status': {}},
            'VolumeStep': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x68\x00\x01\x04([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]{3}'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x68\x80\x00\x01([\x02\x03])[\x00-\xFF]'), self.__MatchError, None)

    def SetChannelBank(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x68\x80\x01\x01\x00\xEA',
            'Bank 1': b'\x68\x80\x01\x01\x01\xEB',
            'Bank 2': b'\x68\x80\x01\x01\x02\xEC',
            'Bank 3': b'\x68\x80\x01\x01\x03\xED'
        }

        ChannelBankCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelBank', ChannelBankCmdString, value, qualifier)

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x68\x80\x02\x02\x07\x12\x05',
            'Down': b'\x68\x80\x02\x02\x07\x10\x03'
        }

        ChannelStepCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV': b'\x68\x80\x04\x01\x02\xEF',
            'PC': b'\x68\x80\x04\x01\x04\xF1',
            'HDMI 1': b'\x68\x80\x04\x01\x06\xF3',
            'HDMI 2': b'\x68\x80\x04\x01\x0B\xF8',
            'HDMI 3': b'\x68\x80\x04\x01\x0C\xF9'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x68\x80\x02\x02\x07\x11\x04',
            '1': b'\x68\x80\x02\x02\x07\x04\xF7',
            '2': b'\x68\x80\x02\x02\x07\x05\xF8',
            '3': b'\x68\x80\x02\x02\x07\x06\xF9',
            '4': b'\x68\x80\x02\x02\x07\x08\xFB',
            '5': b'\x68\x80\x02\x02\x07\x09\xFC',
            '6': b'\x68\x80\x02\x02\x07\x0A\xFD',
            '7': b'\x68\x80\x02\x02\x07\x0C\xFF',
            '8': b'\x68\x80\x02\x02\x07\x0D\x00',
            '9': b'\x68\x80\x02\x02\x07\x0E\x01',
            '-': b'\x68\x80\x02\x02\x07\x23\x16'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x68\x80\x02\x02\x07\x60\x53',
            'Down': b'\x68\x80\x02\x02\x07\x61\x54',
            'Right': b'\x68\x80\x02\x02\x07\x62\x55',
            'Left': b'\x68\x80\x02\x02\x07\x65\x58',
            'Enter': b'\x68\x80\x02\x02\x07\x68\x5B',
            'Exit': b'\x68\x80\x02\x02\x07\x2D\x20',
            'Guide': b'\x68\x80\x02\x02\x07\x4F\x42',
            'TV': b'\x68\x80\x02\x02\x07\x1B\x0E',
            'Return': b'\x68\x80\x02\x02\x07\x58\x4B',
            'Home': b'\x68\x80\x02\x02\x07\x76\x69',
            'Menu': b'\x68\x80\x02\x02\x07\x1A\x0D'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x68\x80\x02\x02\x07\x0F\x02'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMuteStatus(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x68\x80\x00\x01\x80\x69',
            'Off': b'\x68\x80\x00\x01\x00\xE9'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x68\x80\x03\x01\x00\xEC'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        powerBytes = '{0:08b}'.format(ord(match.group(1)))
        value = ValueStateValues[powerBytes[7]]
        self.WriteStatus('Power', value, None)
        muteValue = ValueStateValues[powerBytes[5]]
        self.WriteStatus('MuteStatus', muteValue, None)
        InputStateValues = {
            b'\x02': 'AV',
            b'\x04': 'PC',
            b'\x06': 'HDMI 1',
            b'\x0B': 'HDMI 2',
            b'\x0C': 'HDMI 3'
        }

        inputValue = InputStateValues[match.group(2)]
        self.WriteStatus('Input', inputValue, None)

    def SetTeletext(self, value, qualifier):

        ValueStateValues = {
            'Key': b'\x68\x80\x02\x02\x07\x2C\x1F',
            'Red': b'\x68\x80\x02\x02\x07\x6C\x5F',
            'Green': b'\x68\x80\x02\x02\x07\x14\x07',
            'Yellow': b'\x68\x80\x02\x02\x07\x15\x08',
            'Cyan': b'\x68\x80\x02\x02\x07\x16\x09'
        }

        TeletextCmdString = ValueStateValues[value]
        self.__SetHelper('Teletext', TeletextCmdString, value, qualifier)

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x68\x80\x02\x02\x07\x07\xFA',
            'Down': b'\x68\x80\x02\x02\x07\x0B\xFE'
        }

        VolumeStepCmdString = ValueStateValues[value]
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

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

        DEVICE_ERROR_CODES = {
            b'\x02': 'NACK - Command NOT Acknowledged.',
            b'\x03': 'Command Unsupported'
        }

        value = DEVICE_ERROR_CODES[match.group(1)]
        self.Error(['Error: ' + value])

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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

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
