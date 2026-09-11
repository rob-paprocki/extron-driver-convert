from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'ChannelDiscreteCommand': {'Parameters': ['Tuner'], 'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ClosedCaptionAnalog': {'Status': {}},
            'ClosedCaptionDigital': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'StandbyMode': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.update_delirex = {
            'AudioMute': re.compile(b'\x70[\x00-\x04]\x03\x01[\x00\x01][\x00-\xFF]'),
            'Input': re.compile(b'\x70[\x00-\x04][\x02\x03][\x01\x02\x04][\x00-\xFF]{1,2}'),
            'Power': re.compile(b'\x70[\x00-\x04]\x02[\x00\x01][\x00-\xFF]'),
            'Volume': re.compile(b'\x70[\x00-\x04]\x03\x01[\x00-\x64][\x00-\xFF]')
        }

    def checksum(self, s):

        return bytes([sum(s) & 0xFF])

    def build_set(self, f, d):

        s = b'\x8C\x00' + f + bytes([len(d) + 1]) + d
        return s + self.checksum(s)

    def build_get(self, f):

        s = b'\x83\x00' + f + b'\xFF\xFF'
        return s + self.checksum(s)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom': b'\x00',
            'Full': b'\x01',
            'Zoom': b'\x02',
            'Normal': b'\x03',
            'Normal (PC)': b'\x05',
            'Full 1 (PC)': b'\x06',
            'Full 2 (PC)': b'\x07'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = self.build_set(b'\x44', b'\x01' + ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = self.build_set(b'\x06', b'\x01' + ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        AudioMuteCmdString = self.build_get(b'\x06')
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x00',
            'Down': b'\x01'
        }

        if value in ValueStateValues:
            ChannelCmdString = self.build_set(b'\x04', b'\x00' + ValueStateValues[value])
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def SetChannelDiscreteCommand(self, value, qualifier):

        TunerStates = {
            'Terr Digital': b'\x01',
            'Terr Analog': b'\x02',
            'CATV': b'\x03',
            'BS Digital': b'\x04',
            'CS Digital': b'\x05',
            'DVB-S': b'\x06',
            'DVB-S2': b'\x07',
            'Cable Analog': b'\x0A',
            'Cable Digital': b'\x0B'
        }

        channel = value
        if qualifier['Tuner'] in TunerStates and channel and 1 <= len(channel) <= 10:
            data = b'\x01' + TunerStates[qualifier['Tuner']]
            for i in range(0, 10):
                if i < len(channel):
                    if channel[i] in ['.', ',']:
                        data += b'\x2C'
                    else:
                        data += bytes([int(channel[i])])
                else:
                    data += b'\xFF'

            ChannelDiscreteCommandCmdString = self.build_set(b'\x04', data)
            self.__SetHelper('ChannelDiscreteCommand', ChannelDiscreteCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelDiscreteCommand')

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        if value in ValueStateValues:
            ClosedCaptionCmdString = self.build_set(b'\x10', b'\x01' + ValueStateValues[value])
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def SetClosedCaptionAnalog(self, value, qualifier):

        ValueStateValues = {
            'CC1': b'\x01',
            'CC2': b'\x02',
            'CC3': b'\x03',
            'CC4': b'\x04',
            'Text1': b'\x05',
            'Text2': b'\x06',
            'Text3': b'\x07',
            'Text4': b'\x08'
        }

        if value in ValueStateValues:
            ClosedCaptionAnalogCmdString = self.build_set(b'\x10', b'\x02\x00' + ValueStateValues[value])
            self.__SetHelper('ClosedCaptionAnalog', ClosedCaptionAnalogCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaptionAnalog')

    def SetClosedCaptionDigital(self, value, qualifier):

        ValueStateValues = {
            'CC1': b'\x07',
            'CC2': b'\x08',
            'CC3': b'\x09',
            'CC4': b'\x0A',
            'Service1': b'\x01',
            'Service2': b'\x02',
            'Service3': b'\x03',
            'Service4': b'\x04',
            'Service5': b'\x05',
            'Service6': b'\x06'
        }

        if value in ValueStateValues:
            ClosedCaptionDigitalCmdString = self.build_set(b'\x10', b'\x02\x01' + ValueStateValues[value])
            self.__SetHelper('ClosedCaptionDigital', ClosedCaptionDigitalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaptionDigital')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': b'\x01',
            'Video': b'\x02\x01',
            'HDMI 1': b'\x04\x01',
            'HDMI 2': b'\x04\x02',
            'HDMI 3': b'\x04\x03',
            'HDMI 4': b'\x04\x04'
        }

        if value in ValueStateValues:
            InputCmdString = self.build_set(b'\x02', ValueStateValues[value])
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

        InputCmdString = self.build_get(b'\x02')
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
            '1': b'\x01\x00',
            '2': b'\x01\x01',
            '3': b'\x01\x02',
            '4': b'\x01\x03',
            '5': b'\x01\x04',
            '6': b'\x01\x05',
            '7': b'\x01\x06',
            '8': b'\x01\x07',
            '9': b'\x01\x08',
            '0': b'\x01\x09',
            'Dot': b'\x97\x1D'
        }

        if value in ValueStateValues:
            KeypadCmdString = self.build_set(b'\x67', ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x01\x74',
            'Down': b'\x01\x75',
            'Left': b'\x01\x34',
            'Right': b'\x01\x33',
            'Select': b'\x01\x65',
            'Return': b'\x97\x23',
            'Options': b'\x97\x36',
            'Home': b'\x01\x60'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = self.build_set(b'\x67', ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        if value in ValueStateValues:
            PowerCmdString = self.build_set(b'\x00', ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        PowerCmdString = self.build_get(b'\x00')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetStandbyMode(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'\x01',
            'Disable': b'\x00'
        }

        if value in ValueStateValues:
            StandbyModeCmdString = self.build_set(b'\x01', ValueStateValues[value])
            self.__SetHelper('StandbyMode', StandbyModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandbyMode')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x00',
            'Off': b'\x01'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = self.build_set(b'\x0D', b'\x01' + ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = self.build_set(b'\x05', b'\x01' + bytes([value]))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.build_get(b'\x05')
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
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*SNAMUT0{15}([01])\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*SNINPT0{7}([0135])0{7}([0-4])\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*SNPOWR0{15}([01])\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*SNPMUT0{15}([01])\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*SNVOLU0{13}(\d{3})\n'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(b'\*SA(AMUT|IRCC|INPT|POWR|PMUT|VOLU)[FN]{16}\n'), self.__MatchError, None)

        self.update_delirex = {
            'AudioMute':    re.compile('\*SAAMUT0{15}([01])\n'),
            'Input':        re.compile('\*SAINPT0{7}([0135])0{7}([0-4])\n'),
            'Power':        re.compile('\*SAPOWR0{15}([01])\n'),
            'VideoMute':    re.compile('\*SAPMUT0{15}([01])\n'),
            'Volume':       re.compile('\*SAVOLU0{13}(\d{3})\n')
        }

    def build_set(self, f, d):

        return '*SC{}{:0>16}\n'.format(f, d)

    def build_get(self, f):

        return '*SE{}{}\n'.format(f, '#' * 16)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = self.build_set('AMUT', ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = self.build_get('AMUT')
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
            'Up':   '33',
            'Down': '34'
        }

        if value in ValueStateValues:
            ChannelCmdString = self.build_set('IRCC', ValueStateValues[value])
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV':               ('0', '0'),
            'Video':            ('3', '1'),
            'HDMI 1':           ('1', '1'),
            'HDMI 2':           ('1', '2'),
            'HDMI 3':           ('1', '3'),
            'HDMI 4':           ('1', '4'),
            'Screen Mirroring': ('5', '1')
        }

        if value in ValueStateValues:
            InputCmdString = self.build_set('INPT', '{:0>8}{:0>8}'.format(ValueStateValues[value][0], ValueStateValues[value][1]))
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
            ('1', '4'): 'HDMI 4',
            ('5', '1'): 'Screen Mirroring'
        }

        InputCmdString = self.build_get('INPT')
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
            '3': 'Video',
            '5': 'Screen Mirroring'
        }

        if match.group(1).decode() == '1':
            value = 'HDMI {}'.format(match.group(2).decode())
        else:
            value = ValueStateValues[match.group(1).decode()]

        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1':    '18',
            '2':    '19',
            '3':    '20',
            '4':    '21',
            '5':    '22',
            '6':    '23',
            '7':    '24',
            '8':    '25',
            '9':    '26',
            '0':    '27',
            'Dot':  '38'
        }

        if value in ValueStateValues:
            KeypadCmdString = self.build_set('IRCC', ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':       '09',
            'Down':     '10',
            'Left':     '12',
            'Right':    '11',
            'Select':   '13',
            'Return':   '08',
            'Options':  '07',
            'Home':     '06'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = self.build_set('IRCC', ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            PowerCmdString = self.build_set('POWR', ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = self.build_get('POWR')
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
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = self.build_set('PMUT', ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = self.build_get('PMUT')
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
            VolumeCmdString = self.build_set('VOLU', value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.build_get('VOLU')
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                match = self.update_delirex['Volume'].search(res)
                value = int(match.group(1))
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