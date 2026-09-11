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
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoLevel': {'Status': {}},
            'Bass': {'Status': {}},
            'Input': {'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'Multizone': {'Status': {}},
            'Paging': {'Parameters': ['Zone'], 'Status': {}},
            'PagingActive': {'Parameters': ['Zone'], 'Status': {}},
            'Power': {'Status': {}},
            'Treble': {'Status': {}},
            'Zonelink': {'Status': {}},
            'ZoneMicLevel': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneMusicLevel': {'Parameters': ['Zone'], 'Status': {}},
        }        

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'AUTOLD (ON|OFF)\r'), self.__MatchAutoLevel, None)
            self.AddMatchString(re.compile(b'EQBASS (-?[0-9]{1,2})\r'), self.__MatchBass, None)
            self.AddMatchString(re.compile(b'SELECT (A|B|C|D)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'IPGAIN (A|B|C|D) (-?[0-9]{1,2})\r'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'MULTIZONE (ON|OFF)\r'), self.__MatchMultizone, None)
            self.AddMatchString(re.compile(b'PAGING (ZONE)?(1|2)?\s?(ON|OFF)\r'), self.__MatchPaging, None)
            self.AddMatchString(re.compile(b'PAGACT (ZONE)?(1|2)?\s?(ON|OFF)\r'), self.__MatchPagingActive, None)
            self.AddMatchString(re.compile(b'EQTREB (-?[0-9]{1,2})\r'), self.__MatchTreble, None)
            self.AddMatchString(re.compile(b'ZONELINK (ON|OFF)\r'), self.__MatchZonelink, None)
            self.AddMatchString(re.compile(b'MICLVL (ZONE)?(1|2)?\s?(OFF|-?[0-9]{1,2})\r'), self.__MatchZoneMicLevel, None)
            self.AddMatchString(re.compile(b'MSCLVL (ZONE)?(1|2)?\s?(OFF|-?[0-9]{1,2})\r'), self.__MatchZoneMusicLevel, None)
            self.AddMatchString(re.compile(b'ERROR: (Command Unknown!|Unknown Attribute!|No Header!|Unknown Instruction!|Value Invalid!|Zone Invalid!|AMPLIFIER PROTECT!|OVER TEMPERATURE!)\r'), self.__MatchError, None)

        self.Init(None, None)
           
    def Init(self, value, qualifier):

        self.Send('>SET HEADER 0\r')
        self.Send('>SET ECHO 0\r')
        self.Send('>SET LF 0\r')
        self.Send('>SET BS 0\r')

        self.Send('SET HEADER 0\r')
        self.Send('SET ECHO 0\r')
        self.Send('SET LF 0\r')
        self.Send('SET BS 0\r')

    def SetAutoLevel(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AutoLevelCmdString = 'SET AUTOLD {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoLevel', AutoLevelCmdString, value, qualifier)

    def UpdateAutoLevel(self, value, qualifier):

        AutoLevelCmdString = 'GET AUTOLD\r'
        self.__UpdateHelper('AutoLevel', AutoLevelCmdString, value, qualifier)

    def __MatchAutoLevel(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoLevel', value, None)

    def SetBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -14,
            'Max': 14
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BassCmdString = 'SET EQBASS {0}\r'.format(value)
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        BassCmdString = 'GET EQBASS\r'
        self.__UpdateHelper('Bass', BassCmdString, value, qualifier)

    def __MatchBass(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Bass', value, None)

    def SetInput(self, value, qualifier):

        if value in ('A', 'B', 'C', 'D'):
            InputCmdString = 'SET SELECT {0}\r'.format(value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'GET SELECT\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def SetInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -20,
            'Max': 14
        }

        input = qualifier['Input']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and (input in ['A', 'B', 'C', 'D']):
            InputGainCmdString = 'SET IPGAIN {0} {1}\r'.format(input, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        input = qualifier['Input']
        if input in ['A', 'B', 'C', 'D']:
            InputGainCmdString = 'GET IPGAIN {0}\r'.format(input)
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('InputGain', value, qualifier)

    def SetMultizone(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        MultizoneCmdString = 'SET MULTIZONE {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Multizone', MultizoneCmdString, value, qualifier)

    def UpdateMultizone(self, value, qualifier):

        MultizoneCmdString = 'GET MULTIZONE\r'
        self.__UpdateHelper('Multizone', MultizoneCmdString, value, qualifier)

    def __MatchMultizone(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Multizone', value, None)

    def __MatchPaging(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        if not match.group(1):
            qualifier = {}
            qualifier['Zone'] = 'Multizone Off'
            value = ValueStateValues[match.group(3).decode()]
        else:
            qualifier = {}
            qualifier['Zone'] = match.group(2).decode()
            value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('Paging', value, qualifier)

    def SetPagingActive(self, value, qualifier):

        ZoneStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        zone = qualifier['Zone']
        multizone = self.ReadStatus('Multizone', None)
        if multizone is None:
            multizone = 'Off'
        PagingCmdString = None
        if (multizone == 'On') and (zone in ['1', '2']):
            PagingCmdString = 'SET PAGACT ZONE{0} {1}\r'.format(zone, ValueStateValues[value])
        elif (multizone == 'Off') and (zone == 'Multizone Off'):
            PagingCmdString = 'SET PAGACT {0}\r'.format(ValueStateValues[value])
        if PagingCmdString:
            self.__SetHelper('PagingActive', PagingCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPagingActive')

    def UpdatePagingActive(self, value, qualifier):

        zone = qualifier['Zone']        
        multizone = self.ReadStatus('Multizone', None)
        if multizone is None:
            multizone = 'Off'
        PagingCmdString = None
        if (multizone == 'On') and (zone in ['1', '2']):
            PagingCmdString = 'GET PAGACT ZONE{0}\r'.format(zone)
            self.__UpdateHelper('PagingActive', PagingCmdString, value, qualifier)
        elif (multizone == 'Off') and (zone == 'Multizone Off'):
            PagingCmdString = 'GET PAGACT\r'
            self.__UpdateHelper('PagingActive', PagingCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdatePagingActive')

    def __MatchPagingActive(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        if not match.group(1):
            qualifier = {}
            qualifier['Zone'] = 'Multizone Off'
            value = ValueStateValues[match.group(3).decode()]
        else:
            qualifier = {}
            qualifier['Zone'] = match.group(2).decode()
            value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('PagingActive', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        PowerCmdString = 'SET STANDBY {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': -14,
            'Max': 14
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TrebleCmdString = 'SET EQTREB {0}\r'.format(value)
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        TrebleCmdString = 'GET EQTREB\r'
        self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)

    def __MatchTreble(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Treble', value, None)

    def SetZonelink(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ZonelinkCmdString = 'SET ZONELINK {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Zonelink', ZonelinkCmdString, value, qualifier)

    def UpdateZonelink(self, value, qualifier):

        ZonelinkCmdString = 'GET ZONELINK\r'
        self.__UpdateHelper('Zonelink', ZonelinkCmdString, value, qualifier)

    def __MatchZonelink(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zonelink', value, None)

    def SetZoneMicLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 0
        }

        zone = qualifier['Zone']
        multizone = self.ReadStatus('Multizone', None)
        if multizone is None:
            multizone = 'Off'
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ZoneMicLevelCmdString = None
            if (multizone == 'On') and (zone in ['1', '2']):
                ZoneMicLevelCmdString = 'SET MICLVL ZONE{0} {1}\r'.format(zone, value)
            elif (multizone == 'Off') and (zone == 'Multizone Off'):
                ZoneMicLevelCmdString = 'SET MICLVL {0}\r'.format(value)
            if ZoneMicLevelCmdString:
                self.__SetHelper('ZoneMicLevel', ZoneMicLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoneMicLevel')

    def UpdateZoneMicLevel(self, value, qualifier):

        zone = qualifier['Zone']
        multizone = self.ReadStatus('Multizone', None)
        if multizone is None:
            multizone = 'Off'
        if (multizone == 'On') and (zone in ['1', '2']):
            ZoneMicLevelCmdString = 'GET MICLVL ZONE{0}\r'.format(zone)
            self.__UpdateHelper('ZoneMicLevel', ZoneMicLevelCmdString, value, qualifier)
        elif (multizone == 'Off') and (zone == 'Multizone Off'):
            ZoneMicLevelCmdString = 'GET MICLVL\r'
            self.__UpdateHelper('ZoneMicLevel', ZoneMicLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateZoneMicLevel')

    def __MatchZoneMicLevel(self, match, tag):

        if not match.group(1):
            qualifier = {}
            qualifier['Zone'] = 'Multizone Off'
            if match.group(3).decode() == 'OFF':
                value = -80
            else:
                value = int(match.group(3).decode())
            self.WriteStatus('ZoneMicLevel', value, qualifier)
        else:
            qualifier = {}
            qualifier['Zone'] = match.group(2).decode()
            if match.group(3).decode() == 'OFF':
                value = -80
            else:
                value = int(match.group(3).decode())
            self.WriteStatus('ZoneMicLevel', value, qualifier)

    def SetZoneMusicLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 0
        }

        zone = qualifier['Zone']
        multizone = self.ReadStatus('Multizone', None)
        if multizone is None:
            multizone = 'Off'
        zonelink = self.ReadStatus('Zonelink', None)
        if zonelink is None:
            zonelink = 'Off'
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ZoneMusicLevelCmdString = None
            if (multizone == 'On') and (zonelink == 'Off') and (zone in ['1', '2']):
                ZoneMusicLevelCmdString = 'SET MSCLVL ZONE{0} {1}\r'.format(zone, value)
            elif zone == 'Multizone Off':
                ZoneMusicLevelCmdString = 'SET MSCLVL {0}\r'.format(value)
            if ZoneMusicLevelCmdString:
                self.__SetHelper('ZoneMusicLevel', ZoneMusicLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoneMusicLevel')

    def UpdateZoneMusicLevel(self, value, qualifier):

        zone = qualifier['Zone']
        multizone = self.ReadStatus('Multizone', None)
        if multizone is None:
            multizone = 'Off'
        zonelink = self.ReadStatus('Zonelink', None)
        if zonelink is None:
            zonelink = 'Off'
        if (multizone == 'On') and (zonelink == 'Off') and (zone in ['1', '2']):
            ZoneMusicLevelCmdString = 'GET MSCLVL ZONE{0}\r'.format(zone)
            self.__UpdateHelper('ZoneMusicLevel', ZoneMusicLevelCmdString, value, qualifier)
        elif zone == 'Multizone Off':
            ZoneMusicLevelCmdString = 'GET MSCLVL\r'
            self.__UpdateHelper('ZoneMusicLevel', ZoneMusicLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateZoneMusicLevel')

    def __MatchZoneMusicLevel(self, match, tag):

        if not match.group(1):
            qualifier = {}
            qualifier['Zone'] = 'Multizone Off'
            if match.group(3).decode() == 'OFF':
                value = -80
            else:
                value = int(match.group(3).decode())
            self.WriteStatus('ZoneMusicLevel', value, qualifier)
        else:
            qualifier = {}
            zone = match.group(2).decode()
            qualifier['Zone'] = zone
            if match.group(3).decode() == 'OFF':
                value = -80
            else:
                value = int(match.group(3).decode())
            self.WriteStatus('ZoneMusicLevel', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        ERROR_CODES = {
            'Command Unknown!': 'Wrong spelling of command or command started with Back Space character',
            'Unknown Attribute!': 'Wrong spelling of attribute.',
            'No Header!': 'When HEADER is on and ECHO is off, each instruction must be started with header.',
            'Unknown Instruction!': 'A command was used with an attribute that does not support this',
            'Value Invalid!': 'A value was out of range or illegal',
            'Zone Invalid!': 'No valid zone was specified',
            'AMPLIFIER PROTECT!': 'Amplifier Protect',
            'OVER TEMPERATURE!': 'Over Temperature'
        }
        print('ERROR_CODES[match.group(1).decode()] for', command)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.Init(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
            print(command)
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
