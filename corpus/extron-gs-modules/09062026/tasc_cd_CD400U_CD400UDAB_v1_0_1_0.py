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
        self.Models = {
            'CD-400U': self.tasc_5_3475_1,
            'CD-400UDAB': self.tasc_5_3475_2,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CurrentTrack': {'Status': {}},
            'CurrentTrackTime': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'PlaybackArea': {'Status': {}},
            'PlayMode': {'Status': {}},
            'Repeat': {'Status': {}},
            'ResumePlay': {'Status': {}},
            'TrackSearchPreset': {'Status': {}},
            'TrackSkip': {'Status': {}},
            'Transports': {'Status': {}},
        }

        if 'Serial' not in self.ConnectionType:
            self.Header = b'\x30'
            self.Footer = b'\x0D\x0A'
        else:
            self.Header = b'\x0A\x30'
            self.Footer = b'\x0D'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'0D7([0-9]{4})([0-9]{6})00\r'), self.__MatchCurrentTrack, None)
            self.AddMatchString(re.compile(b'0D0([018F][0-3F])\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'0CC(10|01)\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'0FF01([0-4][0-1])\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'0FF07CF(0[01F])\r'), self.__MatchPlaybackArea, None)
            self.AddMatchString(re.compile(b'0CE(0[016])\r'), self.__MatchPlayMode, None)
            self.AddMatchString(re.compile(b'0B7(0[01])\r'), self.__MatchRepeat, None)
            self.AddMatchString(re.compile(b'0B4(0[01])\r'), self.__MatchResumePlay, None)
            self.AddMatchString(re.compile(b'0F([02])\r'), self.__MatchError, None)

    def UpdateCurrentTrack(self, value, qualifier):
        CurrentTrackCmdString = self.Header + b'57' + self.Footer
        self.__UpdateHelper('CurrentTrack', CurrentTrackCmdString, value, qualifier)

    def __MatchCurrentTrack(self, match, tag):

        TrackNumValue = match.group(1).decode()
        TrackTimeValue = match.group(2).decode()
        TrueTrackNumValue = int('{0}{1}{2}{3}'.format(TrackNumValue[2], TrackNumValue[3], TrackNumValue[0], TrackNumValue[1]))
        TrueTrackTimeValue = float('{0}{1}{2}{3}.{4}{5}'.format(TrackTimeValue[3], TrackTimeValue[2], TrackTimeValue[0], TrackTimeValue[1], TrackTimeValue[4], TrackTimeValue[5]))
        if 1 <= TrueTrackNumValue <= 999:
            self.WriteStatus('CurrentTrack', TrueTrackNumValue, None)
        else:
            self.Discard('Invalid Command')

        if 0.01 <= TrueTrackTimeValue <= 9999.59:
            self.WriteStatus('CurrentTrackTime', TrueTrackTimeValue, None)
        else:
            self.Discard('Invalid Command')

    def UpdateCurrentTrackTime(self, value, qualifier):

        self.UpdateCurrentTrack(value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = self.Header + b'50' + self.Footer
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '00': 'No Media',
            '01': 'Preparing For Disc Ejection',
            '10': 'Stop',
            '11': 'Play',
            '12': 'Ready',
            '81': 'Recording',
            '82': 'Record Ready',
            '83': 'Information Writing',
            'FF': 'Other'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'10',
            'Off': b'01'
        }

        ExecutiveModeCmdString = self.Header + b'4C' + ValueStateValues[value] + self.Footer
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = self.Header + b'4CFF' + self.Footer
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '10': 'On',
            '01': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = self.Header + b'7F01' + self.InputStateValues[value] + self.Footer
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.Header + b'7F01FF' + self.Footer
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPlaybackArea(self, value, qualifier):

        ValueStateValues = {
            'All': b'00',
            'Folder (Not Skip Mode)': b'01',
            'Folder (Skip Mode)': b'0F'
        }

        PlaybackAreaCmdString = self.Header + b'7F074F' + ValueStateValues[value] + self.Footer
        self.__SetHelper('PlaybackArea', PlaybackAreaCmdString, value, qualifier)

    def UpdatePlaybackArea(self, value, qualifier):

        PlaybackAreaCmdString = self.Header + b'7F074FFF' + self.Footer
        self.__UpdateHelper('PlaybackArea', PlaybackAreaCmdString, value, qualifier)

    def __MatchPlaybackArea(self, match, tag):

        ValueStateValues = {
            '00': 'All',
            '01': 'Folder (Not Skip Mode)',
            '0F': 'Folder (Skip Mode)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PlaybackArea', value, None)

    def SetPlayMode(self, value, qualifier):

        ValueStateValues = {
            'Continuous': b'00',
            'Single': b'01',
            'Random': b'06'
        }

        PlayModeCmdString = self.Header + b'4D' + ValueStateValues[value] + self.Footer
        self.__SetHelper('PlayMode', PlayModeCmdString, value, qualifier)

    def UpdatePlayMode(self, value, qualifier):

        PlayModeCmdString = self.Header + b'4E' + self.Footer
        self.__UpdateHelper('PlayMode', PlayModeCmdString, value, qualifier)

    def __MatchPlayMode(self, match, tag):

        ValueStateValues = {
            '00': 'Continuous',
            '01': 'Single',
            '06': 'Random'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PlayMode', value, None)

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'On': b'01',
            'Off': b'00'
        }

        RepeatCmdString = self.Header + b'37' + ValueStateValues[value] + self.Footer
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def UpdateRepeat(self, value, qualifier):

        RepeatCmdString = self.Header + b'37FF' + self.Footer
        self.__UpdateHelper('Repeat', RepeatCmdString, value, qualifier)

    def __MatchRepeat(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Repeat', value, None)

    def SetResumePlay(self, value, qualifier):

        ValueStateValues = {
            'On': b'01',
            'Off': b'00'
        }

        ResumePlayCmdString = self.Header + b'34' + ValueStateValues[value] + self.Footer
        self.__SetHelper('ResumePlay', ResumePlayCmdString, value, qualifier)

    def UpdateResumePlay(self, value, qualifier):

        ResumePlayCmdString = self.Header + b'34FF' + self.Footer
        self.__UpdateHelper('ResumePlay', ResumePlayCmdString, value, qualifier)

    def __MatchResumePlay(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ResumePlay', value, None)

    def SetTrackSearchPreset(self, value, qualifier):

        if 1 <= value <= 999:
            track = str(value).zfill(3)
            TrackSearchPresetCmdString = self.Header + b'23' + track[1:3].encode() + b'0' + track[0].encode() + self.Footer
            self.__SetHelper('TrackSearchPreset', TrackSearchPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackSearchPreset')

    def SetTrackSkip(self, value, qualifier):

        ValueStateValues = {
            'Next': b'00',
            'Previous': b'01'
        }

        TrackSkipCmdString = self.Header + b'1A' + ValueStateValues[value] + self.Footer
        self.__SetHelper('TrackSkip', TrackSkipCmdString, value, qualifier)

    def SetTransports(self, value, qualifier):

        ValueStateValues = {
            'Play': b'12',
            'Stop': b'10',
            'Previous': b'1A01',
            'Next': b'1A00',
            'Open/Close': b'18',
            'Ready': b'0114'
        }

        TransportsCmdString = self.Header + ValueStateValues[value] + self.Footer
        self.__SetHelper('Transports', TransportsCmdString, value, qualifier)

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
        self.Error(['Illegal Command'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def tasc_5_3475_1(self):  # 400U
        self.InputStateValues = {
            'SD': b'\x30\x30',
            'USB': b'\x31\x30',
            'CD': b'\x31\x31',
            'Bluetooth': b'\x32\x30',
            'FM': b'\x33\x30',
            'AM': b'\x33\x31',
            'Aux': b'\x34\x30'
        }
        self.InputStateNames = {
            '00': 'SD',
            '10': 'USB',
            '11': 'CD',
            '20': 'Bluetooth',
            '30': 'FM',
            '31': 'AM',
            '40': 'Aux'
        }

    def tasc_5_3475_2(self):  # 400UDAB
        self.InputStateValues = {
            'SD': b'\x30\x30',
            'USB': b'\x31\x30',
            'CD': b'\x31\x31',
            'Bluetooth': b'\x32\x30',
            'FM': b'\x33\x31',
            'DAB': b'\x33\x30',
            'Aux': b'\x34\x30'
        }
        self.InputStateNames = {
            '00': 'SD',
            '10': 'USB',
            '11': 'CD',
            '20': 'Bluetooth',
            '31': 'FM',
            '30': 'DAB',
            '40': 'Aux'
        }

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
