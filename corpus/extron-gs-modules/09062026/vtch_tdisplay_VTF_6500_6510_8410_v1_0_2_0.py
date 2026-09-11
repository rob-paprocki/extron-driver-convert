from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
        self.Models = {
            'VTF-6510': self.vtch_39_2044_6510_8410,
            'VTF-8410': self.vtch_39_2044_6510_8410,
            'VTF-6500': self.vtch_39_2044_6500,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPAdjust': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07\x01\x00ASP([\x00-\x03])\x08'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00MUT(\x00|\x01)\x08'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00KLC(\x00|\x01)\x08'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00MIN(\x00|\x12|\x11|\x09|\x0A|\x0B|\x0C|\x0D|\x0E)\x08'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00PIN(\x00|\x12|\x11|\x09|\x0A|\x0B|\x0C|\x0D|\x0E)\x08'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00SCM([\x00-\x04])\x08'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00PSC([\x00-\x07])\x08'), self.__MatchPIPAdjust, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00PPO([\x00-\x03])\x08'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00POW(\x00|\x01)\x08'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00VOL([\x00-\x64])\x08'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Native': b'\x00',
            'Full Screen': b'\x01',
            'Pillarbox/4:3': b'\x02',
            'Letterbox': b'\x03'
        }

        AspectRatioCmdString = b''.join([b'\x07\x01\x02ASP', ValueStateValues[value], b'\x08'])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x07\x01\x01ASP\x08'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x00': 'Native',
            '\x01': 'Full Screen',
            '\x02': 'Pillarbox/4:3',
            '\x03': 'Letterbox'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        AudioMuteCmdString = b''.join([b'\x07\x01\x02MUT', ValueStateValues[value], b'\x08'])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x07\x01\x01MUT\x08'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x07\x01\x02ADJ\x00\x08'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        ExecutiveModeCmdString = b''.join([b'\x07\x01\x02KLC', ValueStateValues[value], b'\x08'])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = b'\x07\x01\x01KLC\x08'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = b''.join([b'\x07\x01\x02MIN', self.InputValues[value], b'\x08'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x07\x01\x01MIN\x08'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputStates[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left': b'\x04',
            'Right': b'\x05',
            'Up': b'\x02',
            'Down': b'\x03',
            'Menu': b'\x00',
            'Enter': b'\x06',
            'Exit': b'\x07',
            'Info': b'\x01'
        }

        MenuNavigationCmdString = b''.join([b'\x07\x01\x02RCU', ValueStateValues[value], b'\x08'])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Cinema': b'\x03',
            'Sport': b'\x01',
            'Vivid': b'\x04',
            'User': b'\x00',
            'Game': b'\x02'
        }

        PictureModeCmdString = b''.join([b'\x07\x01\x02SCM', ValueStateValues[value], b'\x08'])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\x07\x01\x01SCM\x08'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '\x03': 'Cinema',
            '\x01': 'Sport',
            '\x04': 'Vivid',
            '\x00': 'User',
            '\x02': 'Game'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPIPAdjust(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x00',
            'Small': b'\x01',
            'Medium': b'\x02',
            'Large': b'\x03',
            'Side By Side': b'\x04',
            '3 Windows': b'\x06',
            '4 Windows': b'\x07'
        }

        PIPAdjustCmdString = b''.join([b'\x07\x01\x02PSC', ValueStateValues[value], b'\x08'])
        self.__SetHelper('PIPAdjust', PIPAdjustCmdString, value, qualifier)

    def UpdatePIPAdjust(self, value, qualifier):

        PIPAdjustCmdString = b'\x07\x01\x01PSC\x08'
        self.__UpdateHelper('PIPAdjust', PIPAdjustCmdString, value, qualifier)

    def __MatchPIPAdjust(self, match, tag):

        ValueStateValues = {
            '\x00': 'Off',
            '\x01': 'Small',
            '\x02': 'Medium',
            '\x03': 'Large',
            '\x04': 'Side By Side',
            '\x06': '3 Windows',
            '\x07': '4 Windows'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPAdjust', value, None)

    def SetPIPInput(self, value, qualifier):

        PIPInputCmdString = b''.join([b'\x07\x01\x02PIN', self.InputValues[value], b'\x08'])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = b'\x07\x01\x01PIN\x08'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        value = self.InputStates[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Bottom-Left': b'\x00',
            'Bottom-Right': b'\x01',
            'Top-Left': b'\x02',
            'Top-Right': b'\x03'
        }

        PIPPositionCmdString = b''.join([b'\x07\x01\x02PPO', ValueStateValues[value], b'\x08'])
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = b'\x07\x01\x01PPO\x08'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            '\x00': 'Bottom-Left',
            '\x01': 'Bottom-Right',
            '\x02': 'Top-Left',
            '\x03': 'Top-Right'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = b'\x07\x01\x02SWA\x00\x08'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        PowerCmdString = b''.join([b'\x07\x01\x02POW', ValueStateValues[value], b'\x08'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x07\x01\x01POW\x08'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\x07\x01\x02RCU\x2B\x08'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b''.join([b'\x07\x01\x02VOL', value.to_bytes(1, 'big'), b'\x08'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x07\x01\x01VOL\x08'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
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

    def vtch_39_2044_6510_8410(self):
        self.InputValues = {
            'VGA': b'\x00',
            'HDMI 1': b'\x09',
            'HDMI 2': b'\x0A',
            'HDMI 3': b'\x0B',
            'HDMI 4': b'\x0C',
            'HDMI 5': b'\x11',
            'Display Port': b'\x0D',
            'IPC/OPS': b'\x0E',
            'Media Player': b'\x12'
        }
        self.InputStates = {
            '\x00': 'VGA',
            '\x09': 'HDMI 1',
            '\x0A': 'HDMI 2',
            '\x0B': 'HDMI 3',
            '\x0C': 'HDMI 4',
            '\x11': 'HDMI 5',
            '\x0D': 'Display Port',
            '\x0E': 'IPC/OPS',
            '\x12': 'Media Player'
        }

    def vtch_39_2044_6500(self):

        self.InputValues = {
            'VGA': b'\x00',
            'HDMI 1': b'\x09',
            'HDMI 2': b'\x0A',
            'Display Port': b'\x0D',
            'IPC/OPS': b'\x0E',
            'Media Player': b'\x12'
        }
        self.InputStates = {
            '\x00': 'VGA',
            '\x09': 'HDMI 1',
            '\x0A': 'HDMI 2',
            '\x0D': 'Display Port',
            '\x0E': 'IPC/OPS',
            '\x12': 'Media Player'
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
