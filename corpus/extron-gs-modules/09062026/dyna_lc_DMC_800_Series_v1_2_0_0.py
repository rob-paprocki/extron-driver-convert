from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack


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
            'AreaOff': {'Parameters': ['Fade Time'], 'Status': {}},
            'ChannelLevelStatus': {'Parameters': ['Area', 'Channel'], 'Status': {}},
            'ClassicPreset': {'Parameters': ['Area', 'Fade Time'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Area'], 'Status': {}},
            'FadeArea': {'Parameters': ['Area', 'Fade Time'], 'Status': {}},
            'FadeChannel': {'Parameters': ['Area', 'Channel Offset', 'Fade Time'], 'Status': {}},
            'LinearChannel': {'Parameters': ['Area', 'Channel', 'Fade Time'], 'Status': {}},
            'LinearPreset': {'Parameters': ['Area', 'Fade Time'], 'Status': {}},
            'Panic': {'Parameters': ['Area', 'Fade Time'], 'Status': {}},
            'PresetStatus': {'Parameters': ['Area'], 'Status': {}},
            'ProgramtoCurrentPreset': {'Parameters': ['Area'], 'Status': {}},
            'RecallSavedPreset': {'Parameters': ['Area', 'Fade Time'], 'Status': {}},
            'ResetPreset': {'Parameters': ['Area', 'Fade Time'], 'Status': {}},
            'SaveCurrentPreset': {'Parameters': ['Area'], 'Status': {}},
            'StopFade': {'Parameters': ['Area', 'Channel'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x1c([\x00-\xFF])([\x00-\xFF])\x60[\x00-\xFF]([\x00-\xFF])\xFF[\x00-\xFF]'), self.__MatchChannelLevelStatus, None)
            self.AddMatchString(re.compile(b'\x1c([\x00-\xFF])([\x00-\x20])\x62\x00\x00\xFF[\x00-\xFF]'), self.__MatchPresetStatus, None)

    def SetAreaOff(self, value, qualifier):

        if value == 'All':
            area = 0
        elif 1 <= int(value) <= 255:
            area = int(value)
        else:
            area = 'Missing'
        if 0 <= qualifier['Fade Time'] <= 1310:
            fade = qualifier['Fade Time'] * 50
            fade_low = fade & 0xFF
            fade_high = fade >> 8
        else:
            fade = 'Missing'

        if 'Missing' not in [area, fade]:
            chksum = 0x1c + area + fade_low + 0x04 + fade_high + 0x00 + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, fade_low, 0x04, fade_high, 0x00, 0xFF, chksum)
            self.__SetHelper('AreaOff', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAreaOff')

    def UpdateChannelLevelStatus(self, value, qualifier):
        if 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'
        if 1 <= int(qualifier['Channel']) <= 255:
            channel = int(qualifier['Channel']) - 1  # channel origin is 0
        else:
            channel = 'Missing'

        if 'Missing' not in [area, channel]:
            chksum = 0x1c + area + channel + 0x61 + 0x00 + 0x00 + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, channel, 0x61, 0x00, 0x00, 0xFF, chksum)
            self.__UpdateHelper('ChannelLevelStatus', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelLevelStatus')

    def __MatchChannelLevelStatus(self, match, tag):
        area = str(match.group(1)[0])
        channel = str(match.group(2)[0] + 1)
        current_level = match.group(3)[0]
        if current_level == 255:
            current_level = 0
        elif current_level == 128:
            current_level = 50
        elif current_level == 1:
            current_level = 100
        else:
            current_level = 255 - current_level
            current_level *= 101
            current_level /= 255
        value = round(current_level)

        self.WriteStatus('ChannelLevelStatus', value, {'Area': area, 'Channel': channel})

    def SetClassicPreset(self, value, qualifier):

        PresetStates = {
            '1': (0x00, 0x00),
            '2': (0x01, 0x00),
            '3': (0x02, 0x00),
            '4': (0x03, 0x00),
            '5': (0x0a, 0x00),
            '6': (0x0b, 0x00),
            '7': (0x0c, 0x00),
            '8': (0x0d, 0x00),
            '9': (0x00, 0x01),
            '10': (0x01, 0x01),
            '11': (0x02, 0x01),
            '12': (0x03, 0x01),
            '13': (0x0a, 0x01),
            '14': (0x0b, 0x01),
            '15': (0x0c, 0x01),
            '16': (0x0d, 0x01),
            '17': (0x00, 0x02),
            '18': (0x01, 0x02),
            '19': (0x02, 0x02),
            '20': (0x03, 0x02),
            '21': (0x0a, 0x02),
            '22': (0x0b, 0x02),
            '23': (0x0c, 0x02),
            '24': (0x0d, 0x02),
            '25': (0x00, 0x03),
            '26': (0x01, 0x03),
            '27': (0x02, 0x03),
            '28': (0x03, 0x03),
            '29': (0x0a, 0x03),
            '30': (0x0b, 0x03),
            '31': (0x0c, 0x03),
            '32': (0x0d, 0x03)
        }
        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'
        if 0 <= qualifier['Fade Time'] <= 1310:
            fade = qualifier['Fade Time'] * 50
            fade_low = fade & 0xFF
            fade_high = fade >> 8
        else:
            fade = 'Missing'
        if 1 <= int(value) <= 32:
            preset = value
            OpCode = PresetStates[value][0]
            Bank = PresetStates[value][1]
        else:
            preset = 'Missing'

        if 'Missing' not in [area, fade, preset]:
            chksum = 0x1c + area + fade_low + OpCode + fade_high + Bank + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, fade_low, OpCode, fade_high, Bank, 0xFF, chksum)
            self.__SetHelper('ClassicPreset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClassicPreset')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x15,
            'Off': 0x16
        }
        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'

        if 'Missing' not in [area]:
            chksum = 0x1c + area + ValueStateValues[value] + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, 0x00, ValueStateValues[value], 0x00, 0x00, 0xFF, chksum)
            self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def SetFadeArea(self, value, qualifier):

        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'
        if 0 <= qualifier['Fade Time'] <= 1310:
            fade = qualifier['Fade Time'] * 50
            fade_low = fade & 0xFF
            fade_high = fade >> 8
        else:
            fade = 'Missing'
        if 0 <= value <= 100:
            lvl = value
            if lvl == 0:
                lvl_to_fade = 0xFF
            elif lvl == 100:
                lvl_to_fade = 0x01
            else:
                lvl_to_fade = int(hex(round((255 - ((255 * lvl) / 101)) + 1)), 16)
        else:
            lvl = 'Missing'

        if 'Missing' not in [area, fade, lvl]:
            chksum = 0x1c + area + pack('>H', lvl_to_fade)[1] + 0x79 + fade_low + fade_high + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, pack('>H', lvl_to_fade)[1], 0x79, fade_low, fade_high, 0xFF, chksum)
            self.__SetHelper('FadeArea', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFadeArea')

    def SetFadeChannel(self, value, qualifier):

        ChannelOffsetStates = {
            '1': (0x80, 0xFF),
            '2': (0x81, 0xFF),
            '3': (0x82, 0xFF),
            '4': (0x83, 0xFF),
            '5': (0x80, 0x00),
            '6': (0x81, 0x00),
            '7': (0x82, 0x00),
            '8': (0x83, 0x00),
            '9': (0x80, 0x01),
            '10': (0x81, 0x01),
            '11': (0x82, 0x01),
            '12': (0x83, 0x01),
            '13': (0x80, 0x02),
            '14': (0x81, 0x02),
            '15': (0x82, 0x02),
            '16': (0x83, 0x02),
        }
        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'
        if 1 <= int(qualifier['Channel Offset']) <= 16:
            ch_offset = qualifier['Channel Offset']
            OpCode = ChannelOffsetStates[ch_offset][0]
            Offset = ChannelOffsetStates[ch_offset][1]
        else:
            ch_offset = 'Missing'
        if 0 <= qualifier['Fade Time'] <= 5:
            fade = qualifier['Fade Time'] * 50
        else:
            fade = 'Missing'
        if 0 <= value <= 100:
            lvl = value
            if lvl == 0:
                lvl_to_fade = 0xFF
            elif lvl == 100:
                lvl_to_fade = 0x01
            else:
                lvl_to_fade = int(hex(round((255 - ((255 * lvl) / 101)) + 1)), 16)
        else:
            lvl = 'Missing'

        if 'Missing' not in [area, ch_offset, fade, lvl]:
            chksum = 0x1c + area + pack('>H', lvl_to_fade)[1] + OpCode + Offset + fade + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, pack('>H', lvl_to_fade)[1], OpCode, Offset, fade, 0xFF, chksum)
            self.__SetHelper('FadeChannel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFadeChannel')

    def SetLinearChannel(self, value, qualifier):

        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'
        if qualifier['Channel'] == 'All':
            channel = 0xFF  # All
        elif 1 <= int(qualifier['Channel']) <= 255:
            channel = int(qualifier['Channel']) - 1  # channel origin is 0
        else:
            channel = 'Missing'
        if 0 <= qualifier['Fade Time'] <= 195:
            OpCode = 0x72
            fade = qualifier['Fade Time']
        else:
            fade = 'Missing'
        if 0 <= value <= 100:
            lvl = value
            if lvl == 0:
                lvl_to_fade = 0xFF
            elif lvl == 100:
                lvl_to_fade = 0x01
            else:
                lvl_to_fade = int(hex(round((255 - ((255 * lvl) / 101)) + 1)), 16)
        else:
            lvl = 'Missing'

        if 'Missing' not in [area, channel, fade, lvl]:
            chksum = 0x1c + area + channel + OpCode + lvl_to_fade + fade + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, channel, OpCode, lvl_to_fade, fade, 0xFF, chksum)
            self.__SetHelper('LinearChannel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLinearChannel')

    def SetLinearPreset(self, value, qualifier):

        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'
        if 0 <= qualifier['Fade Time'] <= 1310:
            fade = qualifier['Fade Time'] * 50
            fade_low = fade & 0xFF
            fade_high = fade >> 8
        else:
            fade = 'Missing'
        if 1 <= int(value) <= 170:
            preset = int(value) - 1
        else:
            preset = 'Missing'

        if 'Missing' not in [area, fade, preset]:
            chksum = 0x1c + area + preset + 0x65 + fade_low + fade_high + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, preset, 0x65, fade_low, fade_high, 0xFF, chksum)
            self.__SetHelper('LinearPreset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLinearPreset')

    def SetPanic(self, value, qualifier):

        ValueStateValues = {
            'On': 0x17,
            'Off': 0x18
        }
        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'
        if 0 <= qualifier['Fade Time'] <= 1310:
            fade = qualifier['Fade Time'] * 50
            fade_low = fade & 0xFF
            fade_high = fade >> 8
        else:
            fade = 'Missing'

        if 'Missing' not in [area, fade]:
            chksum = 0x1c + area + fade_low + ValueStateValues[value] + fade_high + 0x00 + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, fade_low, ValueStateValues[value], fade_high, 0x00, 0xFF, chksum)
            self.__SetHelper('Panic', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanic')

    def UpdatePresetStatus(self, value, qualifier):

        if 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'

        if 'Missing' not in [area]:
            chksum = 0x1c + area + 0x63 + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, 0x00, 0x63, 0x00, 0x00, 0xFF, chksum)
            self.__UpdateHelper('PresetStatus', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresetStatus')

    def __MatchPresetStatus(self, match, tag):
        area = str(match.group(1)[0])
        value = str(match.group(2)[0] + 1)
        self.WriteStatus('PresetStatus', value, {'Area': area})

    def SetProgramtoCurrentPreset(self, value, qualifier):

        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'

        if 'Missing' not in [area]:
            chksum = 0x1c + area + 0x08 + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, 0x00, 0x08, 0x00, 0x00, 0xFF, chksum)
            self.__SetHelper('ProgramtoCurrentPreset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProgramtoCurrentPreset')

    def SetRecallSavedPreset(self, value, qualifier):

        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'
        if 0 <= qualifier['Fade Time'] <= 25:
            fade = qualifier['Fade Time'] * 10
        else:
            fade = 'Missing'

        if 'Missing' not in [area, fade]:
            chksum = 0x1c + area + 0x67 + fade + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, 0x00, 0x67, 0x00, fade, 0xFF, chksum)
            self.__SetHelper('RecallSavedPreset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallSavedPreset')

    def SetResetPreset(self, value, qualifier):

        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'
        if 0 <= qualifier['Fade Time'] <= 1310:
            fade = qualifier['Fade Time'] * 50
            fade_low = fade & 0xFF
            fade_high = fade >> 8
        else:
            fade = 'Missing'

        if 'Missing' not in [area, fade]:
            chksum = 0x1c + area + fade_low + 0x0F + fade_high + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, fade_low, 0x0F, fade_high, 0x00, 0xFF, chksum)
            self.__SetHelper('ResetPreset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResetPreset')

    def SetSaveCurrentPreset(self, value, qualifier):

        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'

        if 'Missing' not in [area]:
            chksum = 0x1c + area + 0x66 + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, 0x00, 0x66, 0x00, 0x00, 0xFF, chksum)
            self.__SetHelper('SaveCurrentPreset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaveCurrentPreset')

    def SetStopFade(self, value, qualifier):

        if qualifier['Area'] == 'All':
            area = 0
        elif 1 <= int(qualifier['Area']) <= 255:
            area = int(qualifier['Area'])
        else:
            area = 'Missing'
        if qualifier['Channel'] == 'All':
            channel = 0xFF  # All
        elif 1 <= int(qualifier['Channel']) <= 255:
            channel = int(qualifier['Channel']) - 1  # channel origin is 0
        else:
            channel = 'Missing'

        if 'Missing' not in [area, channel]:
            chksum = 0x1c + area + channel + 0x76 + 0xFF
            chksum = ((chksum ^ 0xFFFF) + 1) & 0xFF
            CmdString = pack('>8B', 0x1c, area, channel, 0x76, 0x00, 0x00, 0xFF, chksum)
            self.__SetHelper('StopFade', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStopFade')

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS485', Model=None):
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
