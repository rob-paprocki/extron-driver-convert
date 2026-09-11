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
        self._DeviceID = '001'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MultiWindowMode': {'Status': {}},
            'Mute': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            'Window': {'Parameters': ['Input'], 'Status': {}},
            'WindowMode': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'[0-9]{3}SRC=(1|2|3|4|5|6|7)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'[0-9]{3}WMT=(0|1|2)'), self.__MatchMultiWindowMode, None)
            self.AddMatchString(re.compile(b'[0-9]{3}MUT=(0|1)'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'[0-9]{3}PMT=(0|1|2)'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'[0-9]{3}W(1|2|3|4)S=(0|1|2|3|4|5|6)'), self.__MatchWindow, None)
            self.AddMatchString(re.compile(b'[0-9]{3}WIN=(1|2|3|4)'), self.__MatchWindowMode, None)
            self.VolRex = re.compile(b'[0-9]{3}VOL=[0-9]{3}')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 'ALL'
        elif 0 <= int(value) <= 99:
            self._DeviceID = '{0:03d}'.format(int(value))
        else:
            self.Error(['DeviceID should be a value between 0 - 99 or Broadcast.'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'K:{0}ATU.'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': 'SPC',
            'DisplayPort': 'SH1',
            'HDMI 1': 'SH2',
            'HDMI 2': 'SH3',
            'HDMI 3': 'SH4',
            'HDMI 4': 'SH5',
            'OPS/HDMI': 'SH6',
            'OPS/DP': 'SH7'
        }

        InputCmdString = 'K:{0}{1}.'.format(self._DeviceID, InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'K:{0}SRC?'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            '1': 'DisplayPort',
            '2': 'HDMI 1',
            '3': 'HDMI 2',
            '4': 'HDMI 3',
            '5': 'HDMI 4',
            '6': 'OPS/HDMI',
            '7': 'OPS/DP'
        }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': 'RUP',
            'Down': 'RDN',
            'Left': 'RLT',
            'Right': 'RRT',
            'Select': 'REN',
            'Menu': 'RMN'
        }

        MenuNavigationCmdString = 'K:{0}{1}.'.format(self._DeviceID, MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMultiWindowMode(self, value, qualifier):

        MultiWindowModeState = {
            'Off': 'WM0',
            'PBP': 'WM1',
            'Quadrant': 'WM2'
        }

        MultiWindowModeCmdString = 'K:{0}{1}.'.format(self._DeviceID, MultiWindowModeState[value])
        self.__SetHelper('MultiWindowMode', MultiWindowModeCmdString, value, qualifier)

    def UpdateMultiWindowMode(self, value, qualifier):

        MultiWindowModeCmdString = 'K:{0}WMT?'.format(self._DeviceID)
        self.__UpdateHelper('MultiWindowMode', MultiWindowModeCmdString, value, qualifier)

    def __MatchMultiWindowMode(self, match, tag):

        MultiWindowModeState = {
            '0': 'Off',
            '1': 'PBP',
            '2': 'Quadrant'
        }

        value = MultiWindowModeState[match.group(1).decode()]
        self.WriteStatus('MultiWindowMode', value, None)

    def SetMute(self, value, qualifier):

        MuteState = {
            'On': 'MON',
            'Off': 'MOF'
        }

        MuteCmdString = 'K:{0}{1}.'.format(self._DeviceID, MuteState[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'K:{0}MUT?'.format(self._DeviceID)
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        MuteState = {
            '1': 'On',
            '0': 'Off'
        }

        value = MuteState[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPictureMode(self, value, qualifier):

        PictureModeState = {
            'Standard': 'PM0',
            'Dynamic': 'PM1',
            'User': 'PM2'
        }

        PictureModeCmdString = 'K:{0}{1}.'.format(self._DeviceID, PictureModeState[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = 'K:{0}PMT?'.format(self._DeviceID)
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        PictureModeState = {
            '0': 'Standard',
            '1': 'Dynamic',
            '2': 'User'
        }

        value = PictureModeState[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = 'K:{0}{1}.'.format(self._DeviceID, PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= int(value) <= 100:
            VolumeCmdString = 'K:{0}{1}VOL.'.format(self._DeviceID, int(value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'K:{0}VOL?'.format(self._DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            if res[7] == '0' and res[8] != '0':
                value = res[8:10]
            elif res[7:10] == '100':
                value = res[7:10]
            else:
                value = res[7]
            try:
                self.WriteStatus('Volume', int(value), qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/Unexpected Response'])

    def SetWindow(self, value, qualifier):

        WindowState = {
            'DisplayPort': '0',
            'HDMI 1': '1',
            'HDMI 2': '2',
            'HDMI 3': '3',
            'HDMI 4': '4',
            'OPS/HDMI': '5',
            'OPS/DP': '6'
        }

        InputValue = qualifier['Input']
        WindowCmdString = 'K:{0}W{1}{2}.'.format(self._DeviceID, InputValue, WindowState[value])
        self.__SetHelper('Window', WindowCmdString, value, qualifier)

    def UpdateWindow(self, value, qualifier):

        InputValue = qualifier['Input']
        WindowCmdString = 'K:{0}W{1}S?'.format(self._DeviceID, InputValue)
        self.__UpdateHelper('Window', WindowCmdString, value, qualifier)

    def __MatchWindow(self, match, tag):

        WindowState = {
            '0': 'DisplayPort',
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDMI 3',
            '4': 'HDMI 4',
            '5': 'OPS/HDMI',
            '6': 'OPS/DP'
        }

        value = WindowState[match.group(2).decode()]
        self.WriteStatus('Window', value, {'Input': match.group(1).decode()})

    def SetWindowMode(self, value, qualifier):

        WindowModeState = {
            '1': 'WN1',
            '2': 'WN2',
            '3': 'WN3',
            '4': 'WN4'
        }

        WindowModeCmdString = 'K:{0}{1}.'.format(self._DeviceID, WindowModeState[value])
        self.__SetHelper('WindowMode', WindowModeCmdString, value, qualifier)

    def UpdateWindowMode(self, value, qualifier):

        WindowModeCmdString = 'K:{0}WIN?'.format(self._DeviceID)
        self.__UpdateHelper('WindowMode', WindowModeCmdString, value, qualifier)

    def __MatchWindowMode(self, match, tag):

        WindowModeState = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        value = WindowModeState[match.group(1).decode()]
        self.WriteStatus('WindowMode', value, None)

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
        if command == 'Volume':
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.VolRex)
            return res
        else:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
