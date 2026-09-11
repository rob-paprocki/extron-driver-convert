from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Loudness': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Preset': {'Status': {}},
            'Standby': {'Status': {}},
            'SubscribePower': {'Status': {}},
            'Zone1Input': {'Status': {}},
            'Zone1Mute': {'Status': {}},
            'Zone1Power': {'Status': {}},
            'Zone1Volume': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Mute': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'loudness value="(On|Off)"'), self.__MatchLoudness, None)
            self.AddMatchString(re.compile(b'source value="(HDMI \d|Coax \d|Optical \d|ARC|USB stream|Tuner 1|Analog \d|Analog 7.1|Front)"'), self.__MatchZone1Input, None)
            self.AddMatchString(re.compile(b'(zone2_power|power) value="(On|Off)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'(zone2_volume|volume) value="(-?[0-9\.]+)"'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'zone2_input value="(Analog \d|Analog 7.1|Front|ARC|Ethernet|Follow Main|Coax \d|Optical \d)"'), self.__MatchZone2Input, None)

    def SetStandby(self, value, qualifier):

        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><Standby value="0" ack="no" /></emotivaControl>'
        self.__SetHelper('Standby', Cmdstring, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu': 'menu',
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Enter': 'enter'
        }

        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><{0} value="0" ack="no" /></emotivaControl>'.format(States[value])
        self.__SetHelper('MenuNavigation', Cmdstring, value, qualifier)

    def SetLoudness(self, value, qualifier):

        States = {
            'On': 'loudness_on',
            'Off': 'loudness_off'
        }

        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><{0} value="0" ack="no" /></emotivaControl>'.format(States[value])
        self.__SetHelper('Loudness', Cmdstring, value, qualifier)

    def UpdateLoudness(self, value, qualifier):
        CmdString = '<?xml version="1.0" encoding="utf-8"?><emotivaSubscription><loudness /></emotivaSubscription>'
        self.__UpdateHelper('Loudness', CmdString, value, qualifier)

    def __MatchLoudness(self, match, tag):
        self.WriteStatus('Loudness', match.group(1).decode(), None)

    def SetPreset(self, value, qualifier):

        States = {
            'Music': 'music',
            'Movie': 'movie'
        }

        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><{0} value="0" ack="no" /></emotivaControl>'.format(States[value])
        self.__SetHelper('Preset', Cmdstring, value, qualifier)

    def SetZone1Mute(self, value, qualifier):

        States = {
            'On': 'mute_on',
            'Off': 'mute_off'
        }

        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><{0} value="0" ack="no" /></emotivaControl>'.format(States[value])
        self.__SetHelper('Zone1Mute', Cmdstring, value, qualifier)

    def SetZone1Input(self, value, qualifier):

        States = {
            'HDMI 1': 'hdmi1',
            'HDMI 2': 'hdmi2',
            'HDMI 3': 'hdmi3',
            'HDMI 4': 'hdmi4',
            'HDMI 5': 'hdmi5',
            'HDMI 6': 'hdmi6',
            'HDMI 7': 'hdmi7',
            'HDMI 8': 'hdmi8',
            'Coax 1': 'coax1',
            'Coax 2': 'coax2',
            'Coax 3': 'coax3',
            'Coax 4': 'coax4',
            'Optical 1': 'optical1',
            'Optical 2': 'optical2',
            'Optical 3': 'optical3',
            'Optical 4': 'optical4',
            'ARC': 'ARC',
            'USB': 'usb_stream',
            'Tuner': 'tuner',
            'Analog 1': 'analog1',
            'Analog 2': 'analog2',
            'Analog 3': 'analog3',
            'Analog 4': 'analog4',
            'Analog 5': 'analog5',
            'Analog 7.1': 'analog7.1',
            'Front': 'front_in'
        }

        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><{0} value="0" ack="no" /></emotivaControl>'.format(States[value])
        self.__SetHelper('Zone1Input', Cmdstring, value, qualifier)

    def UpdateZone1Input(self, value, qualifier):
        CmdString = '<?xml version="1.0" encoding="utf-8"?><emotivaSubscription><source /></emotivaSubscription>'
        self.__UpdateHelper('Zone1Input', CmdString, value, qualifier)

    def __MatchZone1Input(self, match, tag):

        States = {
            'HDMI 1': 'HDMI 1',
            'HDMI 2': 'HDMI 2',
            'HDMI 3': 'HDMI 3',
            'HDMI 4': 'HDMI 4',
            'HDMI 5': 'HDMI 5',
            'HDMI 6': 'HDMI 6',
            'HDMI 7': 'HDMI 7',
            'HDMI 8': 'HDMI 8',
            'Coax 1': 'Coax 1',
            'Coax 2': 'Coax 2',
            'Coax 3': 'Coax 3',
            'Coax 4': 'Coax 4',
            'Optical 1': 'Optical 1',
            'Optical 2': 'Optical 2',
            'Optical 3': 'Optical 3',
            'Optical 4': 'Optical 4',
            'ARC': 'ARC',
            'USB stream': 'USB',
            'Tuner 1': 'Tuner',
            'Analog 1': 'Analog 1',
            'Analog 2': 'Analog 2',
            'Analog 3': 'Analog 3',
            'Analog 4': 'Analog 4',
            'Analog 5': 'Analog 5',
            'Analog 7.1': 'Analog 7.1',
            'Front': 'Front'
        }

        self.WriteStatus('Zone1Input', States[match.group(1).decode()], None)

    def SetZone1Power(self, value, qualifier):

        States = {
            'On': 'power_on',
            'Off': 'power_off'
        }

        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><{0} value="0" ack="no" /></emotivaControl>'.format(States[value])
        self.__SetHelper('Zone1Power', Cmdstring, value, qualifier)

    def UpdateZone1Power(self, value, qualifier):

        CmdString = '<?xml version="1.0" encoding="utf-8"?><emotivaUpdate><power /></emotivaUpdate>'

        self.__UpdateHelper('Zone1Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        Command = match.group(1).decode()
        value = match.group(2).decode()

        if Command == 'power':

            self.WriteStatus('Zone1Power', value, None)

        elif Command == 'zone2_power':
            self.WriteStatus('Zone2Power', value, None)

    def UpdateSubscribePower(self, value, qualifier):
        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaSubscription><power /></emotivaSubscription>'
        self.__UpdateHelper('SubscribePower', Cmdstring, value, qualifier)

    def SetZone1Volume(self, value, qualifier):

        if -96 <= value <= 11:
            Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><set_volume value="{0}" ack="no" /></emotivaControl>'.format(value)
            self.__SetHelper('Zone1Volume', Cmdstring, value, qualifier)
        else:
            print('Invalid Command for SetZone1Volume')

    def UpdateZone1Volume(self, value, qualifier):
        CmdString = '<?xml version="1.0" encoding="utf-8"?><emotivaSubscription><volume /></emotivaSubscription>'
        self.__UpdateHelper('Zone1Volume', CmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        if match.group(1).decode() == 'volume':
            self.WriteStatus('Zone1Volume', int(match.group(2).decode()), None)
        elif match.group(1).decode() == 'zone2_volume':
            self.WriteStatus('Zone2Volume', int(match.group(2).decode()), None)

    def SetZone2Mute(self, value, qualifier):

        States = {
            'On': 'zone2_mute_on',
            'Off': 'zone2_mute_off'
        }

        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><{0} value="0" ack="no" /></emotivaControl>'.format(States[value])
        self.__SetHelper('Zone2Mute', Cmdstring, value, qualifier)

    def SetZone2Input(self, value, qualifier):

        States = {
            'Analog 1': 'zone2_analog1',
            'Analog 2': 'zone2_analog2',
            'Analog 3': 'zone2_analog3',
            'Analog 4': 'zone2_analog4',
            'Analog 5': 'zone2_analog5',
            'Analog 7.1': 'zone2_analog71',
            'Analog 8': 'zone2_analog8',
            'Front': 'zone2_front_in',
            'ARC': 'zone2_ARC',
            'Ethernet': 'zone2_ethernet',
            'Follow Main': 'zone2_follow_main',
            'Coax 1': 'zone2_coax1',
            'Coax 2': 'zone2_coax2',
            'Coax 3': 'zone2_coax3',
            'Coax 4': 'zone2_coax4',
            'Optical 1': 'zone2_optical1',
            'Optical 2': 'zone2_optical2',
            'Optical 3': 'zone2_optical3',
            'Optical 4': 'zone2_optical4'
        }

        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><{0} value="0" ack="no" /></emotivaControl>'.format(States[value])
        self.__SetHelper('Zone2Input', Cmdstring, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):
        CmdString = '<?xml version="1.0" encoding="utf-8"?><emotivaSubscription><source /></emotivaSubscription>'
        self.__UpdateHelper('Zone2Input', CmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        States = {
            'Analog 1': 'Analog 1',
            'Analog 2': 'Analog 2',
            'Analog 3': 'Analog 3',
            'Analog 4': 'Analog 4',
            'Analog 5': 'Analog 5',
            'Analog 7.1': 'Analog 7.1',
            'Analog 8': 'Analog 8',
            'Front': 'Front',
            'ARC': 'ARC',
            'Ethernet': 'Ethernet',
            'Follow Main': 'Follow Main',
            'Coax 1': 'Coax 1',
            'Coax 2': 'Coax 2',
            'Coax 3': 'Coax 3',
            'Coax 4': 'Coax 4',
            'Optical 1': 'Optical 1',
            'Optical 2': 'Optical 2',
            'Optical 3': 'Optical 3',
            'Optical 4': 'Optical 4'
        }

        self.WriteStatus('Zone2Input', States[match.group(1).decode()], None)

    def SetZone2Power(self, value, qualifier):

        States = {
            'On': 'zone2_power_on',
            'Off': 'zone2_power_off'
        }

        Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><{0} value="0" ack="no" /></emotivaControl>'.format(States[value])
        self.__SetHelper('Zone2Power', Cmdstring, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):
        CmdString = '<?xml version="1.0" encoding="utf-8"?><emotivaSubscription><zone2_power /></emotivaSubscription>'
        self.__UpdateHelper('Zone2Power', CmdString, value, qualifier)

    def SetZone2Volume(self, value, qualifier):

        if -96 <= value <= 11:
            Cmdstring = '<?xml version="1.0" encoding="utf-8"?><emotivaControl><zone2_set_volume value="{0}" ack="no" /></emotivaControl>'.format(value)
            self.__SetHelper('Zone2Volume', Cmdstring, value, qualifier)
        else:
            print('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):
        CmdString = '<?xml version="1.0" encoding="utf-8"?><emotivaSubscription><zone2_volume /></emotivaSubscription>'
        self.__UpdateHelper('Zone2Volume', CmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)          

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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

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


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
