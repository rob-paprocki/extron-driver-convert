from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import pack

class DeviceEthernetClass:
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*SNAMUT0{15}([01])\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*SNINPT0{7}([013])0{7}([01-4])\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*SNPOWR0{15}([01])\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*SNPMUT0{15}([01])\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*SNVOLU0{13}(\d{3})\n'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(b'\*SA(AMUT|IRCC|INPT|POWR|PMUT|VOLU)[FN]{16}\n'), self.__MatchError, None)

        self.update_delirex = {
            'AudioMute': re.compile('\*SAAMUT0{15}([01])\n'),
            'Input': re.compile('\*SAINPT0{7}([013])0{7}([01-4])\n'),
            'Power': re.compile('\*SAPOWR0{15}([01])\n'),
            'VideoMute': re.compile('\*SAPMUT0{15}([01])\n'),
            'Volume': re.compile('\*SAVOLU0{13}(\d{3})\n')
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '*SCAMUT0000000000000001\n',
            'Off': '*SCAMUT0000000000000000\n'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = '*SEAMUT################\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                match = self.update_delirex['AudioMute'].search(res)
                value = ValueStateValues[match.group(1)]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': '*SCIRCC0000000000000033\n',
            'Down': '*SCIRCC0000000000000034\n'
        }

        if value in ValueStateValues:
            ChannelCmdString = ValueStateValues[value]
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': '*SCINPT0000000000000000\n',
            'Video': '*SCINPT0000000300000001\n',
            'HDMI 1': '*SCINPT0000000100000001\n',
            'HDMI 2': '*SCINPT0000000100000002\n',
            'HDMI 3': '*SCINPT0000000100000003\n',
            'HDMI 4': '*SCINPT0000000100000004\n',
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            ('0', '0'): 'TV',
            ('3', '1'): 'Video',
            ('1', '1'): 'HDMI 1',
            ('1', '2'): 'HDMI 2',
            ('1', '3'): 'HDMI 3',
            ('1', '4'): 'HDMI 4'
        }
        InputCmdString = '*SEINPT################\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                match = self.update_delirex['Input'].search(res)
                value = ValueStateValues[(match.group(1), match.group(2))]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'TV',
            '3': 'Video'
        }

        if match.group(1).decode() == '1':
            value = 'HDMI {}'.format(match.group(2).decode())
        else:
            value = ValueStateValues[match.group(1).decode()]

        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '*SCIRCC0000000000000018\n',
            '2': '*SCIRCC0000000000000019\n',
            '3': '*SCIRCC0000000000000020\n',
            '4': '*SCIRCC0000000000000021\n',
            '5': '*SCIRCC0000000000000022\n',
            '6': '*SCIRCC0000000000000023\n',
            '7': '*SCIRCC0000000000000024\n',
            '8': '*SCIRCC0000000000000025\n',
            '9': '*SCIRCC0000000000000026\n',
            '0': '*SCIRCC0000000000000027\n',
            'Dot': '*SCIRCC0000000000000038\n'
        }

        if value in ValueStateValues:
            KeypadCmdString = ValueStateValues[value]
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '*SCIRCC0000000000000009\n',
            'Down': '*SCIRCC0000000000000010\n',
            'Left': '*SCIRCC0000000000000012\n',
            'Right': '*SCIRCC0000000000000011\n',
            'Home': '*SCIRCC0000000000000006\n',
            'Return': '*SCIRCC0000000000000008\n',
            'Select': '*SCIRCC0000000000000013\n',
            'Options': '*SCIRCC0000000000000007\n'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '*SCPOWR0000000000000001\n',
            'Off': '*SCPOWR0000000000000000\n'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '*SEPOWR################\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                match = self.update_delirex['Power'].search(res)
                value = ValueStateValues[match.group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '*SCPMUT0000000000000001\n',
            'Off': '*SCPMUT0000000000000000\n'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = '*SEPMUT################\n'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                match = self.update_delirex['VideoMute'].search(res)
                value = ValueStateValues[match.group(1)]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '*SCVOLU0000000000000{0:03d}\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '*SEVOLU################\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                match = self.update_delirex['Volume'].search(res)
                value = int(match.group(1))
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[7] in ['F', 'N']:
            self.Error(['An error occurred: {0}.'.format(sourceCmdName)])
            return ''
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def __MatchError(self, match, tag):

        self.counter = 0

        commands = {
            'AMUT': 'Audio Mute',
            'IRCC': 'Channel/Keypad/Menu Navigation',
            'INPT': 'Input',
            'POWR': 'Power',
            'PMUT': 'Video Mute',
            'VOLU': 'Volume'
        }

        self.Error(['An error occurred: {}.'.format(commands[match.group(1).decode()])])

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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

class DeviceSerialClass:
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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'ChannelDiscreteCommand': {'Parameters': ['Tuner'], 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'ClosedCaptionAnalog': { 'Status': {}},
            'ClosedCaptionDigital': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.update_delirex = {
            'AudioMute':    re.compile(b'(?:\x70[\x00-\x04]\x03\x01[\x00\x01][\x00-\xFF]|\x70[\x03\x04][\x00-\xFF])'),
            'Input':        re.compile(b'(?:\x70[\x00-\x04][\x02\x03][\x01\x02\x04][\x00-\xFF]{1,2}|\x70[\x03\x04][\x00-\xFF])'),
            'Power':        re.compile(b'(?:\x70[\x00-\x04]\x02[\x00\x01][\x00-\xFF]|\x70[\x03\x04][\x00-\xFF])'),
            'Volume':       re.compile(b'(?:\x70[\x00-\x04]\x03\x01[\x00-\x64][\x00-\xFF]|\x70[\x03\x04][\x00-\xFF])')
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom':    b'\x8C\x00\x44\x03\x01\x00\xD4',
            'Full':         b'\x8C\x00\x44\x03\x01\x01\xD5',
            'Zoom':         b'\x8C\x00\x44\x03\x01\x02\xD6',
            'Normal':       b'\x8C\x00\x44\x03\x01\x03\xD7'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = ValueStateValues[value]
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x8C\x00\x06\x03\x01\x01\x97',
            'Off':  b'\x8C\x00\x06\x03\x01\x00\x96'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        AudioMuteCmdString = b'\x83\x00\x06\xFF\xFF\x87'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up':   b'\x8C\x00\x04\x03\x00\x00\x93',
            'Down': b'\x8C\x00\x04\x03\x00\x01\x94'
        }

        if value in ValueStateValues:
            ChannelCmdString = ValueStateValues[value]
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def SetChannelDiscreteCommand(self, value, qualifier):

        TunerStates = {
            'Terr Digital':     b'\x01',
            'Terr Analog':      b'\x02',
            'CATV':             b'\x03',
            'BS Digital':       b'\x04',
            'CS Digital':       b'\x05',
            'DVB-S':            b'\x06',
            'DVB-S2':           b'\x07',
            'Cable Analog':     b'\x0A',
            'Cable Digital':    b'\x0B'
        }

        if 0 <= len(value) <= 10 and all([i in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ','] for i in value]):
            channel = value
            if qualifier['Tuner'] in TunerStates and channel:
                data = b'\x8C\x00\x04\x0D\x01' + TunerStates[qualifier['Tuner']]
                for i in range(0, 10):
                    if i < len(channel):
                        if channel[i] in ['.', ',']:
                            data += b'\x2C'
                        else:
                            data += bytes([int(channel[i])])
                    else:
                        data += b'\xFF'

                ChannelDiscreteCommandCmdString = data + pack('B', sum(data) & 0xFF)
                self.__SetHelper('ChannelDiscreteCommand', ChannelDiscreteCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetChannelDiscreteCommand')
        else:
            self.Discard('Invalid Command for SetChannelDiscreteCommand')

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x8C\x00\x10\x03\x01\x01\xA1',
            'Off':  b'\x8C\x00\x10\x03\x01\x00\xA0'
        }

        if value in ValueStateValues:
            ClosedCaptionCmdString = ValueStateValues[value]
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def SetClosedCaptionAnalog(self, value, qualifier):

        ValueStateValues = {
            'CC1':      b'\x8C\x00\x10\x04\x02\x00\x01\xA3',
            'CC2':      b'\x8C\x00\x10\x04\x02\x00\x02\xA4',
            'CC3':      b'\x8C\x00\x10\x04\x02\x00\x03\xA5',
            'CC4':      b'\x8C\x00\x10\x04\x02\x00\x04\xA6',
            'Text1':    b'\x8C\x00\x10\x04\x02\x00\x05\xA7',
            'Text2':    b'\x8C\x00\x10\x04\x02\x00\x06\xA8',
            'Text3':    b'\x8C\x00\x10\x04\x02\x00\x07\xA9',
            'Text4':    b'\x8C\x00\x10\x04\x02\x00\x08\xAA'
        }

        if value in ValueStateValues:
            ClosedCaptionAnalogCmdString = ValueStateValues[value]
            self.__SetHelper('ClosedCaptionAnalog', ClosedCaptionAnalogCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaptionAnalog')

    def SetClosedCaptionDigital(self, value, qualifier):

        ValueStateValues = {
            'CC1':      b'\x8C\x00\x10\x04\x02\x01\x07\xAA',
            'CC2':      b'\x8C\x00\x10\x04\x02\x01\x08\xAB',
            'CC3':      b'\x8C\x00\x10\x04\x02\x01\x09\xAC',
            'CC4':      b'\x8C\x00\x10\x04\x02\x01\x0A\xAD',
            'Service1': b'\x8C\x00\x10\x04\x02\x01\x01\xA4',
            'Service2': b'\x8C\x00\x10\x04\x02\x01\x02\xA5',
            'Service3': b'\x8C\x00\x10\x04\x02\x01\x03\xA6',
            'Service4': b'\x8C\x00\x10\x04\x02\x01\x04\xA7',
            'Service5': b'\x8C\x00\x10\x04\x02\x01\x05\xA8',
            'Service6': b'\x8C\x00\x10\x04\x02\x01\x06\xA9'
        }

        if value in ValueStateValues:
            ClosedCaptionDigitalCmdString = ValueStateValues[value]
            self.__SetHelper('ClosedCaptionDigital', ClosedCaptionDigitalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaptionDigital')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV':           b'\x8C\x00\x02\x02\x01\x91',
            'Video':        b'\x8C\x00\x02\x03\x02\x01\x94',
            'HDMI 1':       b'\x8C\x00\x02\x03\x04\x01\x96',
            'HDMI 2':       b'\x8C\x00\x02\x03\x04\x02\x97',
            'HDMI 3':       b'\x8C\x00\x02\x03\x04\x03\x98',
            'HDMI 4':       b'\x8C\x00\x02\x03\x04\x04\x99'
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x01: 'HDMI 1',
            0x02: 'HDMI 2',
            0x03: 'HDMI 3',
            0x04: 'HDMI 4'
        }

        InputCmdString = b'\x83\x00\x02\xFF\xFF\x83'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[3] == 0x01:
                    self.WriteStatus('Input', 'TV', qualifier)
                elif res[3] == 0x02:
                    self.WriteStatus('Input', 'Video', qualifier)
                elif res[3] == 0x04:
                    self.WriteStatus('Input', ValueStateValues[res[4]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1':    b'\x8C\x00\x67\x03\x01\x00\xF7',
            '2':    b'\x8C\x00\x67\x03\x01\x01\xF8',
            '3':    b'\x8C\x00\x67\x03\x01\x02\xF9',
            '4':    b'\x8C\x00\x67\x03\x01\x03\xFA',
            '5':    b'\x8C\x00\x67\x03\x01\x04\xFB',
            '6':    b'\x8C\x00\x67\x03\x01\x05\xFC',
            '7':    b'\x8C\x00\x67\x03\x01\x06\xFD',
            '8':    b'\x8C\x00\x67\x03\x01\x07\xFE',
            '9':    b'\x8C\x00\x67\x03\x01\x08\xFF',
            '0':    b'\x8C\x00\x67\x03\x01\x09\x00',
            'Dot':  b'\x8C\x00\x67\x03\x97\x1D\xAA'
        }

        if value in ValueStateValues:
            KeypadCmdString = ValueStateValues[value]
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':       b'\x8C\x00\x67\x03\x01\x74\x6B',
            'Down':     b'\x8C\x00\x67\x03\x01\x75\x6C',
            'Left':     b'\x8C\x00\x67\x03\x01\x34\x2B',
            'Right':    b'\x8C\x00\x67\x03\x01\x33\x2A',
            'Home':     b'\x8C\x00\x67\x03\x01\x60\x57',
            'Return':   b'\x8C\x00\x67\x03\x97\x23\xB0',
            'Select':   b'\x8C\x00\x67\x03\x01\x65\x5C',
            'Options':  b'\x8C\x00\x67\x03\x97\x36\xC3'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x8C\x00\x00\x02\x01\x8F',
            'Off':  b'\x8C\x00\x00\x02\x00\x8E'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]

            if value == 'Off':
                self.__SetHelper('Standby', b'\x8C\x00\x01\x02\x01\x90', value, qualifier)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        PowerCmdString = b'\x83\x00\x00\xFF\xFF\x81'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x8C\x00\x0D\x03\x01\x00\x9D',
            'Off':  b'\x8C\x00\x0D\x03\x01\x01\x9E'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = b''.join([b'\x8C\x00\x05\x03\x01', pack('B', value)])
            VolumeCmdString += pack('B', sum(VolumeCmdString) & 0xFF)

            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x83\x00\x05\xFF\xFF\x86'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x01: 'Limit Over (over max value)',
            0x02: 'Limit Over (under min value)',
            0x03: 'Command Cancelled',
            0x04: 'Parse Error'
        }

        if response and response[1] in DEVICE_ERROR_CODES:
            self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, DEVICE_ERROR_CODES[response[1]])])
            return b''
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.update_delirex[command])
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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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