from extronlib.interface import EthernetClientInterface
from struct import pack
import re
import math
from extronlib.system import Wait, ProgramLog
from binascii import unhexlify

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
        self.__deviceUsername = None
        self.__devicePassword = None
        self.__MACAddress = ''
        self.Models = {
            'nXp752': self.ashl_25_2915_2,
            'nXp754': self.ashl_25_2915_4,
            'nXp1502': self.ashl_25_2915_2,
            'nXp1504': self.ashl_25_2915_4,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'InputVolume': {'Parameters': ['Channel'], 'Status': {}},
            'OutputVolume': {'Parameters': ['Channel'], 'Status': {}},
            'PowerStatus': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
        }

        self.SetHeader = b'\xAA\xAA\xAA\xAA'
        self.RequestHeader = b'\x8F\x8F\x8F\x8F'

        if self.Unidirectional == 'False':

            self.AddMatchString(re.compile(b'[\x8F]{4}[\x00-\xFF]{6}\x01[\x00-\xFF][\x00]{2}\x02\x03\x01([\x00-\x07])(\x00|\x01)\xFF'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'[\x8F]{4}[\x00-\xFF]{6}\x01[\x00-\xFF][\x00]{2}\x02\x03\x00([\x00-\x07])(\x00|\x01)\xFF'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'[\x8F]{4}[\x00-\xFF]{6}\x01[\x00-\xFF][\x00]{2}\x81\x06\x01([\x00-\x07])\x17([\x00-\xFF])([\x00-\xFF])[\x00-\x01]\xFF'), self.__MatchInputVolume, None)
            self.AddMatchString(re.compile(b'[\x8F]{4}[\x00-\xFF]{6}\x01[\x00-\xFF][\x00]{2}\x06\x01([\x00-\x01])\xFF'), self.__MatchPowerStatus, None)
            self.AddMatchString(re.compile(b'[\x8F]{4}[\x00-\xFF]{6}\x01[\x00-\xFF][\x00]{2}\x81\x06\x00([\x00-\x07])\x17([\x00-\xFF])([\x00-\xFF])[\x00-\x01]\xFF'), self.__MatchOutputVolume, None)

    @property
    def MACAddress(self):
        return self.__MACAddress

    @MACAddress.setter
    def MACAddress(self, value):
        res = re.search('([a-fA-F0-9]{2}-?){6}', value)
        self.__MACAddress = b''
        temp_list = res.group().split('-')
        for mc in temp_list:
            self.__MACAddress += unhexlify(mc)

    @property
    def deviceUsername(self):
        return self.__deviceUsername

    @deviceUsername.setter
    def deviceUsername(self, value):
        self.__deviceUsername = b''
        for user in value.ljust(8, '\x00'):
            self.__deviceUsername += pack('B', ord(user))

    @property
    def devicePassword(self):
        return self.__devicePassword

    @devicePassword.setter
    def devicePassword(self, value):
        self.__devicePassword = b''
        for user in value.ljust(8, '\x00'):
            self.__devicePassword += pack('B', ord(user))

    def SetInputMute(self, value, qualifier):

        MuteValues = {
            'Off': 0x00,
            'On': 0x01
        }

        ch_value = int(qualifier['Channel']) - 1
        if 0 <= ch_value <= self.InputMax:

            CmdString = self.SetHeader + self.__MACAddress + self.__deviceUsername + self.__devicePassword + b'\x00\x00\x00\x00' + pack('>6B', 0x02, 0x03, 0x01, ch_value, MuteValues[value], 0xFF)

            self.__SetHelper('InputMute', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        ch_value = int(qualifier['Channel']) - 1

        if 0 <= ch_value <= self.InputMax:

            CmdString = self.RequestHeader + self.__MACAddress + b'\x00\x00\x00\x00' + pack('>5B', 0x02, 0x02, 0x01, ch_value, 0xFF)
            self.__UpdateHelper('InputMute', CmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, qualifier):

        Mute_States = {
            '\x00': 'Off',
            '\x01': 'On',
        }

        inp_ch = ord(match.group(1).decode()) + 1
        if 1 <= inp_ch <= self.InputMax + 1:
            inp_ch = str(inp_ch)
            value = Mute_States[match.group(2).decode()]
            self.WriteStatus('InputMute', value, {'Channel': inp_ch})
        else:
            print('Invalid Command')

    def SetOutputMute(self, value, qualifier):

        MuteValues = {
            'Off': 0x00,
            'On': 0x01
        }

        ch_value = int(qualifier['Channel']) - 1

        if 0 <= ch_value <= self.OutputMax:

            CmdString = self.SetHeader + self.__MACAddress + self.__deviceUsername + self.__devicePassword + b'\x00\x00\x00\x00' + pack('>6B', 0x02, 0x03, 0x00, ch_value, MuteValues[value], 0xFF)

            self.__SetHelper('OutputMute', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        ch_value = int(qualifier['Channel']) - 1
        if 0 <= ch_value <= self.OutputMax:

            CmdString = self.RequestHeader + self.__MACAddress + b'\x00\x00\x00\x00' + pack('>5B', 0x02, 0x02, 0x00, ch_value, 0xFF)
            self.__UpdateHelper('OutputMute', CmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, qualifier):

        Mute_States = {
            '\x00': 'Off',
            '\x01': 'On',
        }

        out_ch = ord(match.group(1).decode()) + 1
        if 1 <= out_ch <= self.OutputMax + 1:
            out_ch = str(out_ch)
            value = Mute_States[match.group(2).decode()]
            self.WriteStatus('OutputMute', value, {'Channel': out_ch})
        else:
            print('Invalid Command')

    def SetInputVolume(self, value, qualifier):

        ch_value = int(qualifier['Channel']) - 1

        if 0 <= ch_value <= self.InputMax:
            if -50 <= value <= 12:
                vol_gain_word = (value * 10) + 8192
                vol_first_byte = round(vol_gain_word / 256)
                vol_second_byte = vol_gain_word & 127

                CmdString = self.SetHeader + self.__MACAddress + self.__deviceUsername + self.__devicePassword + b'\x00\x00\x00\x00' + pack('>9B', 0x81, 0x06, 0x01, ch_value, 0x17, vol_first_byte, vol_second_byte, 0x00, 0xFF)

                self.__SetHelper('InputVolume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputVolume')

    def UpdateInputVolume(self, value, qualifier):

        ch_value = int(qualifier['Channel']) - 1

        if 0 <= ch_value <= self.InputMax:

            CmdString = self.RequestHeader + self.__MACAddress + b'\x00\x00\x00\x00' + pack('>6B', 0x81, 0x03, 0x01, ch_value, 0x17, 0xFF)
            self.__UpdateHelper('InputVolume', CmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateInputVolume')

    def __MatchInputVolume(self, match, qualifier):

        inp_ch = ord(match.group(1).decode()) + 1
        if 1 <= inp_ch <= self.InputMax + 1:
            inp_ch = str(inp_ch)

            temp_val1 = ord(match.group(2).decode())
            temp_val2 = ord(match.group(3).decode())

            value = (((temp_val1 * 256) + temp_val2) - 8192) / 10
            self.WriteStatus('InputVolume', round(value), {'Channel': inp_ch})
        else:
            print('Invalid Command')

    def SetOutputVolume(self, value, qualifier):

        ch_value = int(qualifier['Channel']) - 1

        if 0 <= ch_value <= self.OutputMax:
            if -50 <= value <= 12:
                vol_gain_word = (value * 10) + 8192
                vol_first_byte = round(vol_gain_word / 256)
                vol_second_byte = vol_gain_word & 127

                CmdString = self.SetHeader + self.__MACAddress + self.__deviceUsername + self.__devicePassword + b'\x00\x00\x00\x00' + pack('>9B', 0x81, 0x06, 0x00, ch_value, 0x17, vol_first_byte, vol_second_byte, 0x00, 0xFF)

                self.__SetHelper('OutputVolume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        ch_value = int(qualifier['Channel']) - 1

        if 0 <= ch_value <= self.OutputMax:

            CmdString = self.RequestHeader + self.__MACAddress + b'\x00\x00\x00\x00' + pack('>6B', 0x81, 0x03, 0x00, ch_value, 0x17, 0xFF)
            self.__UpdateHelper('OutputVolume', CmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateOutputVolume')

    def __MatchOutputVolume(self, match, qualifier):

        out_ch = ord(match.group(1).decode()) + 1

        if 1 <= out_ch <= self.OutputMax + 1:
            out_ch = str(out_ch)

            temp_val1 = ord(match.group(2).decode())
            temp_val2 = ord(match.group(3).decode())

            value = (((temp_val1 * 256) + temp_val2) - 8192) / 10
            self.WriteStatus('OutputVolume', round(value), {'Channel': out_ch})
        else:
            print('Invalid Command')

    def UpdatePowerStatus(self, value, qualifier):

        CmdString = self.RequestHeader + self.__MACAddress + b'\x00\x00\x00\x00' + pack('>3B', 0x06, 0x00, 0xFF)
        self.__UpdateHelper('PowerStatus', CmdString, value, qualifier)

    def __MatchPowerStatus(self, match, tag):

        ValueStateValues = {
            0: 'On',
            1: 'Standby'
        }

        value = ValueStateValues[ord(match.group(1).decode())]
        self.WriteStatus('PowerStatus', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 35:
            preset_recall = int(value) - 1

            CmdString = self.SetHeader + self.__MACAddress + self.__deviceUsername + self.__devicePassword + b'\x00\x00\x00\x00' + pack('>5B', 0x32, 0x02, preset_recall, 0x00, 0xFF)
            self.__SetHelper('PresetRecall', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 35:
            preset_save = int(value) - 1

            CmdString = self.SetHeader + self.__MACAddress + self.__deviceUsername + self.__devicePassword + b'\x00\x00\x00\x00' + pack('>5B', 0x31, 0x02, preset_save, 0x00, 0xFF)
            self.__SetHelper('PresetSave', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetSave')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.__deviceUsername is None:
            self.MissingCredentialsLog('Username')
        elif self.__devicePassword is None:
            self.MissingCredentialsLog('Password')
        else:
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

            if self.__deviceUsername is None:
                self.MissingCredentialsLog('Username')
            elif self.__devicePassword is None:
                self.MissingCredentialsLog('Password')
            else:
                self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def ashl_25_2915_2(self):
        self.OutputMax = 1
        self.InputMax = 1

    def ashl_25_2915_4(self):
        self.OutputMax = 3
        self.InputMax = 3

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')

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
