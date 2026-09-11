from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
from extronlib.system import ProgramLog
import re

from struct import pack


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'NumberPad': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStep': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.regex1 = re.compile(
                b'(\x70(\x00|\x01|\x02|\x03|\x04)\x03\x01(\x01|\x00)[\x00-\xFF])')
            self.regex2 = re.compile(
                b'(\x70(\x00|\x01|\x02|\x03|\x04)(\x02|\x03)(\x01|\x02|\x03|\x04|\x05){1,2}[\x00-\xFF])')
            self.regex3 = re.compile(
                b'(\x70(\x00|\x01|\x02|\x03|\x04)\x02(\x01|\x00)[\x00-\xFF])')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom': b'\x00\xD4',
            'Full': b'\x01\xD5',
            'Zoom': b'\x02\xD6',
            'Full 1': b'\x06\xDA',
            'Full 2': b'\x07\xDB'
        }
        temp = self.ReadStatus('Input', None)
        if temp:
            if temp == 'PC' and value in ['Full 1', 'Full 2', 'Normal']:
                if value == 'Normal':
                    AspectRatioCmdString = b'\x8C\x00\x44\x03\x01\x05\xD9'
                else:
                    AspectRatioCmdString = b''.join([b'\x8C\x00\x44\x03\x01', ValueStateValues[value]])
            elif temp == 'Video' and value in ['Wide Zoom', 'Full', 'Zoom', 'Normal']:
                if value == 'Normal':
                    AspectRatioCmdString = b'\x8C\x00\x44\x03\x01\x03\xD7'
                else:
                    AspectRatioCmdString = b''.join([b'\x8C\x00\x44\x03\x01', ValueStateValues[value]])
            else:
                AspectRatioCmdString = None
            if AspectRatioCmdString:
                self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x97',
            'Off': b'\x00\x96'
        }

        AudioMuteCmdString = b''.join([b'\x8C\x00\x06\x03\x01', ValueStateValues[value]])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off',
        }

        AudioMuteCmdString = b'\x83\x00\x06\xFF\xFF\x87'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x10\x07',
            'Down': b'\x11\x08'
        }

        ChannelCmdString = b''.join([b'\x8C\x00\x67\x03\x01', ValueStateValues[value]])
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': b'\x02\x01\x91',
            'HDMI 1': b'\x03\x04\x01\x96',
            'HDMI 2': b'\x03\x04\x02\x97',
            'HDMI 3': b'\x03\x04\x03\x98',
            'HDMI 4': b'\x03\x04\x04\x99',
            'Video': b'\x03\x02\x01\x94',
            'Component': b'\x03\x03\x01\x95',
            'PC': b'\x03\x05\x01\x97'
        }

        InputCmdString = b''.join([b'\x8C\x00\x02', ValueStateValues[value]])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Video',
            0x03: 'Component',
            0x05: 'PC'
        }

        HDMIstates = {
            0x01: 'HDMI 1',
            0x02: 'HDMI 2',
            0x03: 'HDMI 3',
            0x04: 'HDMI 4',
        }

        InputCmdString = b'\x83\x00\x02\xFF\xFF\x83'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[2] == 0x02 and res[3] == 0x01:
                    self.WriteStatus('Input', 'TV', qualifier)
                elif res[2] == 0x03:
                    if res[3] == 0x04:
                        self.WriteStatus('Input', HDMIstates[res[4]], qualifier)
                    else:
                        self.WriteStatus('Input', ValueStateValues[res[3]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left': b'\x01\x34\x2B',
            'Right': b'\x01\x33\x2A',
            'Up': b'\x01\x74\x6B',
            'Down': b'\x01\x75\x6C',
            'Home': b'\x01\x60\x57',
            'OK': b'\x01\x65\x5C',
            'Return': b'\x97\x23\xB0'
        }

        MenuNavigationCmdString = b''.join([b'\x8C\x00\x67\x03', ValueStateValues[value]])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetNumberPad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x01\x09\x00',
            '1': b'\x01\x00\xF7',
            '2': b'\x01\x01\xF8',
            '3': b'\x01\x02\xF9',
            '4': b'\x01\x03\xFA',
            '5': b'\x01\x04\xFB',
            '6': b'\x01\x05\xFC',
            '7': b'\x01\x06\xFD',
            '8': b'\x01\x07\xFE',
            '9': b'\x01\x08\xFF',
            'Dot': b'\x97\x1D\xAA'
        }

        NumberPadCmdString = b''.join([b'\x8C\x00\x67\x03', ValueStateValues[value]])
        self.__SetHelper('NumberPad', NumberPadCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x8F',
            'Off': b'\x00\x8E'
        }

        PowerCmdString = b''.join([b'\x8C\x00\x00\x02', ValueStateValues[value]])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

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
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x00\x9D',
            'Off': b'\x01\x9E'
        }

        VideoMuteCmdString = b''.join([b'\x8C\x00\x0D\x03\x01', ValueStateValues[value]])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CRC = value + 149
            VolumeCmdString = pack('BBBBBBB', 0x8C, 0x00, 0x05, 0x03, 0x01, value, CRC)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x00\x94',
            'Down': b'\x01\x95'
        }

        VolumeStepCmdString = b''.join([b'\x8C\x00\x05\x03\x00', ValueStateValues[value]])
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x01: "Limit Over (Over max value).",
            0x02: "Limit Over (Under min value).",
            0x03: "Command Cancelled.",
            0x04: "Parse Error."
        }

        temp = response[1]
        if temp in DEVICE_ERROR_CODES:
            print("Unrecognized Command {0} and error is {1}".format(
                sourceCmdName, DEVICE_ERROR_CODES[response[1]]))
            return b''
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if command == 'AudioMute':
            regex = self.regex1
        elif command == 'Power':
            regex = self.regex3
        elif command == 'Input':
            regex = self.regex2

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress,
                                                     self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(
                self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("""
{0} module received a request from the device for a {1}, but device{1} was not provided.
Please provide a device{1} and attempt again.
Ex: dvInterface.device{1} = '{1}'
Please review the communication sheet.
{2}
""".format(__name__, credential_type, port_info), 'warning')

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback,
                                                'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(
                        result.group(0), b'')
                else:
                    break
        return True

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


class DeviceEthernetClass:

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'NumberPad': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '\x2ASCAMUT000000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = '\x2ASEAMUT################\x0A'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[22:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': '3',
            'Down': '4'
        }

        ChannelCmdString = '\x2ASCIRCC000000000000003{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'SCART': '2',
            'Composite': '3',
            'Component': '4',
            'PC': '6'
        }

        HDMIStateValues = {
            'HDMI 1': '1',
            'HDMI 2': '2',
            'HDMI 3': '3',
            'HDMI 4': '4'
            }

        if value in ['HDMI 1', 'HDMI 2', 'HDMI 3', 'HDMI 4']:
            InputCmdString = '\x2ASCINPT000000010000000{0}\x0A'.format(HDMIStateValues[value])
        elif value == 'TV':
            InputCmdString = '\x2ASCINPT0000000000000000\x0A'
        else:
            InputCmdString = '\x2ASCINPT0000000{0}00000001\x0A'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'TV',
            '2': 'SCART',
            '3': 'Composite',
            '4': 'Component',
            '6': 'PC'
        }
        HDMIStateValues = {
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDMI 3',
            '4': 'HDMI 4'
        }

        InputCmdString = '\x2ASEINPT################\x0A'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                temp = res[14:15]
                if temp == '1':
                    self.WriteStatus('Input', HDMIStateValues[res[22:-1]], qualifier)
                else:
                    self.WriteStatus('Input', ValueStateValues[temp], qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left': '12',
            'Right': '11',
            'Up': '09',
            'Down': '10',
            'Home': '06',
            'OK': '13',
            'Return': '08'
        }

        MenuNavigationCmdString = '\x2ASCIRCC00000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetNumberPad(self, value, qualifier):

        ValueStateValues = {
            '1': '18',
            '2': '19',
            '3': '20',
            '4': '21',
            '5': '22',
            '6': '23',
            '7': '24',
            '8': '25',
            '9': '26',
            '0': '27',
            '11': '28',
            '12': '29',
            'Dot': '38'
        }

        NumberPadCmdString = '\x2ASCIRCC00000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('NumberPad', NumberPadCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PIPModeCmdString = '\x2ASCPIPI000000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PIPModeCmdString = '\x2ASEPIPI################\x0A'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[22:-1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIPMode')

    def SetPIPPosition(self, value, qualifier):

        PIPPositionCmdString = '\x2ASETPPP################\x0A'
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '\x2ASCPOWR000000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '\x2ASEPOWR################\x0A'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[22:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = '\x2ASCPMUT000000000000000{0}\x0A'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = '\x2ASEPMUT################\x0A'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[22:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '\x2ASCVOLU0000000000000{0:03d}\x0A'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x2ASEVOLU################\x0A'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[20:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[7] == 'F':
            print('{0} {1}'.format(sourceCmdName, 'has an error.'))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x0A')
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x0A')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("""
{0} module received a request from the device for a {1}, but device{1} was not provided.
Please provide a device{1} and attempt again.
Ex: dvInterface.device{1} = '{1}'
Please review the communication sheet.
{2}
""".format(__name__, credential_type, port_info), 'warning')

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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
