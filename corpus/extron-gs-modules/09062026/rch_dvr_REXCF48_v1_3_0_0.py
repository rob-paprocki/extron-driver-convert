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
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'LiveBroadcasting': {'Parameters': ['Channel'], 'Status': {}},
            'Recording': {'Parameters': ['Channel'], 'Status': {}},
            'RestartServer': {'Status': {}},
            'RoomConnection': {'Parameters': ['Channel'], 'Status': {}},
            'SystemVersion': {'Status': {}},
        }

    def SetLiveBroadcasting(self, value, qualifier):

        ValueStateValues = {
            'Start': b'\x00\x07\x8E\x03\x01\x01',
            'Stop': b'\x00\x07\x8E\x03\x01\x00'
        }

        Channel = int(qualifier['Channel'])
        if 0 <= Channel <= 40:
            LiveBroadcastingCmdString = ValueStateValues[value] + bytes([Channel, 0x0D])
            self.__SetHelper('LiveBroadcasting', LiveBroadcastingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLiveBroadcasting')

    def UpdateLiveBroadcasting(self, value, qualifier):

        ValueStateValues = {
            85: 'Start',
            78: 'Stop'
        }

        Channel = int(qualifier['Channel'])
        if 0 <= Channel <= 40:
            LiveBroadcastingCmdString = b'\x00\x06\x8E\x01\x04' + bytes([Channel, 0x0D])
            res = self.__UpdateHelper('LiveBroadcasting', LiveBroadcastingCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[6]]
                    self.WriteStatus('LiveBroadcasting', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Live Broadcasting: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLiveBroadcasting')

    def SetRecording(self, value, qualifier):

        ValueStateValues = {
            'Record': b'\x00\x09\x8E\x03\x02\x01\x00',
            'Stop': b'\x00\x08\x8E\x03\x02\x00\x00',
            'Pause': b'\x00\x08\x8E\x03\x02\x02\x00',
            'Resume': b'\x00\x08\x8E\x03\x02\x01\x00'
        }

        Channel = int(qualifier['Channel'])
        if 0 <= Channel <= 40:
            if value == 'Record':
                RecordingCmdString = ValueStateValues[value] + bytes([Channel, 0x7F, 0x0D])
            else:
                RecordingCmdString = ValueStateValues[value] + bytes([Channel, 0x0D])
            self.__SetHelper('Recording', RecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecording')

    def UpdateRecording(self, value, qualifier):

        ValueStateValues = {
            82: 'Record',
            78: 'Stop',
            80: 'Pause'
        }

        Channel = int(qualifier['Channel'])
        if 0 <= Channel <= 40:
            RecordingCmdString = b'\x00\x06\x8E\x01\x06' + bytes([Channel, 0x0D])
            res = self.__UpdateHelper('Recording', RecordingCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[6]]
                    self.WriteStatus('Recording', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Recording: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRecording')

    def SetRestartServer(self, value, qualifier):

        RestartServerCmdString = b'\x00\x05\x8E\x03\x08\x0D'
        self.__SetHelper('RestartServer', RestartServerCmdString, value, qualifier)

    def SetRoomConnection(self, value, qualifier):

        ValueStateValues = {
            'Connect': b'\x00\x07\x8E\x03\x01\x01',
            'Disconnect': b'\x00\x07\x8E\x03\x01\x00'
        }

        Channel = int(qualifier['Channel'])
        if 0 <= Channel <= 40:
            RoomConnectionCmdString = ValueStateValues[value] + bytes([Channel, 0x0D])
            self.__SetHelper('RoomConnection', RoomConnectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomConnection')

    def UpdateRoomConnection(self, value, qualifier):

        ValueStateValues = {
            49: 'Connect',
            48: 'Disconnect'
        }

        Channel = int(qualifier['Channel'])
        if 0 <= Channel <= 40:
            RoomConnectionCmdString = b'\x00\x06\x8E\x02\x05' + bytes([Channel, 0x0D])
            res = self.__UpdateHelper('RoomConnection', RoomConnectionCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[6]]
                    self.WriteStatus('RoomConnection', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Room Connection: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRoomConnection')

    def UpdateSystemVersion(self, value, qualifier):

        SystemVersionCmdString = b'\x00\x05\x8E\x02\x01\r'
        res = self.__UpdateHelper('SystemVersion', SystemVersionCmdString, value, qualifier)
        if res:
            try:
                value = res[5:-2].decode('iso-8859-1')
                self.WriteStatus('SystemVersion', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['System Version: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if b'error' in response:
            self.counter = 0
            self.Error(['{} has error'.format(sourceCmdName)])
            response = ''
        elif b'\x7E\x7E\x7E' in response:
            self.counter = 0
            self.Error(['{} has invalid data packet return'.format(sourceCmdName)])
            response = ''
        elif b'\x8E\x8E\x8E' in response:
            self.counter = 0
            self.Error(['{} exceeds maximum connections'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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
