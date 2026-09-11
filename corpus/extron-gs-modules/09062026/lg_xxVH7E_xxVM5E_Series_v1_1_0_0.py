from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceSerialClass:
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
        self._DeviceID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'],'Status': {}},
            'Keypad': {'Parameters': ['Device ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMode': {'Parameters': ['Device ID', 'Column', 'Row'], 'Status': {}},
            'TilePosition': {'Parameters': ['Device ID', 'Tile ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9A-F]{2}) OK0(2|6)x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e ([0-9A-F]{2}) OK0(1|0)x', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm ([0-9A-F]{2}) OK0(1|0)x', re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b ([0-9A-F]{2}) OK(90|A0|91|A1|95|A5|C0|D0)x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'a ([0-9A-F]{2}) OK0(1|0)x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'f ([0-9A-F]{2}) OK([0-9A-F]{2})x', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'([uicembadfx]) ([0-9A-F]{2}) NG([0-9A-F]{2})x', re.I), self.__MatchError, None)

        self.regexSet = re.compile(b'(OK|NG)[0-9A-F]{2}x', re.I)
   
    def GetDeviceID(self, ID):
        if ID == 'Broadcast':
            return '00'
        elif 1 <= int(ID) <= 1000:
            return '{0:02X}'.format(int(ID))
        else:
            self.Error(['Invalid Device ID provided'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full Screen': '02',
            'Original': '06'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID and value in ValueStateValues:
            AspectRatioCmdString = 'kc {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            AspectRatioCmdString = 'kc {0} FF\r'.format(ID)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '2': 'Full Screen',
            '6': 'Original'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AspectRatio', value, {'Device ID': str(ID)})
        else:
            self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID and value in ValueStateValues:
            AudioMuteCmdString = 'ke {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            AudioMuteCmdString = 'ke {0} FF\r'.format(ID)
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, {'Device ID': str(ID)})
        else:
            self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID and value in ValueStateValues:
            ExecutiveModeCmdString = 'km {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            ExecutiveModeCmdString = 'km {0} FF\r'.format(ID)
            self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('ExecutiveMode', value, {'Device ID': str(ID)})
        else:
            self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1 (DTV)': '90',
            'HDMI 1 (PC)': 'A0',
            'HDMI 2 (DTV)': '91',
            'HDMI 2 (PC)': 'A1',
            'OPS/DVI-D (DTV)': '95',
            'OPS/DVI-D (PC)': 'A5',
            'DisplayPort (DTV)': 'C0',
            'DisplayPort (PC)': 'D0'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID and value in ValueStateValues:
            InputCmdString = 'xb {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            InputCmdString = 'xb {0} FF\r'.format(ID)
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '90': 'HDMI 1 (DTV)',
            'A0': 'HDMI 1 (PC)',
            '91': 'HDMI 2 (DTV)',
            'A1': 'HDMI 2 (PC)',
            '95': 'OPS/DVI-D (DTV)',
            'A5': 'OPS/DVI-D (PC)',
            'C0': 'DisplayPort (DTV)',
            'D0': 'DisplayPort (PC)'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode().upper()]
            self.WriteStatus('Input', value, {'Device ID': str(ID)})
        else:
            self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '10',
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID and value in ValueStateValues:
            KeypadCmdString = 'mc {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def UpdateMasterPower(self, value, qualifier):

        MasterPowerCmdString = 'ka {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('MasterPower', MasterPowerCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Enter': '44',
            'Back': '28',
            'Exit': '5B',
            'Menu': '43'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID and value in ValueStateValues:
            MenuNavigationCmdString = 'mc {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID and value in ValueStateValues:
            PowerCmdString = 'ka {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            if ID != self._DeviceID:
                PowerCmdString = 'ka {0} FF\r'.format(ID)
                self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Power', value, {'Device ID': str(ID)})
        else:
            self.Error(['Power: Invalid/unexpected response'])

    def SetTileMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        column = int(qualifier['Column'])
        row = int(qualifier['Row'])
        if ID and 1 <= column <= 15 and 1 <= row <= 15:
            Value = '{0:X}{1:X}'.format(column, row)
            TileModeCmdString = 'dd {0} {1}\r'.format(ID, Value)
            self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        tileID = int(qualifier['Tile ID'])
        if ID and 1 <= tileID <= 225:
            TilePositionCmdString = 'di {0} {1:02X}\r'.format(ID, tileID)
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetVolume(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID and 0 <= value <= 100:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(ID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            VolumeCmdString = 'kf {0} FF\r'.format(ID)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = int(match.group(2).decode(), 16)
            self.WriteStatus('Volume', value, {'Device ID': str(ID)})
        else:
            self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()

        if 'OK' in response:
            return response
        elif 'NG' in response:
            self.Error(['{}: Error occurred'.format(sourceCmdName)])
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regexSet)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
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

        cmdLookup = {
            'i': 'Tile Position',
            'c': 'Aspect Ratio, Menu Navigation, or Keypad',
            'e': 'Audio Mute',
            'm': 'Executive Mode',
            'b': 'Input',
            'a': 'Power',
            'd': 'Tile Mode',
            'f': 'Volume'
        }

        cmd = cmdLookup[match.group(1).decode().lower()]
        id_ = match.group(2).decode().upper()
        error = match.group(3).decode()
        self.Error(['{0} Error, Device ID {1}: {2}'.format(cmd, id_, error)])

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


class DeviceEthernetClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PowerOff': {'Status': {}},
            'TileMode': {'Parameters': ['Column', 'Row'], 'Status': {}},
            'TilePosition': {'Parameters': ['Tile ID'], 'Status': {}},
            'Volume': {'Status': {}},
        }   

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 1000:
            self._DeviceID = '{0:02X}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full Screen': '02',
            'Original': '06'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'kc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'ke {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = 'km {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1 (DTV)': '90',
            'HDMI 1 (PC)': 'A0',
            'HDMI 2 (DTV)': '91',
            'HDMI 2 (PC)': 'A1',
            'OPS/DVI-D (DTV)': '95',
            'OPS/DVI-D (PC)': 'A5',
            'DisplayPort (DTV)': 'C0',
            'DisplayPort (PC)': 'D0'
        }

        if value in ValueStateValues:
            InputCmdString = 'xb {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '10',
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19'
        }

        if value in ValueStateValues:
            KeypadCmdString = 'mc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Enter': '44',
            'Back': '28',
            'Exit': '5B',
            'Menu': '43'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'mc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = 'ka {0} 00\r'.format(self._DeviceID)
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetTileMode(self, value, qualifier):

        column = int(qualifier['Column'])
        row = int(qualifier['Row'])

        if 0 <= column <= 15 and 0 <= row <= 15:
            Value = '{0:X}{1:X}'.format(column, row)
            TileModeCmdString = 'dd {0} {1}\r'.format(self._DeviceID, Value)
            self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        tileID = int(qualifier['Tile ID'])
        if 1 <= tileID <= 225:
            TilePositionCmdString = 'di {0} {1:02X}\r'.format(self._DeviceID, tileID)
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')
            
    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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
