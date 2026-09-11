from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import ProgramLog

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self._compile_list = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.Debug = False
        self.Models = {}
        
        self.deviceUsername = None
        self.devicePassword = None

        self.Commands = {
            'InputGain': {'Parameters': ['Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'LoadPreset': {'Status': {}},
            'OutputGain': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'SelectPreset': {'Status': {}},
            'Standby': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Login:'), self.__MatchLogin, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)

    def __MatchLogin(self, match, qualifier):
        self.SetLogin(None, None)

    def SetLogin(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send(self.deviceUsername + '\r\n')
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, qualifier):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualfiier):
        if self.devicePassword is not None:
            self.Send(b'\xFF\xFC\x2D')
            self.Send(self.devicePassword + '\r\n')
        else:
            self.MissingCredentialsLog('Password')

    def SetInputGain(self, value, qualifier):

        InVal = int(qualifier['Channel'])

        if -47.5 <= value <= 12 and 1 <= InVal <= 2:
            Gain = int(value * 100)
            InVal -= 1
            CmdString = 'm1\r\nn1\r\nc{0}\r\nv{1}\r\ne\r\n'.format(InVal, Gain)
            self.__SetHelper('InputGain', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetInputMute(self, value, qualifier):

        InVal = int(qualifier['Channel'])

        States = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= InVal <= 2:
            InVal -= 1
            CmdString = 'm2\r\nn2\r\nc{0}\r\nv{1}\r\ne\r\n'.format(InVal, States[value])
            self.__SetHelper('InputMute', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetLoadPreset(self, value, qualifier):

        CmdString = 'm3\r\nn3\r\ni1\r\ne\r\n'
        self.__SetHelper('LoadPreset', CmdString, value, qualifier)

    def SetOutputGain(self, value, qualifier):

        OutVal = int(qualifier['Channel'])

        if -47.5 <= value <= 12 and 1 <= OutVal <= 2:
            Gain = int(value * 100)
            OutVal += 127
            CmdString = 'm1\r\nn1\r\nc{0}\r\nv{1}\r\ne\r\n'.format(OutVal, Gain)
            self.__SetHelper('OutputGain', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetOutputMute(self, value, qualifier):

        OutVal = int(qualifier['Channel'])

        States = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= OutVal <= 2:
            OutVal += 127
            CmdString = 'm2\r\nn2\r\nc{0}\r\nv{1}\r\ne\r\n'.format(OutVal, States[value])
            self.__SetHelper('OutputMute', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetSelectPreset(self, value, qualifier):

        if 1 <= int(value) <= 100:
            CmdString = 'm4\r\nn4\r\nv{0}\r\ne\r\n'.format(int(value))
            self.__SetHelper('SelectPreset', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetStandby(self, value, qualifier):

        States = {
            'Enter': 'm3\r\nn3\r\ni4\r\ne\r\n',
            'Exit': 'm3\r\nn3\r\ni5\r\ne\r\n'
        }

        self.__SetHelper('Standby', States[value], value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')


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
