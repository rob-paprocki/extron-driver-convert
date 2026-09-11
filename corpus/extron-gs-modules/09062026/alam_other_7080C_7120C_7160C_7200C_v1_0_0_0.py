from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.DeviceID = 'Broadcast'
        self.Commands = {
            'ReadTEXTFileRecall': {'Status': {}},
            'ReadTEXTFileString': {'Parameters': ['File Label'], 'Status': {}},
            'ReadTEXTFileUpdate': {'Status': {}},
            'WriteTEXTFileCommand': {'Parameters': ['File Label', 'Position', 'Effect', 'Color', 'Speed'], 'Status': {}},
            'WriteTEXTFileString': {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        tempID = value
        if tempID == 'Broadcast':
            self._DeviceID = '00'
        elif 0 <= int(tempID) <= 255:
            self._DeviceID = '{0:02X}'.format(int(tempID))
        else:
            print('Device ID is out of range.')

    def SetReadTEXTFileUpdate(self, value, qualifier):

        if value == 'Priority TEXT' or 1 <= int(value) <= 95:
            if value == 'Priority TEXT':
                fileLabel = '\x30'
            else:
                fileLabel = bytes([int(value) + 31]).decode()
            CmdString = '\x00\x00\x00\x00\x00\x01l{0}\x02B{1}\x04'.format(self._DeviceID, fileLabel)
            res = self.SendAndWait(CmdString, self.DefaultResponseTimeout, deliTag=b'\x03')
            if res:
                res = res.decode()
                try:
                    self.WriteStatus('ReadTEXTFileString', res[27:-1], {'File Label' : value})
                except(IndexError, ValueError):
                    print('ReadTEXTFileUpdate: Invalid/unexpected response for SetReadTEXTFileUpdate')
        else:
            print('Invalid Command for SetReadTEXTFileUpdate')

    def SetReadTEXTFileRecall(self, value, qualifier):

        if value == 'Priority TEXT' or 1 <= int(value) <= 95:
            if value == 'Priority TEXT':
                fileLabel = '\x30'
            else:
                fileLabel = bytes([int(value) + 31]).decode()
            textData = self.ReadStatus('ReadTEXTFileString', {'File Label' : value})
            if textData is not None:
                ReadTEXTFileRecallCmdString = '\x00\x00\x00\x00\x00\x01l{0}\x02A{1}{2}\x04'.format(self._DeviceID, fileLabel, textData)
                self.__SetHelper('ReadTEXTFileRecall', ReadTEXTFileRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetReadTEXTFileRecall')

    def SetWriteTEXTFileCommand(self, value, qualifier):

        position = {
            'Middle': '\x20',
            'Top': '\x22',
            'Bottom': '\x26',
            'Fill': '\x30',
            'None': ''
        }[qualifier['Position']]

        effect = {
            'Rotate': 'a',
            'Hold': 'b',
            'Flash': 'c',
            'Roll Up': 'e',
            'Roll Down': 'f',
            'Roll Left': 'g',
            'Roll Right': 'h',
            'Wipe Up': 'i',
            'Wipe Down': 'j',
            'Wipe Left': 'k',
            'Wipe Right': 'l',
            'Scroll': 'm',
            'Automode': 'o',
            'Twinkle': 'n0',
            'Sparkle': 'n1',
            'Snow': 'n2',
            'Interlock': 'n3',
            'Switch': 'n4',
            'Slide': 'n5',
            'Spray': 'n6',
            'Starburst': 'n7',
            'Roll In': 'p',
            'Roll Out': 'q',
            'Wipe In': 'r',
            'Wipe Out': 's',
            'None': ''
        }[qualifier['Effect']]

        color = {
            'Red': '\x1C1',
            'Green': '\x1C2',
            'Amber': '\x1C3',
            'Dim Red': '\x1C4',
            'Dim Green': '\x1C5',
            'Brown': '\x1C6',
            'Orange': '\x1C7',
            'Yellow': '\x1C8',
            'Color Mix': '\x1CB',
            'Autocolor': '\x1CC',
            'None': ''
        }[qualifier['Color']]

        speed = {
            'Slowest': '\x15',
            'Slow': '\x16',
            'Fast': '\x17',
            'Faster': '\x18',
            'Fastest': '\x19',
            'None': ''
        }[qualifier['Speed']]

        fileLabel = qualifier['File Label']

        if fileLabel == 'Priority TEXT' or 1 <= int(fileLabel) <= 95:

            if fileLabel == 'Priority TEXT':
                fileByte = '\x30'
            else:
                fileByte = bytes([int(fileLabel) + 31]).decode()

            if position and effect and color and speed:
                CmdString = '\x00\x00\x00\x00\x00\x01l{0}\x02A{1}\x1B{2}{3}{4}{5}{6}\x04'.format(self._DeviceID, fileByte, position, effect, color, speed, value)
            else:
                CmdString = '\x00\x00\x00\x00\x00\x01l{0}\x02A{1}{2}\x04'.format(self._DeviceID, fileByte, value)

            self.__SetHelper('WriteTEXTFileCommand', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetWriteTEXTFileCommand')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        pass

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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
