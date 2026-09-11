from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re


class DeviceSerialClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'XBR-65X905A': self.sony_10_1267_AB,
            'XBR-65X900A': self.sony_10_1267_AB,
            'XBR-65X850B': self.sony_10_1267_AB,
            'XBR-65X850C': self.sony_10_1267_C,
            'XBR-75X850C': self.sony_10_1267_C,
            'XBR-43X830C': self.sony_10_1267_C,
            'XBR-55X850D': self.sony_10_1267_D,
            'XBR-65X850D': self.sony_10_1267_D,
            'XBR-75X850D': self.sony_10_1267_D,
            'XBR-85X850D': self.sony_10_1267_D,
            'XBR-75X940D': self.sony_10_1267_D,
            'XBR-65X930D': self.sony_10_1267_D,
            'XBR-55X930D': self.sony_10_1267_D,
            'XBR-55X850C': self.sony_10_1267_C,
            'XBR-49X900E': self.sony_10_1267_D,
            'XBR-55X900E': self.sony_10_1267_D,
            'XBR-65X850E': self.sony_10_1267_D,
            'XBR-65X900E': self.sony_10_1267_D,
            'XBR-75X850E': self.sony_10_1267_D,
            'XBR-75X900E': self.sony_10_1267_D,
        }

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
            'IREmulation': {'Status': {}},
            'Power': {'Status': {}},
            'Standby': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.UpdateDelim = {
            'Input': b'(^\x70(\x00|\x01|\x02|\x03|\x04)(\x02|\x03)(\x01|\x02|\x03|\x04|\x05){1,2}[\x00-\xFF]$)',
            'Power': b'(^\x70(\x00|\x01|\x02|\x03|\x04)\x02(\x01|\x00)[\x00-\xFF]$)',
            'Volume': b'(^\x70(\x00|\x01|\x02|\x03|\x04)\x03\x01[\x00-\xFF]{2}$)'
        }

        self.CompiledRegex = {k: re.compile(v) for k, v in self.UpdateDelim.items()}

    def CalCRC(self, Data):
        Crc = 0
        for i in range(0, len(Data)):
            if type(Data[i]) is int:
                Crc += Data[i]
            else:
                Crc += ord(Data[i])
        return Crc & 0xFF

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 0x03,
            'Wide Zoom': 0x00,
            'Full': 0x01,
            'Zoom': 0x02
        }
        if value != 'Toggle':
            Data = [0x8C, 0x00, 0x44, 0x03, 0x01, ValueStateValues[value]]
            AspectRatioCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        else:
            AspectRatioCmdString = b'\x8C\x00\x44\x02\x00\xD2'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00,
        }
        if value != 'Toggle':
            Data = [0x8C, 0x00, 0x06, 0x03, 0x01, ValueStateValues[value]]
            AudioMuteCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        else:
            AudioMuteCmdString = b'\x8C\x00\x06\x02\x00\x94'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x00,
            'Down': 0x01
        }

        Data = [0x8C, 0x00, 0x04, 0x03, 0x00, ValueStateValues[value]]
        ChannelCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetChannelDiscreteCommand(self, value, qualifier):

        TunerStates = {
            'Terr Digital': b'\x01',
            'Terr Analoue': b'\x02',
            'CATV': b'\x03',
            'BS Digital': b'\x04',
            'CS Digital': b'\x05',
            'DVB-S': b'\x06',
            'DVB-S2': b'\x07',
            'Cable Analog': b'\x0A',
            'Cable Digital': b'\x0B'
        }

        Data = [b'\x8C', b'\x00', b'\x04', b'\x0D', b'\x01', TunerStates[qualifier['Tuner']]]
        cmdstring = value
        if cmdstring:
            cmdstring = cmdstring.replace('.', ',')
            for x in range(0, 10):
                if x < len(cmdstring):
                    if cmdstring[x] == ',':
                        cmdbyte = b'\x2C'
                    else:
                        cmdbyte = bytes.fromhex(cmdstring[x].zfill(2))
                else:
                    cmdbyte = b'\xFF'
                Data.append(cmdbyte)

            ChannelDiscreteCommandCmdString = b''.join(pack('B', ord(x)) for x in Data) + pack('B', self.CalCRC(Data))
            self.__SetHelper('ChannelDiscreteCommand', ChannelDiscreteCommandCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00,
        }
        if value != 'Toggle':
            Data = [0x8C, 0x00, 0x10, 0x03, 0x01, ValueStateValues[value]]
            ClosedCaptionCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        else:
            ClosedCaptionCmdString = b'\x8C\x00\x10\x02\x00\x9E'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetClosedCaptionAnalog(self, value, qualifier):

        ValueStateValues = {
            'CC1': 0x01,
            'CC2': 0x02,
            'CC3': 0x03,
            'CC4': 0x04,
            'Text1': 0x05,
            'Text2': 0x06,
            'Text3': 0x07,
            'Text4': 0x08
        }

        Data = [0x8C, 0x00, 0x10, 0x04, 0x02, 0x00, ValueStateValues[value]]
        ClosedCaptionAnalogCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('ClosedCaptionAnalog', ClosedCaptionAnalogCmdString, value, qualifier)

    def SetClosedCaptionDigital(self, value, qualifier):

        ValueStateValues = {
            'CC1': 0x07,
            'CC2': 0x08,
            'CC3': 0x09,
            'CC4': 0x0a,
            'Service1': 0x01,
            'Service2': 0x02,
            'Service3': 0x03,
            'Service4': 0x04,
            'Service5': 0x05,
            'Service6': 0x06
        }

        Data = [0x8C, 0x00, 0x10, 0x04, 0x02, 0x01, ValueStateValues[value]]
        ClosedCaptionDigitalCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('ClosedCaptionDigital', ClosedCaptionDigitalCmdString, value, qualifier)

    def SetInput(self, value, qualifier):
        if value != 'Toggle':
            if value == 'TV':
                InputCmdString = b'\x8C\x00\x02\x02\x01\x91'
            elif value == 'PC':
                InputCmdString = b'\x8C\x00\x02\x03\x05\x01\x97'
            else:
                Data = [0x8C, 0x00, 0x02, 0x03, self.inputStates[value][0], self.inputStates[value][1]]
                InputCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        else:
            InputCmdString = b'\x8C\x00\x02\x02\x00\x90'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x01: 'HDMI 1',
            0x02: 'HDMI 2',
            0x03: 'HDMI 3',
            0x04: 'HDMI 4',
        }

        Data = [0x83, 0x00, 0x02, 0xFF, 0xFF]
        InputCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[2] == 0x02 and res[3] == 0x01:
                    self.WriteStatus('Input', 'TV', qualifier)
                elif res[2] == 0x03 and res[3] == 0x05:
                    self.WriteStatus('Input', 'PC', qualifier)
                elif res[2] == 0x03 and res[3] == 0x02:
                    if res[4] == 0x01:
                        if 'Video' in self.inputStates:
                            self.WriteStatus('Input', 'Video', qualifier)
                        else:
                            self.WriteStatus('Input', 'Video 1', qualifier)
                    elif res[4] == 0x02:
                        self.WriteStatus('Input', 'Video 2', qualifier)
                elif res[2] == 0x03 and res[3] == 0x03:
                    if res[4] == 0x01:
                        if 'Component' in self.inputStates:
                            self.WriteStatus('Input', 'Component', qualifier)
                        else:
                            self.WriteStatus('Input', 'Component 1', qualifier)
                    elif res[4] == 0x02:
                        self.WriteStatus('Input', 'Component 2', qualifier)
                elif res[2] == 0x03 and res[3] == 0x04:
                    value = ValueStateValues[res[4]]
                    self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetIREmulation(self, value, qualifier):

        ValueStateValues = {
            'Input': b'\x01\x25\x1C',
            'Power': b'\x01\x15\x0C',
            'Wide Mode': b'\xA4\x3D\xD7',
            'dot': b'\x97\x1D\xAA',
            'Display': b'\x01\x3A\x31',
            'Return': b'\x97\x23\xB0',
            'Options': b'\x97\x36\xC3',
            'Home': b'\x01\x60\x57',
            'Up': b'\x01\x74\x6B',
            'Down': b'\x01\x75\x6C',
            'Left': b'\x01\x34\x2B',
            'Right': b'\x01\x33\x2A',
            'Select': b'\x01\x65\x5C',
            '1': b'\x01\x00\xF7',
            '2': b'\x01\x01\xF8',
            '3': b'\x01\x02\xF9',
            '4': b'\x01\x03\xFA',
            '5': b'\x01\x04\xFB',
            '6': b'\x01\x05\xFC',
            '7': b'\x01\x06\xFD',
            '8': b'\x01\x07\xFE',
            '9': b'\x01\x08\xFF',
            '0': b'\x01\x09\x00',
            'Closed Caption': b'\xA4\x10\x01',
            'Volume Up': b'\x01\x12\x02',
            'Volume Down': b'\x01\x13\x03',
            'Muting': b'\x01\x14\x04',
            'Ch/Prog Up': b'\x01\x10\x07',
            'Ch/Prog Down': b'\x01\x11\x08',
            'Jump': b'\x01\x3B\x32'
        }

        IREmulationCmdString = b''.join([b'\x8C\x00\x67\x03', ValueStateValues[value]])
        self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        Data = [0x8C, 0x00, 0x00, 0x02, ValueStateValues[value]]
        PowerCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Power', PowerCmdString, value, qualifier)  # Protocol has note about waiting for 20 seconds

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        Data = [0x83, 0x00, 0x00, 0xFF, 0xFF]
        PowerCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetStandby(self, value, qualifier):

        ValueStateValues = {
            'Enable': 0x01,
            'Disable': 0x00
        }

        Data = [0x8C, 0x00, 0x01, 0x02, ValueStateValues[value]]
        StandbyCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Standby', StandbyCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x00,
            'Off': 0x01,
        }
        if value != 'Toggle':
            Data = [0x8C, 0x00, 0x0D, 0x03, 0x01, ValueStateValues[value]]
            VideoMuteCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        else:
            VideoMuteCmdString = b'\x8C\x00\x0D\x02\x00\x9B'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Data = [0x8C, 0x00, 0x05, 0x03, 0x01, value]
            VolumeCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        Data = [0x83, 0x00, 0x05, 0xFF, 0xFF]
        VolumeCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x01: "Limit Over (Over max value).",
            0x02: "Limit Over (Under min value).",
            0x03: "Command Cancelled.",
            0x04: "Parse Error."
        }
        if response[1] in DEVICE_ERROR_CODES:
            self.Error(["Unrecognized Command {0} and error is {1}".format(sourceCmdName, DEVICE_ERROR_CODES[response[1]])])
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
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        regex = self.CompiledRegex[command]
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

    def sony_10_1267_AB(self):
        self.inputStates = {
            'Video 1': (0x02, 0x01),
            'Video 2': (0x02, 0x02),
            'Component 1': (0x03, 0x01),
            'Component 2': (0x03, 0x02),
            'HDMI 1': (0x04, 0x01),
            'HDMI 2': (0x04, 0x02),
            'HDMI 3': (0x04, 0x03),
            'HDMI 4': (0x04, 0x04),
        }

    def sony_10_1267_C(self):
        self.inputStates = {
            'Component': (0x03, 0x01),
            'HDMI 1': (0x04, 0x01),
            'HDMI 2': (0x04, 0x02),
            'HDMI 3': (0x04, 0x03),
            'HDMI 4': (0x04, 0x04),
            'Video': (0x02, 0x01)
        }

    def sony_10_1267_D(self):
        self.inputStates = {
            'Component': (0x03, 0x01),
            'HDMI 1': (0x04, 0x01),
            'HDMI 2': (0x04, 0x02),
            'HDMI 3': (0x04, 0x03),
            'HDMI 4': (0x04, 0x04),
            'Video 1': (0x02, 0x01),
            'Video 2': (0x02, 0x02)
        }

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
        self.Debug = False
        self.Models = {
            'XBR-43X830C': self.sony_10_1267_C,
            'XBR-55X850C': self.sony_10_1267_C,
            'XBR-55X850D': self.sony_10_1267_D,
            'XBR-55X930D': self.sony_10_1267_D,
            'XBR-65X850B': self.sony_10_1267_AB,
            'XBR-65X850C': self.sony_10_1267_C,
            'XBR-65X850D': self.sony_10_1267_D,
            'XBR-65X900A': self.sony_10_1267_AB,
            'XBR-65X905A': self.sony_10_1267_AB,
            'XBR-65X930D': self.sony_10_1267_D,
            'XBR-75X850C': self.sony_10_1267_C,
            'XBR-75X850D': self.sony_10_1267_D,
            'XBR-75X940D': self.sony_10_1267_D,
            'XBR-85X850D': self.sony_10_1267_D,
            'XBR-49X900E': self.sony_10_1267_D,
            'XBR-55X900E': self.sony_10_1267_D,
            'XBR-65X850E': self.sony_10_1267_D,
            'XBR-65X900E': self.sony_10_1267_D,
            'XBR-75X850E': self.sony_10_1267_D,
            'XBR-75X900E': self.sony_10_1267_D,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'IREmulation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*SAAMUT0{15}(0|1)\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*SAINPT0{7}([0-6])0{7}([0-4])\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*SAPOWR0{15}(0|1)\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*SAPMUT0{15}(0|1)\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*SAVOLU0{13}([0-1][0-9]{2})\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\*SA(AMUT|INPT|PMUT|POWR|VOLU)(F|N){16}\n'), self.__MatchError, None)

        self.deliTagValues = {
            'AudioMute': b'*SNAMUT',
            'Input': b'*SNINPT',
            'Power': b'*SNPOWR',
            'VideoMute': b'*SNPMUT',
            'Volume': b'*SAVOLU'
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'1',
            'Off': b'0'
        }

        AudioMuteCmdString = b''.join([b'*SC', 'AMUT'.ljust(19, '0').encode(), ValueStateValues[value], b'\n'])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b''.join([b'*SE', 'AMUT'.ljust(20, '#').encode(), b'\n'])
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'33',
            'Down': b'34'
        }

        ChannelCmdString = b''.join([b'*SC', 'IRCC'.ljust(18, '0').encode(), ValueStateValues[value], b'\n'])
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = b''.join([b'*SC', 'INPT'.ljust(11, '0').encode(), self.setState[value][0].ljust(8, '0').encode(), self.setState[value][1], b'\n'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b''.join([b'*SE', 'INPT'.ljust(20, '#').encode(), b'\n'])
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'TV',
            '4': 'Component',
            '5': 'Screen Mirroring',
            '6': 'PC'
        }

        inputMatch = match.group(1).decode()

        if inputMatch == '1':
            value = 'HDMI {0}'.format(match.group(2).decode())
        elif inputMatch == '3':
            value = 'Video {0}'.format(match.group(2).decode())
        else:
            value = ValueStateValues[inputMatch]

        self.WriteStatus('Input', value, None)

    def SetIREmulation(self, value, qualifier):

        ValueStateValues = {
            'Power Off': b'00',
            'Input': b'01',
            'GGuide': b'02',
            'EPG': b'03',
            'Favorites': b'04',
            'Display': b'05',
            'Home': b'06',
            'Options': b'07',
            'Return': b'08',
            'Up': b'09',
            'Down': b'10',
            'Right': b'11',
            'Left': b'12',
            'Confirm': b'13',
            'Red': b'14',
            'Green': b'15',
            'Yellow': b'16',
            'Blue': b'17',
            '1': b'18',
            '2': b'19',
            '3': b'20',
            '4': b'21',
            '5': b'22',
            '6': b'23',
            '7': b'24',
            '8': b'25',
            '9': b'26',
            '0': b'27',
            '11': b'28',
            '12': b'29',
            'Volume Up': b'30',
            'Volume Down': b'31',
            'Mute': b'32',
            'Channel Up': b'33',
            'Channel Down': b'34',
            'Subtitle': b'35',
            'Closed Caption': b'36',
            'Enter': b'37',
            'DOT': b'38',
            'Analog': b'39',
            'Teletext': b'40',
            'Exit': b'41',
            'Analog 2': b'42',
            'AD': b'43',
            'Digital': b'44',
            'Analog?': b'45',
            'BS': b'46',
            'CS': b'47',
            'BS/CS': b'48',
            'Ddata': b'49',
            'Picture Off': b'50',
            'TV Radio': b'51',
            'Theater': b'52',
            'SEN': b'53',
            'Internet Widgets': b'54',
            'Internet Video': b'55',
            'Netflix': b'56',
            'Scene Select': b'57',
            'Mode3D': b'58',
            'iManual': b'59',
            'Audio': b'60',
            'Wide': b'61',
            'Jump': b'62',
            'PAP': b'63',
            'MyEPG': b'64',
            'Program Description': b'65',
            'Write Chapter': b'66',
            'TrackID': b'67',
            'Ten Key': b'68',
            'AppliCast': b'69',
            'acTVila': b'70',
            'Delete Video': b'71',
            'Photo Frame': b'72',
            'TV Pause': b'73',
            'Keypad': b'74',
            'Media': b'75',
            'Sync Menu': b'76',
            'Forward': b'77',
            'Play': b'78',
            'Rewind': b'79',
            'Previous': b'80',
            'Stop': b'81',
            'Next': b'82',
            'Record': b'83',
            'Pause': b'84',
            'Eject': b'85',
            'Flash Plus': b'86',
            'Flash Minus': b'87',
            'Top Menu': b'88',
            'Popup Menu': b'89',
            'Rakuraku Start': b'90',
            'One Touch Time Record': b'91',
            'One Touch View': b'92',
            'One Touch Record': b'93',
            'One Touch Stop': b'94',
            'DUX': b'95',
            'Football Mode': b'96',
            'Social': b'97'
        }

        IREmulationCmdString = b''.join([b'*SC', 'IRCC'.ljust(18, '0').encode(), ValueStateValues[value], b'\n'])
        self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'1',
            'Off': b'0'
        }

        PowerCmdString = b''.join([b'*SC', 'POWR'.ljust(19, '0').encode(), ValueStateValues[value], b'\n'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b''.join([b'*SE', 'POWR'.ljust(20, '#').encode(), b'\n'])
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteCmdString = b''.join([b'*SC', 'PMUT'.ljust(19, '0').encode(), b'1', b'\n'])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b''.join([b'*SE', 'PMUT'.ljust(20, '#').encode(), b'\n'])
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b''.join([b'*SC', 'VOLU'.ljust(17, '0').encode(), str(value).zfill(3).encode(), b'\n'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b''.join([b'*SE', 'VOLU'.ljust(20, '#').encode(), b'\n'])
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command not in self.deliTagValues:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, 3.2, deliTag=self.deliTagValues[command])
            if not res:
                self.Error(['Invalid/unexpected response'])

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

        CommandValues = {
            'AMUT': 'Audio Mute',
            'INPT': 'Input',
            'POWR': 'Power',
            'PMUT': 'Video Mute',
            'VOLU': 'Volume'
        }
        value = match.group(1).decode()
        errorValue = match.group(2).decode()

        if errorValue[0] == 'F':
            errorString = 'Error: {0}'.format(CommandValues[value])
        elif errorValue[0] == 'N':
            errorString = 'Not Found: {0}'.format(CommandValues[value])
        else:
            errorString = 'Unknown Error.'

        self.Error([errorString])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def sony_10_1267_AB(self):
        self.setState = {
            'TV': ['0', b'0'],
            'HDMI 1': ['1', b'1'],
            'HDMI 2': ['1', b'2'],
            'HDMI 3': ['1', b'3'],
            'HDMI 4': ['1', b'4'],
            'Video 1': ['3', b'1'],
            'Video 2': ['3', b'2'],
            'Component 1': ['4', b'1'],
            'Component 2': ['4', b'2'],
            'Screen Mirroring': ['5', b'1'],
            'PC': ['6', b'1']
        }

    def sony_10_1267_C(self):
        self.setState = {
            'TV': ['0', b'0'],
            'HDMI 1': ['1', b'1'],
            'HDMI 2': ['1', b'2'],
            'HDMI 3': ['1', b'3'],
            'HDMI 4': ['1', b'4'],
            'Video 1': ['3', b'1'],
            'Component': ['4', b'1'],
            'Screen Mirroring': ['5', b'1'],
            'PC': ['6', b'1']
        }

    def sony_10_1267_D(self):
        self.setState = {
            'TV': ['0', b'0'],
            'HDMI 1': ['1', b'1'],
            'HDMI 2': ['1', b'2'],
            'HDMI 3': ['1', b'3'],
            'HDMI 4': ['1', b'4'],
            'Video 1': ['3', b'1'],
            'Video 2': ['3', b'2'],
            'Component': ['4', b'1'],
            'Screen Mirroring': ['5', b'1'],
            'PC': ['6', b'1']
        }

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
