from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceSerialClass:
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
        self._DeviceID = '01'
        self.Models = {
            '75UH5E': self.lg_10_4060_ops,
            '86UH5E': self.lg_10_4060_ops,
            '98UH5E': self.lg_10_4060_no_ops,
            '98UM3E': self.lg_10_4060_no_ops,
            '86UM3E': self.lg_10_4060_ops,
            '75UM3E': self.lg_10_4060_ops,
            '49UH5E': self.lg_10_4060_ops,
            '55UH5E': self.lg_10_4060_ops,
            '65UH5E': self.lg_10_4060_ops,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Brightness': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SoundMode': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False' and self.DeviceID != '00':
            self.AddMatchString(re.compile(b'c [a-f0-9]{2,3} OK(0[26])x'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [a-f0-9]{2,3} OK(0[01])x'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'q [a-f0-9]{2,3} OK(0[0-4])x'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'm [a-f0-9]{2,3} OK(0[01])x'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [a-f0-9]{2,3} OK(90|a0|91|a1|92|a2|96|a6|c0|d0|e2)x'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'x [a-f0-9]{2,3} OK(0[0-58]|1[12])x'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'a [a-f0-9]{2,3} OK(0[01])x'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'y [a-f0-9]{2,3} OK(0[1-57])x'), self.__MatchSoundMode, None)
            self.AddMatchString(re.compile(b'd [a-f0-9]{2,3} OK(0[01])x'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [a-f0-9]{2,3} OK([0-9a-f]{2})x'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'([ceqmbxaydf]) [a-f0-9]{2,3} NG.*?x$'), self.__MatchError, None)

        self.setRegex = re.compile(b'[ceqmbxaydf] [a-f0-9]{2,3} (?:OK|NG).*?x$')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = 0x81 + value

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full Screen': '02',
            'Original': '06'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'kc {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'kc {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '02': 'Full Screen',
            '06': 'Original'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'ke {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'ke {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '00': 'On',
            '01': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Off': '00',
            'Minimum': '01',
            'Medium': '02',
            'Maximum': '03',
            'Automatic': '04'
        }

        if value in ValueStateValues:
            BrightnessCmdString = 'jq {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = 'jq {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)

    def __MatchBrightness(self, match, tag):

        ValueStateValues = {
            '00': 'Off',
            '01': 'Minimum',
            '02': 'Medium',
            '03': 'Maximum',
            '04': 'Automatic'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Brightness', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = 'km {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'km {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01'
        }

        if value in ValueStateValues:
            FreezeCmdString = 'kx {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def SetInput(self, value, qualifier):

        if value in self.InputStates:
            InputCmdString = 'xb {} {}\r'.format(self.DeviceID, self.InputStates[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'xb {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19',
            '0': '10'
        }

        if value in ValueStateValues:
            KeypadCmdString = 'mc {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Menu': '43',
            'OK': '44',
            'Exit': '5B',
            'Back': '28',
            'Clear': '2F'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'mc {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Mall/QSR': '00',
            'General': '01',
            'Gov./Corp.': '02',
            'Transportation': '03',
            'Education': '04',
            'Expert1': '05',
            'APS': '08',
            'Calibration': '11',
            'Hospital': '12'
        }

        if value in ValueStateValues:
            PictureModeCmdString = 'dx {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = 'dx {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '00': 'Mall/QSR',
            '01': 'General',
            '02': 'Gov./Corp.',
            '03': 'Transportation',
            '04': 'Education',
            '05': 'Expert1',
            '08': 'APS',
            '11': 'Calibration',
            '12': 'Hospital'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        if value in ValueStateValues:
            PowerCmdString = 'ka {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'ka {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSoundMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '01',
            'Music': '02',
            'Cinema': '03',
            'Sports': '04',
            'Game': '05',
            'News (Clear Voice III)': '07'
        }

        if value in ValueStateValues:
            SoundModeCmdString = 'dy {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSoundMode')

    def UpdateSoundMode(self, value, qualifier):

        SoundModeCmdString = 'dy {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def __MatchSoundMode(self, match, tag):

        ValueStateValues = {
            '01': 'Standard',
            '02': 'Music',
            '03': 'Cinema',
            '04': 'Sports',
            '05': 'Game',
            '07': 'News (Clear Voice III)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundMode', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = 'kd {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'kd {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {} {:02X}\r'.format(self.DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'kf {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Volume', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if b'NG' in response:
            self.Error(['{}: An error occurred.'.format(sourceCmdName)])
            return ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand' or self.DeviceID == '00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.setRegex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '00':
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

        error_map = {
            'c': 'Aspect Ratio/Keypad/Menu Navigation',
            'e': 'Audio Mute',
            'q': 'Brightness',
            'm': 'Executive Mode',
            'b': 'Input',
            'x': 'Picture Mode',
            'a': 'Power',
            'y': 'Sound Mode',
            'd': 'Video Mute',
            'f': 'Volume'
        }

        self.Error(['{}: An error occurred.'.format(error_map[match.group(1).decode()])])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def lg_10_4060_ops(self):
        self.InputStates = {
            'HDMI 1 (DTV)':             '90',
            'HDMI 1 (PC)':              'A0',
            'HDMI 2 (DTV)':             '91',
            'HDMI 2 (PC)':              'A1',
            'OPS/HDMI 3/DVI-D (DTV)':   '92',
            'OPS/HDMI 3/DVI-D (PC)':    'A2',
            'DisplayPort (DTV)':        'C0',
            'DisplayPort (PC)':         'D0',
            'Multi Screen':             'E2'
        }

        self.InputValues = {
            '90': 'HDMI 1 (DTV)',
            'a0': 'HDMI 1 (PC)',
            '91': 'HDMI 2 (DTV)',
            'a1': 'HDMI 2 (PC)',
            '92': 'OPS/HDMI 3/DVI-D (DTV)',
            'a2': 'OPS/HDMI 3/DVI-D (PC)',
            'c0': 'DisplayPort (DTV)',
            'd0': 'DisplayPort (PC)',
            'e2': 'Multi Screen'
        }




    def lg_10_4060_no_ops(self):
        self.InputStates = {
            'HDMI 1 (DTV)':         '90',
            'HDMI 1 (PC)':          'A0',
            'HDMI 2 (DTV)':         '91',
            'HDMI 2 (PC)':          'A1',
            'HDMI 3/DVI-D (DTV)':   '96',
            'HDMI 3/DVI-D (PC)':    'A6',
            'DisplayPort (DTV)':    'C0',
            'DisplayPort (PC)':     'D0',
            'Multi Screen':         'E2'
        }

        self.InputValues = {
            '90': 'HDMI 1 (DTV)',
            'a0': 'HDMI 1 (PC)',
            '91': 'HDMI 2 (DTV)',
            'a1': 'HDMI 2 (PC)',
            '96': 'HDMI 3/DVI-D (DTV)',
            'a6': 'HDMI 3/DVI-D (PC)',
            'c0': 'DisplayPort (DTV)',
            'd0': 'DisplayPort (PC)',
            'e2': 'Multi Screen'
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
        self._DeviceID = '01'
        self.Models = {
            '75UH5E': self.lg_10_4060_ops,
            '86UH5E': self.lg_10_4060_ops,
            '98UH5E': self.lg_10_4060_no_ops,
            '98UM3E': self.lg_10_4060_no_ops,
            '86UM3E': self.lg_10_4060_ops,
            '75UM3E': self.lg_10_4060_ops,
            '49UH5E': self.lg_10_4060_ops,
            '55UH5E': self.lg_10_4060_ops,
            '65UH5E': self.lg_10_4060_ops,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'SoundMode': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        if self.Unidirectional == 'False' and self.DeviceID != '00':
            self.AddMatchString(re.compile(b'c [a-f0-9]{2,3} OK(0[26])x'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [a-f0-9]{2,3} OK(0[01])x'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'q [a-f0-9]{2,3} OK(0[0-4])x'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'm [a-f0-9]{2,3} OK(0[01])x'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [a-f0-9]{2,3} OK(90|a0|91|a1|92|a2|96|a6|c0|d0|e2)x'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'x [a-f0-9]{2,3} OK(0[0-58]|1[12])x'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'y [a-f0-9]{2,3} OK(0[1-57])x'), self.__MatchSoundMode, None)
            self.AddMatchString(re.compile(b'd [a-f0-9]{2,3} OK(0[01])x'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [a-f0-9]{2,3} OK([0-9a-f]{2})x'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'([ceqmbxaydf]) [a-f0-9]{2,3} NG.*?x$'), self.__MatchError, None)

        self.setRegex = re.compile(b'[ceqmbxaydf] [a-f0-9]{2,3} (?:OK|NG).*?x$')
        
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID= 0x81 + value

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full Screen':  '02',
            'Original':     '06'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'kc {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'kc {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '02': 'Full Screen',
            '06': 'Original'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '00',
            'Off':  '01'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'ke {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'ke {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '00': 'On',
            '01': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Off':          '00',
            'Minimum':      '01',
            'Medium':       '02',
            'Maximum':      '03',
            'Automatic':    '04'
        }

        if value in ValueStateValues:
            BrightnessCmdString = 'jq {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = 'jq {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)

    def __MatchBrightness(self, match, tag):

        ValueStateValues = {
            '00': 'Off',
            '01': 'Minimum',
            '02': 'Medium',
            '03': 'Maximum',
            '04': 'Automatic'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Brightness', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = 'km {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'km {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':   '00',
            'Off':  '01'
        }

        if value in ValueStateValues:
            FreezeCmdString = 'kx {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')
    def SetInput(self, value, qualifier):

        if value in self.InputStates:
            InputCmdString = 'xb {} {}\r'.format(self.DeviceID, self.InputStates[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'xb {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19',
            '0': '10'
        }

        if value in ValueStateValues:
            KeypadCmdString = 'mc {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':       '40',
            'Down':     '41',
            'Left':     '07',
            'Right':    '06',
            'Menu':     '43',
            'OK':       '44',
            'Exit':     '5B',
            'Back':     '28',
            'Clear':    '2F'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'mc {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')
            
    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Mall/QSR':         '00',
            'General':          '01',
            'Gov./Corp.':       '02',
            'Transportation':   '03',
            'Education':        '04',
            'Expert1':          '05',
            'APS':              '08',
            'Calibration':      '11',
            'Hospital':			'12'
        }

        if value in ValueStateValues:
            PictureModeCmdString = 'dx {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = 'dx {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '00': 'Mall/QSR',
            '01': 'General',
            '02': 'Gov./Corp.',
            '03': 'Transportation',
            '04': 'Education',
            '05': 'Expert1',
            '08': 'APS',
            '11': 'Calibration',
            '12': 'Hospital'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = 'ka {} 00\r'.format(self.DeviceID)
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)
        
    def SetSoundMode(self, value, qualifier):

        ValueStateValues = {
            'Standard':                 '01',
            'Music':                    '02',
            'Cinema':                   '03',
            'Sports':                   '04',
            'Game':                     '05',
            'News (Clear Voice III)':   '07'
        }

        if value in ValueStateValues:
            SoundModeCmdString = 'dy {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSoundMode')

    def UpdateSoundMode(self, value, qualifier):

        SoundModeCmdString = 'dy {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def __MatchSoundMode(self, match, tag):

        ValueStateValues = {
            '01': 'Standard',
            '02': 'Music',
            '03': 'Cinema',
            '04': 'Sports',
            '05': 'Game',
            '07': 'News (Clear Voice III)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundMode', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = 'kd {} {}\r'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'kd {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {} {:02X}\r'.format(self.DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'kf {} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Volume', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if b'NG' in response:
            self.Error(['{}: An error occurred.'.format(sourceCmdName)])
            return ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        
        self.Debug = True
        if self.Unidirectional == 'True' or self.DeviceID == '00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.setRegex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '00':
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

        error_map = {
            'c': 'Aspect Ratio/Keypad/Menu Navigation',
            'e': 'Audio Mute',
            'q': 'Brightness',
            'm': 'Executive Mode',
            'b': 'Input',
            'x': 'Picture Mode',
            'a': 'Power Off',
            'y': 'Sound Mode',
            'd': 'Video Mute',
            'f': 'Volume'
        }

        self.Error(['{}: An error occurred.'.format(error_map[match.group(1).decode()])])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def lg_10_4060_ops(self):
        self.InputStates = {
            'HDMI 1 (DTV)':             '90',
            'HDMI 1 (PC)':              'A0',
            'HDMI 2 (DTV)':             '91',
            'HDMI 2 (PC)':              'A1',
            'OPS/HDMI 3/DVI-D (DTV)':   '92',
            'OPS/HDMI 3/DVI-D (PC)':    'A2',
            'DisplayPort (DTV)':        'C0',
            'DisplayPort (PC)':         'D0',
            'Multi Screen':             'E2'
        }

        self.InputValues = {
            '90': 'HDMI 1 (DTV)',
            'a0': 'HDMI 1 (PC)',
            '91': 'HDMI 2 (DTV)',
            'a1': 'HDMI 2 (PC)',
            '92': 'OPS/HDMI 3/DVI-D (DTV)',
            'a2': 'OPS/HDMI 3/DVI-D (PC)',
            'c0': 'DisplayPort (DTV)',
            'd0': 'DisplayPort (PC)',
            'e2': 'Multi Screen'
        }

    def lg_10_4060_no_ops(self):
        self.InputStates = {
            'HDMI 1 (DTV)':         '90',
            'HDMI 1 (PC)':          'A0',
            'HDMI 2 (DTV)':         '91',
            'HDMI 2 (PC)':          'A1',
            'HDMI 3/DVI-D (DTV)':   '96',
            'HDMI 3/DVI-D (PC)':    'A6',
            'DisplayPort (DTV)':    'C0',
            'DisplayPort (PC)':     'D0',
            'Multi Screen':         'E2'
        }

        self.InputValues = {
            '90': 'HDMI 1 (DTV)',
            'a0': 'HDMI 1 (PC)',
            '91': 'HDMI 2 (DTV)',
            'a1': 'HDMI 2 (PC)',
            '96': 'HDMI 3/DVI-D (DTV)',
            'a6': 'HDMI 3/DVI-D (PC)',
            'c0': 'DisplayPort (DTV)',
            'd0': 'DisplayPort (PC)',
            'e2': 'Multi Screen'
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
