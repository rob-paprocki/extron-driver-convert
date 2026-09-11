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

        self.deviceUsername = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'ReadControlUnitZoneIntensities': {'Parameters': ['Control Unit', 'Zone'], 'Status': {}},
            'SceneLock': {'Parameters': ['Control Unit'], 'Status': {}},
            'SceneStatus': {'Parameters': ['Control Unit'], 'Status': {}},
            'SetControlUnitZoneIntensities': {'Parameters': ['Control Unit', 'Fade Time Duration', 'Fade Time Units', 'Zone'], 'Status': {}},
            'SelectScene': {'Parameters': ['Control Unit'], 'Status': {}},
            'Sequence': {'Parameters': ['Control Unit'], 'Status': {}},
            'ZoneLock': {'Parameters': ['Control Unit'], 'Status': {}},
            'ZoneLowerRaise': {'Parameters': ['Control Unit', 'Zone'], 'Status': {}},
            'ZoneLowerRaiseStop': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'login: '), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b':v (.*) (model|OK)'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'~:zi ([1-8]) (\S+ \S+ \S+ \S+ \S+ \S+ \S+ \S+) 1 OK\r{1,2}\n'), self.__MatchReadControlUnitZoneIntensities, None)
            self.AddMatchString(re.compile(b'~:ss ([M0123456789ABCDEFG]{8}) 1 OK\r{1,2}\n'), self.__MatchSceneStatus, None)
            self.AddMatchString(re.compile(b'~ERROR6 0 OK\r'), self.__MatchError, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchUsername(self, match, qualifier):
        self.SetUsername(None, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        self.__UpdateHelper('FirmwareVersion', ':V\r\n', value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value=match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)


    def SetSelectScene(self, value, qualifier):

        CU=int(qualifier['Control Unit'])

        Scene={
                '0': '0',
                '1': '1',
                '2': '2',
                '3': '3',
                '4': '4',
                '5': '5',
                '6': '6',
                '7': '7',
                '8': '8',
                '9': '9',
                '10': 'A',
                '11': 'B',
                '12': 'C',
                '13': 'D',
                '14': 'E',
                '15': 'F',
                '16': 'G'
                }

        if 1 <= CU <= 8:
            CmdString=':A{}{}\r\n'.format(Scene[value], CU)
            self.__SetHelper('SelectScene', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelectScene')

    def SetSceneLock(self, value, qualifier):

        CU=int(qualifier['Control Unit'])

        States={
            'Add': '+',
            'Remove': '-'
        }

        if 1 <= CU <= 8:
            CmdString=':SL{}{}\r\n'.format(States[value], CU)
            self.__SetHelper('SceneLock', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneLock')

    def UpdateSceneStatus(self, value, qualifier):

        self.__UpdateHelper('SceneStatus', ':G\r\n', value, qualifier)

    def __MatchSceneStatus(self, match, tag):

        Response=match.group(1).decode()

        Values={
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            'A': '10',
            'B': '11',
            'C': '12',
            'D': '13',
            'E': '14',
            'F': '15',
            'G': '16',
            'M': 'Missing'
        }

        for CU in range(1, 9):
            self.WriteStatus('SceneStatus', Values[Response[CU - 1]], {'Control Unit': str(CU)})

    def SetSequence(self, value, qualifier):

        CU=qualifier['Control Unit']

        States={
            'Add': '+',
            'Remove': '-'
        }

        if 1 <= int(CU) <= 8:
            CmdString=':SL{}{}\r\n'.format(States[value], CU)
            self.__SetHelper('Sequence', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequence')

    def SetZoneLock(self, value, qualifier):

        CU=qualifier['Control Unit']

        States={
            'Add': '+',
            'Remove': '-'
        }

        if 1 <= int(CU) <= 8:
            CmdString=':ZL{}{}\r\n'.format(States[value], CU)
            self.__SetHelper('ZoneLock', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneLock')

    def SetZoneLowerRaise(self, value, qualifier):

        CU=int(qualifier['Control Unit'])
        Zone=qualifier['Zone']

        if Zone == 'All':
            Value={'Lower': 'D', 'Raise': 'B'}[value]
            CmdString=':{}{}\r\n'.format(Value, CU)
            self.__SetHelper('ZoneLowerRaise', CmdString, value, qualifier)

        elif 1 <= CU <= 8 and 0 <= int(Zone) <= 8:
            Value={'Lower': 'D', 'Raise': 'B'}[value]
            CmdString=':{}{}{}\r\n'.format(Value, CU, Zone)
            self.__SetHelper('ZoneLowerRaise', CmdString, value, qualifier)
        else:
            self.Error(['Invalid Command'])

    def SetZoneLowerRaiseStop(self, value, qualifier):

        if value == 'Lower Stop':
            self.__SetHelper('ZoneLowerRaiseStop', ':E\r\n', value, qualifier)
        elif value == 'Raise Stop':
            self.__SetHelper('ZoneLowerRaiseStop', ':C\r\n', value, qualifier)


    def SetSetControlUnitZoneIntensities(self, value, qualifier):

        CU=int(qualifier['Control Unit'])
        Zone=int(qualifier['Zone'])
        FTDur=int(qualifier['Fade Time Duration'])
        FTUnit=qualifier['Fade Time Units']
        FadeTime = None
        Placeholders = None
        Intensity = None
        if FTUnit == 'Minutes' and FTDur == 0:
            FadeTime=0x00
        elif FTUnit == 'Seconds' and FTDur == 60:
            FadeTime=0x3C
        elif FTUnit == 'Seconds' and 0 <= FTDur <= 59:
            FadeTime=hex(FTDur)[2:]
        elif FTUnit == 'Minutes' and 1 <= FTDur <= 60:
            FadeTime=hex(FTDur + 59)[2:]

        if 1 <= CU <= 8 and 1 <= Zone <= 8 and 0 <= value <= 99:
            Placeholders=' *' * (Zone - 1)
            if value == 0:
                Intensity=0
            else:
                Intensity=hex(int(value * 1.2796) + 1)[2:].upper()
        if FadeTime and Placeholders and Intensity:
            CmdString=': szi {} {}{} {}\r\n'.format(CU, FadeTime, Placeholders, Intensity)
            self.__SetHelper('SetControlUnitZoneIntensities', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetControlUnitZoneIntensities')

    def UpdateReadControlUnitZoneIntensities(self, value, qualifier):

        CU=int(qualifier['Control Unit'])
        if 1 <= CU <= 8:
            CmdString=':rzi {}\r\n'.format(CU)
            self.__UpdateHelper('ReadControlUnitZoneIntensities', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateReadControlUnitZoneIntensities')

    def __MatchReadControlUnitZoneIntensities(self, match, tag):

        CU=match.group(1).decode()
        Response=match.group(2).decode().split()

        for Zone in range(1, 9):
            HexVal=int(Response[Zone - 1], 16)
            Value=int(HexVal / 1.2796)
            if 0 <= Value <= 99:
                self.WriteStatus('ReadControlUnitZoneIntensities', Value, {'Control Unit': CU, 'Zone': str(Zone)})

    def __MatchError(self, match, tag):

        Errors={
                  '1': 'Control Unit Raise/Lower error',
                  '2': 'Invalid scene selected',
                  '6': 'Bad command was sent',
                  '13': 'Not a timeclock unit (GRX-ATC or GRX-PRG)',
                  '14': 'Illegal time was entered',
                  '15': 'Invalid schedule',
                  '16': 'No Super Sequence has been loaded',
                  '20': 'Command was missing Control Units',
                  '21': 'Command was missing data',
                  '22': 'Error in command argument (improper hex value)',
                  '24': 'Invalid Control Unit',
                  '25': 'Invalid value, outside range of acceptable values',
                  '26': 'Invalid Accessory Control',
                  '31': 'Network address illegally formatted; 4 octets required (xxx.xxx.xxx.xxx)',
                  '80': 'Time-out error, no response received',
                  '100': 'Invalid Telnet login number',
                  '101': 'Invalid Telnet login',
                  '102': 'Telnet login name exceeds 8 characters',
                  '103': 'Invalid number of arguments',
                  '255': 'GRX-PRG must be in programming mode for specific commands',
                  }

        value=Errors[match.group(1).decode()]
        self.Error([value])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug=True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk=False

            self.counter=self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag=True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter=0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag=False

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

	# Send Control Commands
    def Set(self, command, value, qualifier=None):
        method=getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method=getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command=self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command]={'method': {}}

            Subscribe=self.Subscription[command]
            Method=Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method=Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]]={}
                            Method=Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback']=callback
            Method['qualifier']=qualifier
        else:
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription:
            Subscribe=self.Subscription[command]
            Method=Subscribe['method']
            Command=self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method=Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter=0
        if not self.connectionFlag:
            self.OnConnected()
        Command=self.Commands[command]
        Status=Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status=Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]]={}
                        Status=Status[qualifier[Parameter]]
                    else:
                        return
        try:
            if Status['Live'] != value:
                Status['Live']=value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live']=value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command=self.Commands[command]
        Status=Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status=Status[qualifier[Parameter]]
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
            self._ReceiveBuffer=b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string]={'callback': callback, 'para': arg}

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result=re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer=self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType='Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo='Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])


class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType='Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo='IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType='Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo='IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()