from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
            'Qt 300': self.cbad_25_172_Qt300,
            'Qt 600': self.cbad_25_172_Qt600,
            'Qt 100': self.cbad_25_172_Qt100,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoRamping': {'Parameters': ['Zone'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'InputAOutputLevel': {'Parameters': ['Type', 'Zone'], 'Status': {}},
            'InputBOutputLevel': {'Parameters': ['Type', 'Zone'], 'Status': {}},
            'MaskingLevel': {'Parameters': ['Type', 'Zone'], 'Status': {}},
            'Mute': {'Parameters': ['Zone'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{ZOGET,AUTO([0-5])=(-?\d{1,2})}\r'), self.__MatchAutoRamping, None)
            self.AddMatchString(re.compile(b'{CSGET,LOCK=([01])}\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'{ZOGET,(INAM|INAI)([0-5])=(\d{1,2})}\r'), self.__MatchInputAOutputLevel, None)
            self.AddMatchString(re.compile(b'{ZOGET,(INBM|INBI)([0-5])=(\d{1,2})}\r'), self.__MatchInputBOutputLevel, None)
            self.AddMatchString(re.compile(b'{ZOGET,M(MAX|MIN)([0-5])=(\d{1,2})}\r'), self.__MatchMaskingLevel, None)
            self.AddMatchString(re.compile(b'{ZOGET,MUTE([0-5])=([01])}\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'{NAK}\r'), self.__MatchError, None)

    def getZone(self, qualifier):
        zone = None
        if self.model == 'Qt100':
            zone = '0'
        else:
            try:
                zone = self.SetZone[qualifier['Zone']]
            except KeyError:
                self.Discard('Invalid Zone Parameter')
        return zone

    def SetAutoRamping(self, value, qualifier):

        zone = self.getZone(qualifier)
        if -20 <= value <= 0 and zone:
            AutoRampingCmdString = 'ZOSET,AUTO{0}={1}\r'.format(zone, value)
            self.__SetHelper('AutoRamping', AutoRampingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoRamping')

    def UpdateAutoRamping(self, value, qualifier):

        zone = self.getZone(qualifier)
        if zone:
            AutoRampingCmdString = 'ZOGET,AUTO{0}\r'.format(zone)
            self.__UpdateHelper('AutoRamping', AutoRampingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutoRamping')

    def __MatchAutoRamping(self, match, tag):

        if self.model == 'Qt100':
            zone = '1'
        else:
            zone = self.GetZone[match.group(1)]
        value = int(match.group(2))
        self.WriteStatus('AutoRamping', value, {'Zone': zone})

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'CSGET,LOCK\r'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInputAOutputLevel(self, value, qualifier):

        TypeStates = {
            'Max': 'INAM',
            'Min': 'INAI'
        }

        zone = self.getZone(qualifier)
        if 0 <= value <= 30 and qualifier['Type'] in TypeStates and zone:
            InputAOutputLevelCmdString = 'ZOSET,{0}{1}={2}\r'.format(TypeStates[qualifier['Type']], zone, value)
            self.__SetHelper('InputAOutputLevel', InputAOutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputAOutputLevel')

    def UpdateInputAOutputLevel(self, value, qualifier):

        TypeStates = {
            'Max': 'INAM',
            'Min': 'INAI'
        }

        zone = self.getZone(qualifier)
        if qualifier['Type'] in TypeStates and zone:
            InputAOutputLevelCmdString = 'ZOGET,{0}{1}\r'.format(TypeStates[qualifier['Type']], zone)
            self.__UpdateHelper('InputAOutputLevel', InputAOutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputAOutputLevel')

    def __MatchInputAOutputLevel(self, match, tag):

        TypeStates = {
            b'INAM': 'Max',
            b'INAI': 'Min'
        }

        if self.model == 'Qt100':
            zone = '1'
        else:
            zone = self.GetZone[match.group(2)]

        qualifier = {'Zone' : zone, 'Type': TypeStates[match.group(1)]}
        value = int(match.group(3))
        self.WriteStatus('InputAOutputLevel', value, qualifier)

    def SetInputBOutputLevel(self, value, qualifier):

        TypeStates = {
            'Max': 'INBM',
            'Min': 'INBI'
        }

        zone = self.getZone(qualifier)
        if 0 <= value <= 30 and qualifier['Type'] in TypeStates and zone:
            InputBOutputLevelCmdString = 'ZOSET,{0}{1}={2}\r'.format(TypeStates[qualifier['Type']], zone, value)
            self.__SetHelper('InputBOutputLevel', InputBOutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputBOutputLevel')

    def UpdateInputBOutputLevel(self, value, qualifier):

        TypeStates = {
            'Max': 'INBM',
            'Min': 'INBI'
        }

        zone = self.getZone(qualifier)
        if qualifier['Type'] in TypeStates and zone:
            InputBOutputLevelCmdString = 'ZOGET,{0}{1}\r'.format(TypeStates[qualifier['Type']], zone)
            self.__UpdateHelper('InputBOutputLevel', InputBOutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputBOutputLevel')

    def __MatchInputBOutputLevel(self, match, tag):

        TypeStates = {
            b'INBM': 'Max',
            b'INBI': 'Min'
        }

        if self.model == 'Qt100':
            zone = '1'
        else:
            zone = self.GetZone[match.group(2)]
        qualifier = {'Zone' : zone, 'Type': TypeStates[match.group(1)]}
        value = int(match.group(3).decode())
        self.WriteStatus('InputBOutputLevel', value, qualifier)

    def SetMaskingLevel(self, value, qualifier):

        zone = self.getZone(qualifier)
        if 0 <= value <= 30 and qualifier['Type'] in ['Max', 'Min'] and zone:
            MaskingLevelCmdString = 'ZOSET,M{0}{1}={2}\r'.format(qualifier['Type'].upper(), zone, int(value * 2))
            self.__SetHelper('MaskingLevel', MaskingLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMaskingLevel')

    def UpdateMaskingLevel(self, value, qualifier):

        zone = self.getZone(qualifier)
        if qualifier['Type'] in ['Max', 'Min'] and zone:
            MaskingLevelCmdString = 'ZOGET,M{0}{1}\r'.format(qualifier['Type'].upper(), zone)
            self.__UpdateHelper('MaskingLevel', MaskingLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMaskingLevel')

    def __MatchMaskingLevel(self, match, tag):

        if self.model == 'Qt100':
            zone = '1'
        else:
            zone = self.GetZone[match.group(2)]

        value = int(match.group(3).decode()) / 2
        qualifier = {'Zone' : zone, 'Type': match.group(1).decode().title()}
        self.WriteStatus('MaskingLevel', value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        zone = self.getZone(qualifier)
        if value in ValueStateValues and zone:
            MuteCmdString = 'ZOSET,MUTE{0}={1}\r'.format(zone, ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        zone = self.getZone(qualifier)
        if zone:
            MuteCmdString = 'ZOGET,MUTE{0}\r'.format(zone)
            self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        if self.model == 'Qt100':
            zone = '1'
        else:
            zone = self.GetZone[match.group(1)]
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Mute', value, {'Zone' : zone})

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

        self.Error(['Command Failed'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def cbad_25_172_Qt100(self):

        self.model = 'Qt100'

    def cbad_25_172_Qt300(self):

        self.model = 'Qt300'

        self.SetZone = {
            '1': '0',
            '2': '1',
            '3': '2'
        }

        self.GetZone = {
            b'0': '1',
            b'1': '2',
            b'2': '3'
        }

    def cbad_25_172_Qt600(self):

        self.model = 'Qt600'

        self.SetZone = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5'
        }

        self.GetZone = {
            b'0': '1',
            b'1': '2',
            b'2': '3',
            b'3': '4',
            b'4': '5',
            b'5': '6'
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
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

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