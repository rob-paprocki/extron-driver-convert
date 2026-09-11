from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack

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
            'ActiveMicrophones': {'Status': {}},
            'ActiveMicrophoneStatus': {'Parameters': ['Number'], 'Status': {}},
            'Alarm': {'Status': {}},
            'AutoVideoTracking': {'Status': {}},
            'Blink': {'Parameters': ['Nameplate ID'], 'Status': {}},
            'BlinkAllNameplates': {'Status': {}},
            'MicrophoneGain': {'Parameters': ['Congress Unit ID'], 'Status': {}},
            'MicrophonePower': {'Parameters': ['Microphone ID'], 'Status': {}},
            'NameplateControl': {'Status': {}},
            'NameplatePower': {'Parameters': ['Nameplate ID'], 'Status': {}},
            'NameplatePowerAllNameplates': {'Status': {}},
            'Page': {'Parameters': ['Nameplate ID'], 'Status': {}},
            'PageAllNameplates': {'Status': {}},
            'Power': {'Status': {}},
            'Scroll': {'Parameters': ['Nameplate ID', 'Scroll Speed', 'Scroll Page'], 'Status': {}},
            'ScrollAllNameplates': {'Parameters': ['Scroll Speed', 'Scroll Page'], 'Status': {}},
            'TurnOffAllMicrophones': {'Status': {}},
            'Volume': {'Parameters': ['Type'], 'Status': {}},
        }

        self.controlFlag = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xEA\xE8\x0F\x41([\x00-\x04])([\x00-\xFF]{12})\xED'), self.__MatchActiveMicrophoneStatus, None)  # Taiden Active Microphone Status Response.docx
            self.AddMatchString(re.compile(b'\xEA\xE8\x06\x47([\x00-\xFF]{2})([\x00-\xFF])\x00\xED'), self.__MatchMicrophoneGain, None)
            self.AddMatchString(re.compile(b'\xEA\xE8[\x00-\xFF]\xB4[\x00-\xFF]{3}([\x00-\xFF]{1,})\xED'), self.__MatchNameplatePower, None)
            self.AddMatchString(re.compile(b'\xE6\x01([\x01\x02])[\xE8-\xE9]'), self.__MatchPower, None)

    def __MatchActiveMicrophoneStatus(self, match, tag):

        num = ord(match.group(1).decode())
        value = match.group(2)

        if 0 <= num <= 4:
            self.WriteStatus('ActiveMicrophones', num, None)

        i = 0
        if num == 0:
            for j in range(1, 5):
                self.WriteStatus('ActiveMicrophoneStatus', 'None', {'Number': str(j)})
        else:
            if num != 5:
                for j in range(num + 1, 5):
                    self.WriteStatus('ActiveMicrophoneStatus', 'None', {'Number': str(j)})
        while i < num * 2:
            id = unpack('>H', value[i:i + 2])[0]
            numb = '{0}'.format(int(i / 2 + 1))
            self.WriteStatus('ActiveMicrophoneStatus', str(id), {'Number': numb})
            i = i + 2

    def SetAlarm(self, value, qualifier):

        ValueStateValues = {
            'Set': b'\xEA\xE8\x05\xC4\x00\x00\xED',
            'Release': b'\xEA\xE8\x05\xC4\x01\x00\xED'
        }

        AlarmCmdString = ValueStateValues[value]
        self.__SetHelper('Alarm', AlarmCmdString, value, qualifier)

    def SetAutoVideoTracking(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xEA\xE8\x02\x51\xED',
            'Off': b'\xEA\xE8\x02\x52\xED'
        }

        AutoVideoTrackingCmdString = ValueStateValues[value]
        self.__SetHelper('AutoVideoTracking', AutoVideoTrackingCmdString, value, qualifier)

    def SetBlink(self, value, qualifier):

        ValueStateValues = {
            'A Side On, B Side On': 0xC0,
            'A Side On, B Side Off': 0x80,
            'A Side Off, B Side On': 0x40,
            'A Side Off, B Side Off': 0x00
        }
        if 0 <= int(qualifier['Nameplate ID']) <= 4095:
            upperbyte = qualifier['Nameplate ID'] >> 8
            if upperbyte == 0:
                lowerbyte = qualifier['Nameplate ID']
            else:
                lowerbyte = 255
            BlinkCmdString = pack('>8B', 0xEA, 0xE8, 0x05, 0xB8, upperbyte, lowerbyte, ValueStateValues[value], 0xED)
            self.__SetHelper('Blink', BlinkCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBlink')

    def SetBlinkAllNameplates(self, value, qualifier):

        ValueStateValues = {
            'A Side On, B Side On': 0xC0,
            'A Side On, B Side Off': 0x80,
            'A Side Off, B Side On': 0x40,
            'A Side Off, B Side Off': 0x00
        }

        BlinkAllNameplatesCmdString = pack('>8B', 0xEA, 0xE8, 0x05, 0xB8, 0xFF, 0xFF, ValueStateValues[value], 0xED)
        self.__SetHelper('BlinkAllNameplates', BlinkAllNameplatesCmdString, value, qualifier)

    def SetMicrophoneGain(self, value, qualifier):

        if (-15 <= value <= 15) and (0 <= int(qualifier['Congress Unit ID']) <= 4095):
            upperbyte = qualifier['Congress Unit ID'] >> 8
            if upperbyte == 0:
                lowerbyte = qualifier['Congress Unit ID']
            else:
                lowerbyte = 255
            tempvalue = value + 16
            MicrophoneGainCmdString = pack('>9B', 0xEA, 0xE8, 0x06, 0x48, upperbyte, lowerbyte, tempvalue, 0x00, 0xED)
            self.__SetHelper('MicrophoneGain', MicrophoneGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneGain')

    def UpdateMicrophoneGain(self, value, qualifier):

        if 0 <= int(qualifier['Congress Unit ID']) <= 4095:
            cID = qualifier['Congress Unit ID']
            upperbyte = qualifier['Congress Unit ID'] >> 8
            if upperbyte == 0:
                lowerbyte = qualifier['Congress Unit ID']
            else:
                lowerbyte = 255
            MicrophoneGainCmdString = pack('>9B', 0xEA, 0xE8, 0x06, 0x47, upperbyte, lowerbyte, 0x00, 0x00, 0xED)
            self.__UpdateHelper('MicrophoneGain', MicrophoneGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicrophoneGain')

    def __MatchMicrophoneGain(self, match, tag):

        qualifier = {}
        qualifier['Congress Unit ID'] = unpack('>H', match.group(1))[0]
        value = ord(match.group(2).decode(encoding='iso-8859-1'))
        if value >= 0x80:
            value = value - 0x80
        value = value - 16
        self.WriteStatus('MicrophoneGain', value, qualifier)

    def SetMicrophonePower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x41,
            'Off': 0x42
        }

        if 0 <= int(qualifier['Microphone ID']) <= 65535:
            upperbyte = qualifier['Microphone ID'] >> 8
            if upperbyte == 0:
                lowerbyte = qualifier['Microphone ID']
            else:
                lowerbyte = 255
            MicrophonePowerCmdString = pack('>7B', 0xEA, 0xE8, 0x04, ValueStateValues[value], upperbyte, lowerbyte, 0xED)
            self.__SetHelper('MicrophonePower', MicrophonePowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophonePower')

    def SetNameplateControl(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'\xEA\xE8\x02\xB1\xED',
            'Disable': b'\xEA\xE8\x02\xB2\xED'
        }

        NameplateControlCmdString = ValueStateValues[value]
        self.__SetHelper('NameplateControl', NameplateControlCmdString, value, qualifier)

    def SetNameplatePower(self, value, qualifier):

        ValueStateValues = {
            'A Side On, B Side On': 0xC0,
            'A Side On, B Side Off': 0x80,
            'A Side Off, B Side On': 0x40,
            'A Side Off, B Side Off': 0x00
        }

        if 0 <= int(qualifier['Nameplate ID']) <= 4095:
            upperbyte = qualifier['Nameplate ID'] >> 8
            if upperbyte == 0:
                lowerbyte = qualifier['Nameplate ID']
            else:
                lowerbyte = 255
            NameplatePowerCmdString = pack('>8B', 0xEA, 0xE8, 0x05, 0xB5, upperbyte, lowerbyte, ValueStateValues[value], 0xED)
            self.__SetHelper('NameplatePower', NameplatePowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNameplatePower')

    def UpdateNameplatePower(self, value, qualifier):

        NameplatePowerCmdString = b'\xea\xe8\x02\xb3\xed'
        self.__UpdateHelper('NameplatePower', NameplatePowerCmdString, value, qualifier)

    def __MatchNameplatePower(self, match, tag):

        ValueStateValues = {
            0x03: 'A Side On, B Side On',
            0x02: 'A Side On, B Side Off',
            0x01: 'A Side Off, B Side On',
            0x00: 'A Side Off, B Side Off'
        }

        value = match.group(1)
        for x in range(0, len(value), 3):
            temp_value = value[x: x + 3]
            qualifier = {'Nameplate ID': unpack('>H', temp_value[0:2])[0]}
            power_info = ValueStateValues[temp_value[2] >> 6]
            self.WriteStatus('NameplatePower', power_info, qualifier)

    def SetNameplatePowerAllNameplates(self, value, qualifier):

        ValueStateValues = {
            'A Side On, B Side On': 0xC0,
            'A Side On, B Side Off': 0x80,
            'A Side Off, B Side On': 0x40,
            'A Side Off, B Side Off': 0x00
        }

        NameplatePowerAllNameplatesCmdString = pack('>8B', 0xEA, 0xE8, 0x05, 0xB5, 0xff, 0xff, ValueStateValues[value], 0xED)
        self.__SetHelper('NameplatePowerAllNameplates', NameplatePowerAllNameplatesCmdString, value, qualifier)

    def SetPage(self, value, qualifier):

        ValueStateValues = {
            'A Side Page 1, B Side Page 1': 0x00,
            'A Side Page 1, B Side Page 2': 0x10,
            'A Side Page 1, B Side Page 3': 0x20,
            'A Side Page 2, B Side Page 1': 0x40,
            'A Side Page 2, B Side Page 2': 0x50,
            'A Side Page 2, B Side Page 3': 0x60,
            'A Side Page 3, B Side Page 1': 0x80,
            'A Side Page 3, B Side Page 2': 0x90,
            'A Side Page 3, B Side Page 3': 0xA0
        }
        if 0 <= int(qualifier['Nameplate ID']) <= 4095:
            upperbyte = qualifier['Nameplate ID'] >> 8
            if upperbyte == 0:
                lowerbyte = qualifier['Nameplate ID']
            else:
                lowerbyte = 255
            PageCmdString = pack('>8B', 0xEA, 0xE8, 0x05, 0xB9, upperbyte, lowerbyte, ValueStateValues[value], 0xED)
            self.__SetHelper('Page', PageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPage')

    def SetPageAllNameplates(self, value, qualifier):

        ValueStateValues = {
            'A Side Page 1, B Side Page 1': 0x00,
            'A Side Page 1, B Side Page 2': 0x10,
            'A Side Page 1, B Side Page 3': 0x20,
            'A Side Page 2, B Side Page 1': 0x40,
            'A Side Page 2, B Side Page 2': 0x50,
            'A Side Page 2, B Side Page 3': 0x60,
            'A Side Page 3, B Side Page 1': 0x80,
            'A Side Page 3, B Side Page 2': 0x90,
            'A Side Page 3, B Side Page 3': 0xA0
        }

        PageAllNameplatesCmdString = pack('>8B', 0xEA, 0xE8, 0x05, 0xB9, 0xFF, 0xFF, ValueStateValues[value], 0xED)
        self.__SetHelper('PageAllNameplates', PageAllNameplatesCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xE6\x01\xA3\x8A',
            'Off': b'\xE6\x01\xA1\x88'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xE6\x01\xA2\x89'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x02': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetScroll(self, value, qualifier):

        ScrollSpeedStates = {
            'Slow': '0',
            'Middle': '1'
        }

        ScrollPageStates = {
            'One Page': '0000',
            'Two Pages': '0100',
            'Three Pages': '1000'
        }

        ValueStateValues = {
            'A Side Start, B Side Start': '11',
            'A Side Start, B Side Stop': '10',
            'A Side Stop, B Side Start': '01',
            'A Side Stop, B Side Stop': '00'
        }

        if 0 <= int(qualifier['Nameplate ID']) <= 4095:
            upperbyte = qualifier['Nameplate ID'] >> 8
            if upperbyte == 0:
                lowerbyte = qualifier['Nameplate ID']
            else:
                lowerbyte = 255
            valuebyte = ValueStateValues[value] + '1' + ScrollSpeedStates[qualifier['Scroll Speed']] + ScrollPageStates[qualifier['Scroll Page']]
            valuebyte = int(valuebyte, 2)
            ScrollCmdString = pack('>8B', 0xEA, 0xE8, 0x05, 0xB7, upperbyte, lowerbyte, valuebyte, 0xED)
            self.__SetHelper('Scroll', ScrollCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScroll')

    def SetScrollAllNameplates(self, value, qualifier):

        ScrollSpeedStates = {
            'Slow': '0',
            'Middle': '1'
        }

        ScrollPageStates = {
            'One Page': '0000',
            'Two Pages': '0100',
            'Three Pages': '1000'
        }

        ValueStateValues = {
            'A Side Start, B Side Start': '11',
            'A Side Start, B Side Stop': '10',
            'A Side Stop, B Side Start': '01',
            'A Side Stop, B Side Stop': '00'
        }
        valuebyte = ValueStateValues[value] + '1' + ScrollSpeedStates[qualifier['Scroll Speed']] + ScrollPageStates[qualifier['Scroll Page']]
        valuebyte = int(valuebyte, 2)
        ScrollAllNameplatesCmdString = pack('>8B', 0xEA, 0xE8, 0x05, 0xB7, 0xFF, 0xFF, valuebyte, 0xED)
        self.__SetHelper('ScrollAllNameplates', ScrollAllNameplatesCmdString, value, qualifier)

    def SetTurnOffAllMicrophones(self, value, qualifier):

        TurnOffAllMicrophonesCmdString = b'\xEA\xE8\x02\x43\xED'
        self.__SetHelper('TurnOffAllMicrophones', TurnOffAllMicrophonesCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        TypeStates = {
            'Master': 0x18,
            'Speaker': 0x14,
            'Line-In 1': 0x13,
            'Line-In 2': 0x17
        }

        ValueConstraints = {
            'Min': -30,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            tempvalue = abs(value)
            VolumeCmdString = pack('>6B', 0xEA, 0xE8, 0x03, TypeStates[qualifier['Type']], tempvalue, 0xED)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if not self.controlFlag:
            self.Send(b'\xEA\xE8\x02\x01\xED')
            self.controlFlag = True
        else:
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

            if not self.controlFlag:
                self.Send(b'\xEA\xE8\x02\x01\xED')
                self.controlFlag = True
            else:
                self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.controlFlag = False
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


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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
