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
            'AVMute': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'=SER:(0|1|4|8|16)\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'=SIS:(3|5|6|7|9|10)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'=SLT:([0-9]{1,4}).*?\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'=STT:([0-9]{1,5}).*?\r'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'=SPS:(0|1|5|7)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'[#=](MUT|SIS|SLT|STT|PIC|SPS|VVL):ER0\r'), self.__MatchError, None)

    def SetAVMute(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '#MUT:{0}\r'.format(States[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        self.__UpdateHelper('DeviceStatus', '#SER\r', value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        States = {
            '0': 'No Error',
            '1': 'Lamp Error',
            '4': 'Fan Error',
            '8': 'Temp Error',
            '16': 'CW Error'
        }

        self.WriteStatus('DeviceStatus', States[match.group(1).decode()], None)

    def SetInput(self, value, qualifier):

        States = {
            'Computer 1': '3',
            'Computer 2': '5',
            'HDMI 1': '6',
            'HDMI 2': '7',
            'Video': '9',
            'S-Video': '10'
        }

        self.__SetHelper('Input', '#INP:{0}\r'.format(States[value]), value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '#SIS\r', value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            '3': 'Computer 1',
            '5': 'Computer 2',
            '6': 'HDMI 1',
            '7': 'HDMI 2',
            '9': 'Video',
            '10': 'S-Video'
        }

        self.WriteStatus('Input', States[match.group(1).decode()], None)

    def UpdateLampUsage(self, value, qualifier):

        self.__UpdateHelper('LampUsage', '#SLT\r', value, qualifier)

    def __MatchLampUsage(self, match, tag):
        self.WriteStatus('LampUsage', int(match.group(1).decode()), None)

    def UpdateOperationHours(self, value, qualifier):

        self.__UpdateHelper('OperationHours', '#STT\r', value, qualifier)

    def __MatchOperationHours(self, match, tag):
        self.WriteStatus('OperationHours', int(match.group(1).decode()), None)

    def SetPictureMode(self, value, qualifier):

        States = {
            'Bright': '0',
            'Standard': '1',
            'Natural': '2'
        }

        self.__SetHelper('PictureMode', '#PIC:{0}\r'.format(States[value]), value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On': '#PON\r',
            'Off': '#POF\r',
        }

        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):
        self.__UpdateHelper('Power', '#SPS\r', value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '5': 'On',
            '0': 'Off',
            '1': 'Warming Up',
            '7': 'Cooling Down'
        }
        self.WriteStatus('Power', States[match.group(1).decode()], None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 20:
            self.__SetHelper('Volume', '#VVL:{}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:

            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):

        State = {
            'MUT': 'AV Mute',
            'SIS': 'Input',
            'SLT': 'Lamp Usage',
            'STT': 'Operation Hours',
            'PIC': 'Picture Mode',
            'SPS': 'Power',
            'VVL': 'Volume',
        }

        self.Error(['Command {0} is Invalid'.format(State[match.group(1).decode()])])

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
