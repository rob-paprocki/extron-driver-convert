from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceSerialClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = '01'
        self.Models = {
            '75UH5C': self.lg_10_2427_A,
            '75UM3C': self.lg_10_2427_B,
            '86UH5C': self.lg_10_2427_A,
            '86UM3C': self.lg_10_2427_B,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'EnergySaving': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c [0-9a-f]{2,3} OK(01|02|04|06|09|10|11|12|13|14|15|16|17|18|19|1a|1b|1c|1d|1e|1f)x'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [0-9a-f]{2,3} OK(01|00)x'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'q [0-9a-f]{2,3} OK(00|01|02|03|04|05)x'), self.__MatchEnergySaving, None)
            self.AddMatchString(re.compile(b'm [0-9a-f]{2,3} OK(01|00)x'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [0-9a-f]{2,3} OK(90|a0|91|a1|92|a2|95|a5|c0|d0|e2)x'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'x [0-9a-f]{2,3} OK(00|01|02|03|04|05|08|09|11)x'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'a [0-9a-f]{2,3} OK(01|00)x'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd [0-9a-f]{2,3} OK(01|00)x'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9a-f]{2,3} OK([0-9a-f]{2})x'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(c|e|m|b|a|d|f|x|q) [0-9a-f]{2,3} NG(.*?)x'), self.__MatchError, None)

        self.regexSet = re.compile(b'(OK|NG)[0-9a-f]{2}x')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 0 <= int(value) <= 1000:
            self._DeviceID = '{0:02X}'.format(int(value))
        else:
            print('Invalid Device ID Parameter. Range is from 1 - 1000')

    def SetPower(self, value, qualifier):

        Value = {
            'On': '01',
            'Off': '00'
            }[value]

        CmdString = 'ka {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        self.__UpdateHelper('Power', 'ka {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchPower(self, match, tag):

        Value = {
            '01': 'On',
            '00': 'Off'
            }[match.group(1).decode()]

        self.WriteStatus('Power', Value, None)

    def SetInput(self, value, qualifier):

        CmdString = 'xb {0} {1}\r'.format(self._DeviceID, self.Input[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', 'xb {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchInput(self, match, tag):
        self.WriteStatus('Input', self.Inputs[match.group(1).decode()], None)

    def SetAspectRatio(self, value, qualifier):

        Value = {
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Set by Program': '06',
            'Just Scan': '09',
            'Cinema Zoom 1': '10',
            'Cinema Zoom 2': '11',
            'Cinema Zoom 3': '12',
            'Cinema Zoom 4': '13',
            'Cinema Zoom 5': '14',
            'Cinema Zoom 6': '15',
            'Cinema Zoom 7': '16',
            'Cinema Zoom 8': '17',
            'Cinema Zoom 9': '18',
            'Cinema Zoom 10': '19',
            'Cinema Zoom 11': '1a',
            'Cinema Zoom 12': '1b',
            'Cinema Zoom 13': '1c',
            'Cinema Zoom 14': '1d',
            'Cinema Zoom 15': '1e',
            'Cinema Zoom 16': '1f'
            }[value]

        CmdString = 'kc {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        self.__UpdateHelper('AspectRatio', 'kc {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        Values = {
            '01': '4:3',
            '02': '16:9',
            '04': 'Zoom',
            '06': 'Set by Program',
            '09': 'Just Scan',
            '10': 'Cinema Zoom 1',
            '11': 'Cinema Zoom 2',
            '12': 'Cinema Zoom 3',
            '13': 'Cinema Zoom 4',
            '14': 'Cinema Zoom 5',
            '15': 'Cinema Zoom 6',
            '16': 'Cinema Zoom 7',
            '17': 'Cinema Zoom 8',
            '18': 'Cinema Zoom 9',
            '19': 'Cinema Zoom 10',
            '1a': 'Cinema Zoom 11',
            '1b': 'Cinema Zoom 12',
            '1c': 'Cinema Zoom 13',
            '1d': 'Cinema Zoom 14',
            '1e': 'Cinema Zoom 15',
            '1f': 'Cinema Zoom 16'
            }[match.group(1).decode()]

        self.WriteStatus('AspectRatio', Values, None)

    def SetEnergySaving(self, value, qualifier):

        Value = {
            'Off': '00',
            'Minimum': '01',
            'Medium': '02',
            'Maximum': '03',
            'Automatic': '04',
            'Screen Off': '05'
        }[value]

        CmdString = 'jq {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('EnergySaving', CmdString, value, qualifier)

    def UpdateEnergySaving(self, value, qualifier):
        self.__UpdateHelper('EnergySaving', 'jq {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchEnergySaving(self, match, tag):

        Values = {
            '00': 'Off',
            '01': 'Minimum',
            '02': 'Medium',
            '03': 'Maximum',
            '04': 'Automatic',
            '05': 'Screen Off'
        }[match.group(1).decode()]

        self.WriteStatus('EnergySaving', Values, None)

    def SetFreeze(self, value, qualifier):

        Value = {
            'On': '00',
            'Off': '01'
        }[value]

        CmdString = 'kx {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('Freeze', CmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        Value = {
            'Vivid': '00',
            'Standard': '01',
            'Cinema': '02',
            'Sports': '03',
            'Game': '04',
            'Expert': '05',
            'APS': '08',
            'Photos': '09',
            'Calibration': '11'
        }[value]

        CmdString = 'dx {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('PictureMode', CmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        self.__UpdateHelper('PictureMode', 'dx {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchPictureMode(self, match, tag):

        Values = {
            '00': 'Vivid',
            '01': 'Standard',
            '02': 'Cinema',
            '03': 'Sports',
            '04': 'Game',
            '05': 'Expert',
            '08': 'APS',
            '09': 'Photos',
            '11': 'Calibration'
        }[match.group(1).decode()]

        self.WriteStatus('PictureMode', Values, None)

    def SetAudioMute(self, value, qualifier):

        Value = {
            'On': '00',
            'Off': '01'
            }[value]

        CmdString = 'ke {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', 'ke {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchAudioMute(self, match, tag):

        Values = {
            '00': 'On',
            '01': 'Off'
            }[match.group(1).decode()]

        self.WriteStatus('AudioMute', Values, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'kf {0} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', 'kf {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1).decode(), 16), None)

    def SetKeypad(self, value, qualifier):

        Value = {
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
        }[value]

        CmdString = 'mc {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('Keypad', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        Value = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Menu': '45',
            'Ok': '44',
            'Exit': '5b',
            'Back': '28'
            }[value]

        CmdString = 'mc {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        Value = {
            'On': '01',
            'Off': '00'
            }[value]

        CmdString = 'kd {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', 'kd {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchVideoMute(self, match, tag):

        Values = {
            '01': 'On',
            '00': 'Off'
            }[match.group(1).decode()]
        self.WriteStatus('VideoMute', Values, None)

    def SetExecutiveMode(self, value, qualifier):

        Value = {
            'On': '01',
            'Off': '00'
            }[value]

        CmdString = 'km {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        self.__UpdateHelper('ExecutiveMode', 'km {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        Values = {
            '01': 'On',
            '00': 'Off'
            }[match.group(1).decode()]

        self.WriteStatus('ExecutiveMode', Values, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'NG' in response:
            print('Error response from Set {0} command'.format(sourceCmdName))

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regexSet)
            if not res:
                print('Invalid/unexpected response for', command)
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
            print('Inappropriate Command ', command)
        else:

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)

    def __MatchError(self, match, tag):

        ErrorState = {
            'c' : 'Aspect Ratio',
            'e' : 'Audio Mute',
            'b' : 'Input',
            'x' : 'Picture Mode',
            'a' : 'Power',
            'm' : 'Executive Mode',
            'd' : 'Video Mute',
            'f' : 'Volume',
            'q' : 'Energy Saving'
            }

        temp1 = ErrorState[match.group(1).decode()]
        temp2 = match.group(2).decode()
        value = 'Command: {0}. Error: {1}'.format(temp1,temp2)
        print('value for', command)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def lg_10_2427_A(self):


        self.Input = {
            'HDMI1 (DTV)'            : '90',
            'HDMI1 (PC)'             : 'a0',
            'HDMI 2 (DTV)'           : '91',
            'HDMI 2 (PC)'            : 'a1',
            'OPS/HDMI 3/DVI-D (DTV)' : '92',
            'OPS/HDMI 3/DVI-D (PC)'  : 'a2',
            'DisplayPort (DTV)'      : 'c0',
            'DisplayPort (PC)'       : 'd0',
            'Multi Screen'           : 'e2'
        }

        self.Inputs = {
            '90' : 'HDMI1 (DTV)',
            'a0' : 'HDMI1 (PC)',
            '91' : 'HDMI 2 (DTV)',
            'a1' : 'HDMI 2 (PC)',
            '92' : 'OPS/HDMI 3/DVI-D (DTV)',
            'a2' : 'OPS/HDMI 3/DVI-D (PC)',
            'c0' : 'DisplayPort (DTV)',
            'd0' : 'DisplayPort (PC)',
            'e2' : 'Multi Screen'
        }


    def lg_10_2427_B(self):


        self.Input = {
            'HDMI 1 (DTV)'      : '90',
            'HDMI 1 (PC)'       : 'a0',
            'HDMI 2 (DTV)'      : '91',
            'HDMI 2 (PC)'       : 'a1',
            'OPS/DVI-D (DTV)'   : '95',
            'OPS/DVI-D (PC)'    : 'a5',
            'DisplayPort (DTV)' : 'c0',
            'DisplayPort (PC)'  : 'd0',
            'Multi Screen'      : 'e2'
        }

        self.Inputs = {
            '90' : 'HDMI 1 (DTV)',
            'a0' : 'HDMI 1 (PC)',
            '91' : 'HDMI 2 (DTV)',
            'a1' : 'HDMI 2 (PC)',
            '95' : 'OPS/DVI-D (DTV)',
            'a5' : 'OPS/DVI-D (PC)',
            'c0' : 'DisplayPort (DTV)',
            'd0' : 'DisplayPort (PC)',
            'e2' : 'Multi Screen'
        }

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
            print(command, 'does not exist in the module')

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
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

class DeviceEthernetClass:

    def __init__(self):

        self.Debug = False
        self._DeviceID = '01'
        self.Models = {
            '75UH5C': self.lg_10_2427_A,
            '75UM3C': self.lg_10_2427_B,
            '86UH5C': self.lg_10_2427_A,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'EnergySaving': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 0 <= int(value) <= 1000:
            self._DeviceID = '{0:02X}'.format(int(value))
        else:
            print('Invalid Device ID Parameter. Range is from 1 - 1000')
        

    def SetPower(self, value, qualifier):

        Value = {
            'Off': '00'
        }[value]

        CmdString = 'ka {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('Power', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        CmdString = 'xb {0} {1}\r'.format(self._DeviceID, self.Input[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        Value = {
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Set by Program': '06',
            'Just Scan': '09',
            'Cinema Zoom 1': '10',
            'Cinema Zoom 2': '11',
            'Cinema Zoom 3': '12',
            'Cinema Zoom 4': '13',
            'Cinema Zoom 5': '14',
            'Cinema Zoom 6': '15',
            'Cinema Zoom 7': '16',
            'Cinema Zoom 8': '17',
            'Cinema Zoom 9': '18',
            'Cinema Zoom 10': '19',
            'Cinema Zoom 11': '1a',
            'Cinema Zoom 12': '1b',
            'Cinema Zoom 13': '1c',
            'Cinema Zoom 14': '1d',
            'Cinema Zoom 15': '1e',
            'Cinema Zoom 16': '1f'
        }[value]

        CmdString = 'kc {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def SetEnergySaving(self, value, qualifier):

        Value = {
            'Off': '00',
            'Minimum': '01',
            'Medium': '02',
            'Maximum': '03',
            'Automatic': '04',
            'Screen Off': '05'
        }[value]

        CmdString = 'jq {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('EnergySaving', CmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        Value = {
            'On': '00',
            'Off': '01'
        }[value]

        CmdString = 'kx {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('Freeze', CmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        Value = {
            'Vivid': '00',
            'Standard': '01',
            'Cinema': '02',
            'Sports': '03',
            'Game': '04',
            'Expert': '05',
            'APS': '08',
            'Photos': '09',
            'Calibration': '11'
        }[value]

        CmdString = 'dx {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('PictureMode', CmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        Value = {
            'On': '00',
            'Off': '01'
        }[value]

        CmdString = 'ke {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100 and self.__SafeToSet('Volume'):
            CmdString = 'kf {0} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def SetKeypad(self, value, qualifier):

        Value = {
            '1': '10',
            '2': '11',
            '3': '12',
            '4': '13',
            '5': '14',
            '6': '15',
            '7': '16',
            '8': '17',
            '9': '18',
            '0': '19'
        }[value]

        CmdString = 'mc {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('Keypad', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        Value = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Menu': '45',
            'Ok': '44',
            'Exit': '5b',
            'Back': '28'
        }[value]

        CmdString = 'mc {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        Value = {
            'On': '01',
            'Off': '00'
        }[value]

        CmdString = 'kd {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        Value = {
            'On': '01',
            'Off': '00'
        }[value]

        CmdString = 'km {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def lg_10_2427_A(self):

        self.Input = {
            'HDMI1 (DTV)': '90',
            'HDMI1 (PC)': 'a0',
            'HDMI 2 (DTV)': '91',
            'HDMI 2 (PC)': 'a1',
            'OPS/HDMI 3/DVI-D (DTV)': '92',
            'OPS/HDMI 3/DVI-D (PC)': 'a2',
            'DisplayPort (DTV)': 'c0',
            'DisplayPort (PC)': 'd0',
            'Multi Screen': 'e2'
        }

    def lg_10_2427_B(self):

        self.Input = {
            'HDMI 1 (DTV)': '90',
            'HDMI 1 (PC)': 'a0',
            'HDMI 2 (DTV)': '91',
            'HDMI 2 (PC)': 'a1',
            'OPS/DVI-D (DTV)': '95',
            'OPS/DVI-D (PC)': 'a5',
            'DisplayPort (DTV)': 'c0',
            'DisplayPort (PC)': 'd0',
            'Multi Screen': 'e2'
        }
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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
