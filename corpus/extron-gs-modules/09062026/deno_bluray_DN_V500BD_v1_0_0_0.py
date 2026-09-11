from extronlib.interface import EthernetClientInterface, SerialInterface
from functools import reduce
from operator import add


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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioChannel': {'Status': {}},
            'AudioFormat': {'Status': {}},
            'DirectSelect': {'Parameters': ['Search Mode'], 'Status': {}},
            'DiscType': {'Status': {}},
            'Function': {'Status': {}},
            'General': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PlayMode': {'Status': {}},
            'Power': {'Status': {}},
            'RequiredCommand': {'Status': {}},
            'ElapsedTime': {'Status': {}},
            'Transport': {'Status': {}},
            'UserDefinedString': {'Status': {}}
        }

        self.DiscTypeStates = {
            '1': 'DVD Video',
            '2': 'DVD Audio',
            '3': 'VCD',
            '4': 'CD-DA',
            '5': 'CD-ROM',
            '6': 'Unknown',
            '7': 'SACD',
            '8': 'DVD VR',
            '9': 'BDMV',
            ':': 'BDAV'
        }

        self.AudioFormatStates = {
            '1': 'Dolby Digital',
            '2': 'DTS',
            '3': 'MPEG',
            '4': 'LPCM',
            '5': 'PPCM',
            '6': 'Unknown',
            '7': 'DSD',
            '8': 'DD+',
            '9': 'DTS-HD',
            ':': 'Dolby TrueHD',
            ';': 'MP3',
            '<': 'AAC',
            '=': 'WMA'
        }

        self.AudioChannelStates = {
            '1': '1 ch',
            '2': '2 ch',
            '3': '2.1 ch',
            '4': '3 ch',
            '5': '3.1 ch',
            '6': '4 ch',
            '7': '4.1 ch',
            '8': '5 ch',
            '9': '5.1 ch',
            ':': '6 ch',
            ';': 'L/R (CD/VCD/MP3)',
            '<': 'R (CD/CD)',
            '=': 'L (CD/VCD)',
            '>': 'Unknown',
            '?': '6.1 ch',
            '@': '7 ch',
            'A': '7.1 ch',
            'B': '8 ch'
        }

        self.GeneralStates = {
            '0': 'Standby',
            '1': 'Disc Loading',
            '2': 'Disc Loading Complete',
            '3': 'Tray Opening',
            '4': 'Tray Closing',
            'A': 'No Disc',
            'B': 'Stopped',
            'C': 'Playing',
            'D': 'Paused',
            'E': 'Scan Play',
            'F': 'Slow Search Play',
            'G': 'Setup Mode',
            'H': 'Play Back Control',
            'I': 'DVD Resume Stop',
            'J': 'DVD Menu',
        }

        self.PlayModeStates = {
            '1': 'Normal',
            '2': 'Program',
            '3': 'Random',
        }

        self.AnswerCodes = {
            '0': 'Invalid Command.',
            '1': 'Inappropriate Command Format.',
            '2': 'The Specified Track, Group, Title or Chapter Does Not Exist.',
            '3': 'The Specified Time Does Not Exist.'
        }

    def EncodeBCC(self, Frame):

        BCC = '{:02X}'.format(reduce(add, Frame[1:]) & 255)
        return b''.join([Frame, BCC.encode()])

    def DecodeBCC(self, Frame):

        BCC = int(Frame[-2:], 16)
        Frame = Frame[:-2]
        if BCC == reduce(add, Frame[1:]) & 255:
            return Frame
        else:
            raise ValueError

    def SetDirectSelect(self, value, qualifier):

        SearchModeStates = {
            'Group or Title Number': '1',
            'Track or Chapter Number': '2',
        }
        ValueConstraints = {
            'Min': 1,
            'Max': 999
        }
        SearchMode = qualifier['Search Mode']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and SearchMode in SearchModeStates:
            DirectSelectCmdString = self.EncodeBCC('\x02L{}{:04}\x03'.format(SearchModeStates[SearchMode], value).encode())
            self.__SetHelper('DirectSelect', DirectSelectCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDirectSelect')

    def SetFunction(self, value, qualifier):

        ValueStateValues = {
            'Setup': b'\x02E\x00\x00\x00\x00\x00\x03',
            'Track Clear': b'\x02f\x00\x00\x00\x00\x00\x03',
            'Track Call': b'\x02g\x00\x00\x00\x00\x00\x03',
            'Program/Direct': b'\x02e\x00\x00\x00\x00\x00\x03',
            'Display': b'\x02h\x00\x00\x00\x00\x00\x03',
            'Marker': b'\x02l\x00\x00\x00\x00\x00\x03',
            'Zoom': b'\x02m\x00\x00\x00\x00\x00\x03',
            'Dimmer': b'\x02n\x00\x00\x00\x00\x00\x03',
            'Red': b'\x02r1\x00\x00\x00\x00\x03',
            'Green': b'\x02r2\x00\x00\x00\x00\x03',
            'Blue': b'\x02r3\x00\x00\x00\x00\x03',
            'Yellow': b'\x02r4\x00\x00\x00\x00\x03',
            'Picture in Picture': b'\x02s\x00\x00\x00\x00\x00\x03',
        }
        FunctionCmdString = self.EncodeBCC(ValueStateValues[value])
        self.__SetHelper('Function', FunctionCmdString, value, qualifier)

    def UpdateGeneral(self, value, qualifier):

        RequiredCommandCmdString = self.EncodeBCC(b'\x020\x00\x00\x00\x00\x00\x03')
        res = self.__UpdateHelper('RequiredCommand', RequiredCommandCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('DiscType', self.DiscTypeStates[res[3]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateRequiredCommand')
            try:
                self.WriteStatus('AudioFormat', self.AudioFormatStates[res[4]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateRequiredCommand')
            try:
                self.WriteStatus('AudioChannel', self.AudioChannelStates[res[5]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateRequiredCommand')
            try:
                self.WriteStatus('General', self.GeneralStates[res[9]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateRequiredCommand')
            try:
                self.WriteStatus('PlayMode', self.PlayModeStates[res[10]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateRequiredCommand')
            try:
                self.WriteStatus('DirectSelect', int(res[11:14]), {'Search Mode': 'Group or Title Number'})
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateRequiredCommand')
            try:
                self.WriteStatus('DirectSelect', int(res[14:18]), {'Search Mode': 'Track or Chapter Number'})
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateRequiredCommand')
            try:
                self.WriteStatus('ElapsedTime', '{}:{}:{}'.format(res[19:21], res[21:23], res[23:25]), qualifier)
            except IndexError:
                print('Invalid/unexpected response for UpdateRequiredCommand')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Top Menu': b'\x02F\x00\x00\x00\x00\x00\x03',
            'Playback Menu': b'\x02G\x00\x00\x00\x00\x00\x03',
            'Return': b'\x02H\x00\x00\x00\x00\x00\x03',
            'Left': b'\x02M1\x00\x00\x00\x00\x03',
            'Up': b'\x02M2\x00\x00\x00\x00\x03',
            'Right': b'\x02M3\x00\x00\x00\x00\x03',
            'Down': b'\x02M4\x00\x00\x00\x00\x03',
            'Enter': b'\x02N\x00\x00\x00\x00\x00\x03',
        }
        MenuNavigationCmdString = self.EncodeBCC(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02 \x00\x00\x00\x00\x00\x03',
            'Off': b'\x02!\x00\x00\x00\x00\x00\x03',
        }
        PowerCmdString = self.EncodeBCC(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': b'\x02@\x00\x00\x00\x00\x00\x03',
            'Stop': b'\x02A\x00\x00\x00\x00\x00\x03',
            'Pause': b'\x02B\x00\x00\x00\x00\x00\x03',
            'Next': b'\x02C+\x00\x00\x00\x00\x03',
            'Previous': b'\x02C-\x00\x00\x00\x00\x03',
            'Fast Forward': b'\x02D+\x00\x00\x00\x00\x03',
            'Rewind': b'\x02D-\x00\x00\x00\x00\x03',
            'Open/Close': b'\x02a\x00\x00\x00\x00\x00\x03',
            'Repeat': b'\x02i1\x00\x00\x00\x00\x03',
            'Repeat A-B': b'\x02i2\x00\x00\x00\x00\x03',
            'Random': b'\x02k\x00\x00\x00\x00\x00\x03',
        }
        TransportCmdString = self.EncodeBCC(ValueStateValues[value])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            response = self.DecodeBCC(response).decode('iso 8859-1')
            if response[2] in self.AnswerCodes:
                print(self.AnswerCodes[response[2]])
                response = ''
        except (ValueError, AttributeError, IndexError):
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
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

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=28)
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
