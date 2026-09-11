from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re


class DeviceClass:
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
        self.devicePassword = 'RGB'
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Window'], 'Status': {}},
            'AutoSync': {'Parameters': ['Input Type', 'Input'], 'Status': {}},
            'Freeze': {'Parameters': ['Window'], 'Status': {}},
            'FullScreen': {'Parameters': ['Window'], 'Status': {}},
            'Ping': {'Status': {}},
            'WindowEnable': {'Parameters': ['Window'], 'Status': {}},
            'WindowPresetRecall': {'Parameters': ['Fade Time'], 'Status': {}},
            'WindowPresetSave': {'Status': {}},
            'WindowWallPosition': {'Parameters': ['Window'], 'Status': {}},
        }       

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'normal',
            '1.66:1': 'ws1',
            '1.78:1': 'ws2',
            '1.85:1': 'ws3',
            '2.35:1': 'ws4'
        }
        window = qualifier['Window']
        if 1 <= int(window) <= 4:
            AspectRatioCmdString = 'ar {0} {1}\r'.format(window, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAutoSync(self, value, qualifier):

        InputTypeStates = {
            'DVI': 'dvi',
            'RGB': 'rgb',
            'YPbPr': 'ypbpr',
            'Composite': 'comp',
            'S-Video': 'svid',
            'Component': 'cmpn'
        }

        InputStates = {
            'All': 'all',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }
        Input = qualifier['Input']
        Type = qualifier['Input Type']
        if (Input in InputStates) and (Type in InputTypeStates):
            AutoSyncCmdString = 'inas {0} {1} {2}\r'.format(InputTypeStates[Type], InputStates[Input], ValueStateValues[value])
            self.__SetHelper('AutoSync', AutoSyncCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSync')

    def SetFreeze(self, value, qualifier):

        WindowStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            'All': 'all'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }
        window = qualifier['Window']
        if window in WindowStates:
            FreezeCmdString = 'frz {0} {1}\r'.format(WindowStates[window], ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def SetFullScreen(self, value, qualifier):

        WindowStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        window = qualifier['Window']
        if 1 <= int(window) <= 4:
            FullScreenCmdString = 'fs {0}\r'.format(window)
            self.__SetHelper('FullScreen', FullScreenCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFullScreen')

    def UpdatePing(self, value, qualifier):

        PingCmdString = 'stat\r'
        res = self.__UpdateHelper('Ping', PingCmdString, value, qualifier)

    def SetWindowEnable(self, value, qualifier):

        WindowStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            'All': 'all'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }
        window = qualifier['Window']
        if window in WindowStates:
            WindowEnableCmdString = 'winen {0} {1}\r'.format(window, ValueStateValues[value])
            self.__SetHelper('WindowEnable', WindowEnableCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowEnable')

    def SetWindowPresetRecall(self, value, qualifier):

        time = qualifier['Fade Time']
        if (0 <= time <= 128) and (1 <= int(value) <= 50):
            if time == 0:
                WindowPresetRecallCmdString = 'wpload {0}\r'.format(value)
            else:
                WindowPresetRecallCmdString = 'wpload {0} {1}\r'.format(value, time)
            self.__SetHelper('WindowPresetRecall', WindowPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPresetRecall')

    def SetWindowPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 50:
            WindowPresetSaveCmdString = 'wpsave {0}\r'.format(value)
            self.__SetHelper('WindowPresetSave', WindowPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPresetSave')

    def SetWindowWallPosition(self, value, qualifier):

        ValueStateValues = {
            'Up': 'i',
            'Left': 'j',
            'Down': 'm',
            'Right': 'l',
            'Stop': 'q'
        }
        window = qualifier['Window']
        if 1 <= int(window) <= 4:
            WindowWallPositionCmdString = 'pos {0} {1}\r'.format(window, ValueStateValues[value])
            self.__SetHelper('WindowWallPosition', WindowWallPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowWallPosition') 
            
    def __CheckResponseForErrors(self, sourceCmdName, response):

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'>')
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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
