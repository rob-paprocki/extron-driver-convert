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
        self._DeviceID = '001'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteControlLock': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x0F\d{3}KPL#(-ON|OFF)#\x0D'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x0F\d{3}MIN#(DVI|-DP|-PC|HDM)#\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x0F\d{3}PWR#(-ON|OFF)#\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x0F\d{3}RML#(-ON|OFF)#\x0D'), self.__MatchRemoteControlLock, None)
            self.AddMatchString(re.compile(b'\x0F\d{3}([A-Z]{3})ERROR\x0D'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 100:
            self._DeviceID = '{0:03d}'.format(int(value))
        else:
            self.Error(['Device ID should be between 1 to 100.'])

    def SetPower(self, value, qualifier):

        States = {
            'On': '-ON',
            'Off': 'OFF'
        }

        CmdString = '\x0F{}PWRW{}0\x0D'.format(self._DeviceID, States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        CmdString = '\x0F{}PWRR0000\x0D'.format(self._DeviceID)
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '-ON': 'On',
            'OFF': 'Off'
        }

        self.WriteStatus('Power', States[match.group(1).decode()], None)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '-ON',
            'Off': 'OFF'
        }

        CmdString = '\x0F{}KPLW{}0\x0D'.format(self._DeviceID, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        CmdString = '\x0F{}KPLR0000\x0D'.format(self._DeviceID)
        self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        States = {
            '-ON': 'On',
            'OFF': 'Off'
        }

        self.WriteStatus('ExecutiveMode', States[match.group(1).decode()], None)

    def SetRemoteControlLock(self, value, qualifier):

        States = {
            'On': '-ON',
            'Off': 'OFF'
        }

        CmdString = '\x0F{}RMLW{}0\x0D'.format(self._DeviceID, States[value])
        self.__SetHelper('RemoteControlLock', CmdString, value, qualifier)

    def UpdateRemoteControlLock(self, value, qualifier):
        CmdString = '\x0F{}RMLR0000\x0D'.format(self._DeviceID)
        self.__UpdateHelper('RemoteControlLock', CmdString, value, qualifier)

    def __MatchRemoteControlLock(self, match, tag):

        States = {
            '-ON': 'On',
            'OFF': 'Off'
        }

        self.WriteStatus('RemoteControlLock', States[match.group(1).decode()], None)

    def SetInput(self, value, qualifier):

        States = {
            'DVI': 'DVI',
            'DisplayPort': '-DP',
            'PC': '-PC',
            'HDMI': 'HDM'
        }

        CmdString = '\x0F{}MINW{}0\x0D'.format(self._DeviceID, States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        CmdString = '\x0F{}MINR0000\x0D'.format(self._DeviceID)
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            'DVI': 'DVI',
            '-DP': 'DisplayPort',
            '-PC': 'PC',
            'HDM': 'HDMI'
        }

        self.WriteStatus('Input', States[match.group(1).decode()], None)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu': 'MEN',
            'Source': 'SOU',
            'Left': 'LEF',
            'Right': 'RIG',
            'Enter': 'ENT',
            'Up': '-UP',
            'Down': 'DOW',
            'Exit': 'EXI'
        }

        CmdString = '\x0F{}RMTW{}0\x0D'.format(self._DeviceID, States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

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

        Commands = {
            'PWR': 'Power',
            'KPL': 'Executive Mode',
            'RML': 'Remote Control Lock',
            'MIN': 'Input',
            'RMT': 'Menu Navigation',
        }

        ErrorStr = 'Error: {0}'.format(Commands[match.group(1).decode()])
        self.Error([ErrorStr])

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
