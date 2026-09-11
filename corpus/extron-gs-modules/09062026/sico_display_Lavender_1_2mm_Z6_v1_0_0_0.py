from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


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
        self.DeviceID = 'Broadcast'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Brightness': {'Status': {}},
            'ColorTemperature': {'Status': {}},
            'Heartbeat': {'Status': {}},
            'Input': {'Status': {}},
            'LoadPreset': {'Status': {}},
            'Show': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x99\x99\x04\x00'), self.__MatchHeartbeat, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        device_id_map = {
            'Broadcast': b'\xFF\xFF',
            'First Z6': b'\x00\x00',
            'Second Z6': b'\x00\x01'
        }
        try:
            self._DeviceID = device_id_map[value]
        except KeyError:
            self.Error(['Invalid Device ID.'])

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Brightness', b''.join([b'\x21\x00\x14\x00\x00\x00', self._DeviceID, b'\xFF\x00\x00\x00\x00\x00\x00\x00', pack('<f', value)]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetColorTemperature(self, value, qualifier):

        if 2000 <= value <= 10000:
            self.__SetHelper('ColorTemperature', b''.join([b'\x22\x00\x12\x00\x00\x00', self._DeviceID, b'\xFF\x00\x00\x00\x00\x00\x00\x00', pack('<h', value)]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorTemperature')

    def UpdateHeartbeat(self, value, qualifier):

        self.__UpdateHelper('Heartbeat', b'\x99\x99\x04\x00', value, qualifier)

    def __MatchHeartbeat(self, match, tag):
        self.WriteStatus('Heartbeat', 'Good Response', None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': b'\x10',
            'DVI 1': b'\x01',
            'DVI 2': b'\x02',
            'DVI 3': b'\x03',
            'DVI 4': b'\x04',
            'SDI 1': b'\x20',
            'SDI 2': b'\x21'
        }

        if value in ValueStateValues:
            self.__SetHelper('Input', b''.join([b'\x33\x00\x12\x00\x00\x00', self._DeviceID, b'\xFF\x00\x00\x00\x00\x00\x00\x00\x00', ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetLoadPreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            self.__SetHelper('LoadPreset',
                             b''.join([b'\x74\x00\x11\x00\x00\x00', self._DeviceID, b'\xFF\x00\x00\x00\x00\x00\x00\x00', pack('b', int(value) - 1)]), value,
                             qualifier)
        else:
            self.Discard('Invalid Command for SetLoadPreset')

    def SetShow(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        if value in ValueStateValues:
            self.__SetHelper('Show', b''.join([b'\x11\x00\x11\x00\x00\x00', self._DeviceID, b'\xFF\x00\x00\x00\x00\x00\x00\x00', ValueStateValues[value]]),
                             value, qualifier)
        else:
            self.Discard('Invalid Command for SetShow')

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
        pass

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
                    except:
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
            raise KeyError('Invalid command for ReadStatus: ' + command)

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
