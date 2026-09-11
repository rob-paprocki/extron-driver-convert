from extronlib.interface import SerialInterface, EthernetClientInterface
import re


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
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'Track': {'Status': {}},
            'Transport': {'Status': {}},
        }        

        self.setHelperDeliRex = re.compile(b'(\x10\x01\x11|\x11\x12[\x00-\xFF][\x00-\xFF])')
        self.updateHelperDeliRex = re.compile(b'(\x11\x12[\x00-\xFF][\x00-\xFF]|\x79\x20[\x00-\xFF]{9}[\x00-\xFF])')

    def UpdateDeviceStatus(self, value, qualifier):

        res = self.__UpdateHelper('DeviceStatus', b'\x61\x20\x09\x8A', value, qualifier)
        if res:

            try:
                if res[3] & 1 == 1:
                    self.WriteStatus('Transport', 'Play', qualifier)
                elif res[3] & 32 == 32:
                    self.WriteStatus('Transport', 'Stop', qualifier)
                elif res[3] & 4 == 4:
                    self.WriteStatus('Transport', 'Fast Forward', qualifier)
                elif res[3] & 8 == 8:
                    self.WriteStatus('Transport', 'Rewind', qualifier)
                elif res[3] & 2 == 2:
                    self.WriteStatus('Transport', 'Record', qualifier)
                elif res[4] & 2 == 2:
                    self.WriteStatus('Transport', 'Pause', qualifier)
            except (IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

            try:
                if res[2] & 128 == 128:
                    self.WriteStatus('DeviceStatus', 'Busy', qualifier)
                elif res[2] & 32 == 32:
                    self.WriteStatus('DeviceStatus', 'Disk Out', qualifier)
                elif res[2] & 4 == 4:
                    self.WriteStatus('DeviceStatus', 'Hardware Error', qualifier)
                elif res[10] & 16 == 16:
                    self.WriteStatus('DeviceStatus', 'Disk Full', qualifier)
                elif res[2] == 0:
                    self.WriteStatus('DeviceStatus', 'Normal', qualifier)
            except (IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

    def SetInput(self, value, qualifier):

        States = {
            'Component': b'\x41\x53\x00\x94',
            'S-Video': b'\x41\x53\x01\x95',
            'CVBS': b'\x41\x53\x02\x96',
            'DV': b'\x41\x53\x03\x97',
        }

        self.__SetHelper('Input', States[value], value, qualifier)

    def SetTrack(self, value, qualifier):

        ValueStateValues = {
            'Next': b'\x40\x50\x90',
            'Previous': b'\x40\x51\x91'
        }
        if value in ['Next', 'Previous']:
            CmdString = ValueStateValues[value]
        elif 1 <= int(value) <= 99:
            Track = int(value)
            CmdString = bytes([0x41, 0x52, Track, 0x41 + 0x52 + Track])
        else:
            print('Invalid Command for SetTrack')

        if CmdString:
            self.__SetHelper('Track', CmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        States = {
            'Play': b'\x20\x01\x21',
            'Stop': b'\x20\x00\x20',
            'Pause': b'\x21\x13\x00\x34',
            'Record': b'\x20\x02\x22',
            'Fast Forward': b'\x20\x10\x30',
            'Rewind': b'\x20\x20\x40',
            'Shuttle Forward': b'\x21\x13\x01\x35',
            'Shuttle Rewind': b'\x21\x23\x01\x45'
        }

        self.__SetHelper('Transport', States[value], value, qualifier)        

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0:2] == b'\x11\x12':
            if response[2] & 1 == 1:
                print('Error from device: Undefined Command')
            if response[2] & 2 == 2:
                self.Error(['Error from device: Software Overrun'])
            if response[2] & 4 == 4:
                self.Error(['Error from device: Checksum Error'])
            if response[2] & 16 == 16:
                self.Error(['Error from device: Parity Error'])
            if response[2] & 32 == 32:
                self.Error(['Error from device: Overrun Error'])
            if response[2] & 64 == 64:
                self.Error(['Error from device: Framing Error'])
            if response[2] & 128 == 128:
                self.Error(['Error from device: Timeout'])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.setHelperDeliRex)
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.updateHelperDeliRex)
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
