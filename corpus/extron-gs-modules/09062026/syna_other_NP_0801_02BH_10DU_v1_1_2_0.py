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
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'NP-02B': self.syna_31_1717_02,
            'NP-0801DTG2': self.syna_31_1717_08_dual,
            'NP-0801DTH': self.syna_31_1717_08_single,
            'NP-0801DTHG2': self.syna_31_1717_08_dual,
            'NP-0801DT': self.syna_31_1717_08_single,
            'NP-02BH': self.syna_31_1717_02,
            'NP-1601DT': self.syna_31_1717_16_dual,
            'NP-1601DTH': self.syna_31_1717_16_dual,
            'NP-1601DTA20': self.syna_31_1717_16_single,
            'NP-1601DTA30': self.syna_31_1717_16_single,
            'NPB-20DT': self.syna_31_1717_20,
            'NP-0801DUH': self.syna_31_1717_08_single,
            'NP-10DU': self.syna_31_1717_10,
            'NP-10DUH': self.syna_31_1717_10,
            'NP-0202DT': self.syna_31_1717_02,
            'NP-0201DT': self.syna_31_1717_02,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ACCurrentDrawDual': {'Parameters': ['Outlet'], 'Status': {}},
            'ACCurrentDrawSingle': {'Status': {}},
            'ACMaxDrawDual': {'Parameters': ['Outlet'], 'Status': {}},
            'ACMaxDrawSingle': {'Status': {}},
            'Login': {'Parameters': ['Username', 'Password'], 'Status': {}},
            'Logout': {'Status': {}},
            'OutletPower': {'Parameters': ['Port'], 'Status': {}},
            'OutletStatus': {'Parameters': ['Port'], 'Status': {}},
            'RebootOutlet': {'Status': {}},
            'RequiredPolling': {'Status': {}},
            'Temperature': {'Parameters': ['Unit'], 'Status': {}},
        }


        if self.Unidirectional == 'False':
            if 'Serial' in self.ConnectionType:
                self.AddMatchString(re.compile(b'Telnet is active.'), self.__MatchDisableTelnet, None)
            self.AddMatchString(re.compile(b'AC current draw ([12]): (\d{1,2}\.\d{2})\. Max detected (\d{1,2}\.\d{2}) Amps\.'), self.__MatchACCurrentDraw, None)
            self.AddMatchString(re.compile(b'\$A5([01]{2})|\$A5\r[\s\S]+?,([01]{2,20}),'), self.__MatchOutletStatus, None)
            self.AddMatchString(re.compile(b'Environment Temperature: (\d+)(C)\. (\d+)(F)\.\r\n|Temperature Probe is not installed\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'\$AF|Invalid command\r\n'), self.__MatchError, None)

    def __MatchDisableTelnet(self, match, tag):

        self.DisableTelnet(None, None)

    def DisableTelnet(self, value, qualifier):
        self.Send('!\r')

    def __MatchACCurrentDraw(self, match, tag):

        currentDraw = match.group(2).decode()
        maxDraw = match.group(3).decode()
        if self.modelType == 'Dual':
            self.WriteStatus('ACCurrentDrawDual', currentDraw, {'Outlet': match.group(1).decode()})
            self.WriteStatus('ACMaxDrawDual', maxDraw, {'Outlet': match.group(1).decode()})
        else:
            self.WriteStatus('ACCurrentDrawSingle', currentDraw, None)
            self.WriteStatus('ACMaxDrawSingle', maxDraw, None)

    def UpdateACCurrentDrawDual(self, value, qualifier):

        ACCurrentDrawDualCmdString = 'cs 1\r\n'
        self.__UpdateHelper('ACCurrentDrawDual', ACCurrentDrawDualCmdString, value, qualifier)

    def UpdateACMaxDrawDual(self, value, qualifier):
        self.UpdateACCurrentDrawDual(value, qualifier)

    def UpdateACCurrentDrawSingle(self, value, qualifier):
        ACCurrentDrawSingleCmdString = 'cs 1\r\n'
        self.__UpdateHelper('ACCurrentDrawSingle', ACCurrentDrawSingleCmdString, value, qualifier)

    def UpdateACMaxDrawSingle(self, value, qualifier):
        self.UpdateACCurrentDrawSingle(value, qualifier)

    def SetLogin(self, value, qualifier):

        LoginCmdString = '$A1 {0} {1}\r\n'.format(qualifier['Username'], qualifier['Password'])
        self.__SetHelper('Login', LoginCmdString, value, qualifier)

    def SetLogout(self, value, qualifier):

        LogoutCmdString = '$A2\r\n'
        self.__SetHelper('Logout', LogoutCmdString, value, qualifier)

    def SetOutletPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        OutletPowerCmdString = ''
        if qualifier['Port'] == 'All':
            OutletPowerCmdString = '$A7 {}\r\n'.format(ValueStateValues[value])
        elif 1 <= int(qualifier['Port']) <= self.portCount:
            OutletPowerCmdString = '$A3 {0} {1}\r\n'.format(qualifier['Port'], ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetOutletPower')

        if OutletPowerCmdString:
            self.__SetHelper('OutletPower', OutletPowerCmdString, value, qualifier)

    def SetRebootOutlet(self, value, qualifier):

        if 1 <= int(value) <= self.portCount:
            RebootOutletCmdString = '$A4 {0}\r\n'.format(value)
            self.__SetHelper('RebootOutlet', RebootOutletCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRebootOutlet')

    def UpdateOutletStatus(self, value, qualifier):

        RequiredPollingCmdString = '$A5\r\n'
        self.__UpdateHelper('OutletStatus', RequiredPollingCmdString, value, qualifier)

    def __MatchOutletStatus(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if match.group(1):
            res = match.group(1).decode()[::-1]  # Reverse the string, response for On/Off is backwards
        else:
            res = match.group(2).decode()[::-1]

        for i in range(0, self.portCount):
            value = ValueStateValues[res[i]]
            self.WriteStatus('OutletStatus', value, {'Port': str(i + 1)})

    def UpdateTemperature(self, value, qualifier):
        TemperatureCmdString = 'cs 1\r\n'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        if 'Temperature Probe is not installed' in match.group(0).decode():
            self.WriteStatus('Temperature', 'N/A', {'Unit': 'Celsius'})
            self.WriteStatus('Temperature', 'N/A', {'Unit': 'Fahrenheit'})
        else:
            UnitStates = {
                'F': 'Fahrenheit',
                'C': 'Celsius'
            }
            self.WriteStatus('Temperature', match.group(1).decode(), {'Unit': UnitStates[match.group(2).decode()]})
            self.WriteStatus('Temperature', match.group(3).decode(), {'Unit': UnitStates[match.group(4).decode()]})

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
        self.Error(['Error: Unknown/Invalid Command'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.lastCurrentUpdate = 0

    def syna_31_1717_02(self):

        self.portCount = 2
        self.modelType = 'Single'

    def syna_31_1717_08_single(self):

        self.portCount = 8
        self.modelType = 'Single'

    def syna_31_1717_08_dual(self):

        self.portCount = 8
        self.modelType = 'Dual'

    def syna_31_1717_10(self):

        self.portCount = 10
        self.modelType = 'Single'

    def syna_31_1717_16_single(self):

        self.portCount = 16
        self.modelType = 'Single'

    def syna_31_1717_16_dual(self):

        self.portCount = 16
        self.modelType = 'Dual'

    def syna_31_1717_20(self):

        self.portCount = 20
        self.modelType = 'Single'
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

