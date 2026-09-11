from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from functools import reduce
from operator import add


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelMode': {'Parameters': ['Channel', 'Area', 'Movement'], 'Status': {}},
            'Dim': {'Parameters': ['Channel', 'Amplitude'], 'Status': {}},
            'DimFrames': {'Parameters': ['Channel'], 'Status': {}},
            'Position': {'Parameters': ['Channel'], 'Status': {}},
            'Tilt': {'Parameters': ['Channel', 'Amplitude'], 'Status': {}},
            'TiltFramesCE': {'Parameters': ['Channel'], 'Status': {}},
            'TiltFramesUS': {'Parameters': ['Channel'], 'Status': {}},
        }

        self.ACKbit = 128
        self._SourceID = None
        self._DestinationID = None

    def create_match_strings(self):
        if self.Unidirectional == 'False':
            if self._SourceID is not None and self._DestinationID is not None:
                MatchChannelMode = b''.join([self.Raw2Actual_NoCheckSum([0xB0, 15, 5] + self._DestinationID + self._SourceID), b'([\xF0-\xFF])(\xFF|\xFE)(\xFF|\xFE)(\xFF|\xFE)[\x5Cs\x5CS]{2}'])
                MatchDimFrames = b''.join([self.Raw2Actual_NoCheckSum([0xB2, 13, 5] + self._DestinationID + self._SourceID), b'([\xF0-\xFF])([\x00-\xFB])[\x5Cs\x5CS]{2}'])
                MatchTiltFrames = b''.join([self.Raw2Actual_NoCheckSum([0xB1, 14, 5] + self._DestinationID + self._SourceID), b'([\xF0-\xFF])([\x00-\xFB])([\xF2-\xFD])[\x5Cs\x5CS]{2}'])
                MatchError = b''.join([self.Raw2Actual_NoCheckSum([0x6F, 12, 5] + self._DestinationID + self._SourceID), b'(\xFE|\xEF|\xEE|\x00)[\x5Cs\x5CS]{2}'])

                self.AddMatchString(re.compile(MatchChannelMode), self.__MatchChannelMode, None)
                self.AddMatchString(re.compile(MatchDimFrames), self.__MatchDimFrames, None)
                self.AddMatchString(re.compile(MatchTiltFrames), self.__MatchTiltFramesCEandUS, None)
                self.AddMatchString(re.compile(MatchError), self.__MatchError, None)

    def ID_error(self, parameter):
        ProgramLog('{0} module error: Invalid format for {1} parameter, see Communication Sheet for more information'.format(__name__, parameter), 'error')

    @property
    def SourceID(self):
        return self._SourceID

    @SourceID.setter
    def SourceID(self, value):
        try:
            SourceID = value
            SourceID = SourceID.split(':')
            SourceID = [int(a, 16) for a in reversed(SourceID)]
            self._SourceID = [a for a in SourceID if a < 256]
            if len(self._SourceID) != 3:
                self.ID_error('Source ID')
        except (ValueError, AttributeError):
            self.ID_error('Source ID')
        else:
            self.create_match_strings()

    @property
    def DestinationID(self):
        return self._DestinationID

    @DestinationID.setter
    def DestinationID(self, value):
        try:
            DestinationID = value
            DestinationID = DestinationID.split(':')
            DestinationID = [int(a, 16) for a in reversed(DestinationID)]
            self._DestinationID = [a for a in DestinationID if a < 256]
            if len(self._DestinationID) != 3:
                self.ID_error('Destination ID')
        except (ValueError, AttributeError):
            self.ID_error('Destination ID')
        else:
            self.create_match_strings()

    def Raw2Actual(self, Frame):
        Not = [~a & 255 for a in Frame]
        CheckSum = reduce(add, Not)
        Not.extend([CheckSum >> 8, CheckSum & 255])
        return bytes(Not)

    def Actual2Raw(self, Frame):
        FrameList = list(Frame)
        CheckSum = FrameList.pop() + FrameList.pop() * 256
        if CheckSum == reduce(add, FrameList):
            return [~a & 255 for a in FrameList]
        else:
            return False

    def Raw2Actual_NoCheckSum(self, Frame):
        Not = [~a & 255 for a in Frame]
        return bytes(Not)

    def SetChannelMode(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        AreaStates = {
            'Central European': 0,
            'United States': 1
        }
        MovementStates = {
            'Roll': 0,
            'Tilt': 1
        }
        ValueStateValues = {
            'Normal': 0,
            'Modulis': 1
        }
        Channel = int(qualifier['Channel'])
        Area = qualifier['Area']
        Movement = qualifier['Movement']
        if (ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max'] and
                Area in AreaStates and Movement in MovementStates):
            ChannelModeCmdString = [0x90, 15 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1, AreaStates[Area], MovementStates[Movement], ValueStateValues[value]]
            ChannelModeCmdString = self.Raw2Actual(ChannelModeCmdString)
            self.__SetHelper('ChannelMode', ChannelModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelMode')

    def UpdateChannelMode(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        AreaStates = {
            'Central European': 0,
            'United States': 1
        }
        MovementStates = {
            'Roll': 0,
            'Tilt': 1
        }
        Channel = int(qualifier['Channel'])
        Area = qualifier['Area']
        Movement = qualifier['Movement']
        if (ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max'] and
                Area in AreaStates and Movement in MovementStates):
            ChannelModeCmdString = self.Raw2Actual([0xA0, 12 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1])
            self.__UpdateHelper('ChannelMode', ChannelModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelMode')

    def __MatchChannelMode(self, match, tag):

        Raw = self.Actual2Raw(match.group(0))
        if Raw:
            AreaStates = {
                0: 'Central European',
                1: 'United States'
            }
            MovementStates = {
                0: 'Roll',
                1: 'Tilt'
            }
            ValueStateValues = {
                0: 'Normal',
                1: 'Modulis'
            }
            qualifier = {'Channel': str(Raw[9] + 1),
                         'Area': AreaStates[Raw[10]],
                         'Movement': MovementStates[Raw[11]]}
            self.WriteStatus('ChannelMode', ValueStateValues[Raw[12]], qualifier)

    def SetDim(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        AmplitudeConstraints = {
            'Min': 1,
            'Max': 127
        }
        ValueStateValues = {
            'Increase': 0,
            'Decrease': 1
        }
        Channel = int(qualifier['Channel'])
        Amplitude = qualifier['Amplitude']
        if (ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max'] and
                AmplitudeConstraints['Min'] <= Amplitude <= AmplitudeConstraints['Max']):
            DimCmdString = self.Raw2Actual([0x82, 14 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1, ValueStateValues[value], Amplitude])
            self.__SetHelper('Dim', DimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDim')

    def SetDimFrames(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        FramesConstraints = {
            'Min': 4,
            'Max': 255
        }
        Channel = int(qualifier['Channel'])
        if (ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max'] and
                FramesConstraints['Min'] <= value <= FramesConstraints['Max']):
            DimFramesCmdString = self.Raw2Actual([0x92, 13 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1, value])
            self.__SetHelper('DimFrames', DimFramesCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimFrames')

    def UpdateDimFrames(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        Channel = int(qualifier['Channel'])
        if ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max']:
            DimFramesCmdString = self.Raw2Actual([0xA2, 12 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1])
            self.__UpdateHelper('DimFrames', DimFramesCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDimFrames')

    def __MatchDimFrames(self, match, tag):

        Raw = self.Actual2Raw(match.group(0))
        if Raw:
            qualifier = {'Channel': str(Raw[9] + 1)}
            self.WriteStatus('DimFrames', Raw[10], qualifier)

    def SetPosition(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        ValueStateValues = {
            'Upper Limit / Light On': 1,
            'Lower Limit / Light Off': 2,
            'Stop': 3,
            'Intermediate / Light On with Favorite Light Position': 4
        }
        Channel = int(qualifier['Channel'])
        if ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max']:
            PositionCmdString = self.Raw2Actual([0x80, 13 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1, ValueStateValues[value]])
            self.__SetHelper('Position', PositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPosition')

    def SetTilt(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        AmplitudeConstraints = {
            'Min': 1,
            'Max': 127
        }
        ValueStateValues = {
            'Up': 0,
            'Down': 1
        }
        Channel = int(qualifier['Channel'])
        Amplitude = qualifier['Amplitude']
        if (ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max'] and
                AmplitudeConstraints['Min'] <= Amplitude <= AmplitudeConstraints['Max']):
            TiltCmdString = self.Raw2Actual([0x81, 14 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1, ValueStateValues[value], Amplitude])
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetTiltFramesCE(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        ValueConstraints = {
            'Min': 2,
            'Max': 13
        }
        TiltUS = value
        if not TiltUS: TiltUS = 5

        Channel = int(qualifier['Channel'])
        if (ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max'] and
                ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            TiltFramesCECmdString = self.Raw2Actual([0x91, 14 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1, TiltUS, value])
            self.__SetHelper('TiltFramesCE', TiltFramesCECmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTiltFramesCE')

    def UpdateTiltFramesCE(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        Channel = int(qualifier['Channel'])
        if ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max']:
            TiltFramesCECmdString = self.Raw2Actual([0xA1, 12 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1])
            self.__UpdateHelper('TiltFramesCE', TiltFramesCECmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTiltFramesCE')

    def SetTiltFramesUS(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        ValueConstraints = {
            'Min': 4,
            'Max': 255
        }
        TiltCE = value
        if not TiltCE: TiltCE = 2

        Channel = int(qualifier['Channel'])
        if (ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max'] and
                ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            TiltFramesUSCmdString = self.Raw2Actual([0x91, 14 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1, value, TiltCE])
            self.__SetHelper('TiltFramesUS', TiltFramesUSCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTiltFramesUS')

    def UpdateTiltFramesUS(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 16
        }
        Channel = int(qualifier['Channel'])
        if ChannelConstraints['Min'] <= Channel <= ChannelConstraints['Max']:
            TiltFramesUSCmdString = self.Raw2Actual([0xA1, 12 | self.ACKbit, 5] + self._SourceID + self._DestinationID + [Channel - 1])
            self.__UpdateHelper('TiltFramesUS', TiltFramesUSCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTiltFramesUS')

    def __MatchTiltFramesCEandUS(self, match, tag):

        Raw = self.Actual2Raw(match.group(0))
        if Raw:  # is checksum valid?
            qualifier = {'Channel': str(Raw[9] + 1)}
            self.WriteStatus('TiltFramesCE', Raw[11], qualifier)
            self.WriteStatus('TiltFramesUS', Raw[10], qualifier)

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

        Raw = self.Actual2Raw(match.group(0))
        if Raw:
            Errors = {
                1: 'Data out of range.',
                0x10: 'Unknown message.',
                0x11: 'Message length error.',
                0xFF: 'Busy - Cannot process message.'
            }
            self.Error([Errors[Raw[9]]])

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=4800, Data=8, Parity='Odd', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
