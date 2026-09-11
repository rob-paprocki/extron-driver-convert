from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self._deviceUsername = 'su'
        self._devicePassword = 'supass'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CloudClean': { 'Status': {}},
            'DisplayStatus': {'Parameters': ['User'], 'Status': {}},
            'DoNotDisturb': {'Parameters': ['User'], 'Status': {}},
            'IPAddress': { 'Status': {}},
            'Kickoff': {'Parameters': ['User'], 'Status': {}},
            'PresentationMode': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'RestartApacheServer': { 'Status': {}},
            'RoomCode': { 'Status': {}},
            'Screenshare': { 'Status': {}},
            'Volume': { 'Status': {}},
            'WakeUp': { 'Status': {}},
            'WifiGuestMode': { 'Status': {}},
        }

        self.authenticated = False
        self.commandhead = '<P><UN>{0}</UN><Pwd>{1}</Pwd>'.format(self._deviceUsername, self._devicePassword)
        self.commandbody = '<Cmd>{0}</Cmd><P1>{1}</P1><P2>{2}</P2><P3>{3}</P3>'
        self.commandtail = '<P4></P4><P5></P5><P6></P6><P7></P7><P8></P8><P9></P9><P10></P10></P>'
        self.command = self.commandhead + self.commandbody + self.commandtail

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Login Successful\.\nNow Please send a command'), self.__MatchLoginSuccess, None)
            self.AddMatchString(re.compile(b'Error(1[1234])'), self.__MatchLoginFail, None)

        self.update_delirex = {
            'DisplayStatus':    re.compile(b'DisplayStatus\|Get\|(?:Not ?Presenting|Presenting|Waiting|UsrNotExist)\r'),
            'IPAddress':        re.compile(b'IP:.*?\|'),
            'PresentationMode': re.compile(b'PrsMode\|Get\|[01]\r'),
            'RoomCode':         re.compile(b'(?:Error21|RCode\|Get\|Code\|\d+\r)'),
            'Volume':           re.compile(b'Vol\|Get\|\d+\r'),
            'WifiGuestMode':    re.compile(b'WifiGuestMode\|Status\|[01]\r'),
        }

    @property
    def deviceUsername(self):
        return self._deviceUsername

    @deviceUsername.setter
    def deviceUsername(self, value):
        self._deviceUsername = value
        self.commandhead = '<P><UN>{0}</UN><Pwd>{1}</Pwd>'.format(self._deviceUsername, self._devicePassword)

    @property
    def devicePassword(self):
        return self._devicePassword

    @devicePassword.setter
    def devicePassword(self, value):
        self._devicePassword = value
        self.commandhead = '<P><UN>{0}</UN><Pwd>{1}</Pwd>'.format(self._deviceUsername, self._devicePassword)

    def __MatchLoginSuccess(self, match, tag):

        self.authenticated = True
        self.command = '<P><UN>{0}</UN><Pwd></Pwd>'.format(self._deviceUsername) + self.commandbody + self.commandtail

    def __MatchLoginFail(self, match, qualifier):

        self.authenticated = None
        self.command = self.commandhead + self.commandbody + self.commandtail

        error_map = {
            '11': 'Command does not contain username',
            '12': 'User is not authorized',
            '13': 'Wrong username and password',
            '14': 'No such user exists'
        }
        self.Error(['An error occurred: {}'.format(error_map[match.group(1).decode()])])
    
    def SetCloudClean(self, value, qualifier):

        CloudCleanCmdString = self.command.format('CloudClean', '', '', '')
        self.__SetHelper('CloudClean', CloudCleanCmdString, value, qualifier)

    def UpdateDisplayStatus(self, value, qualifier):

        user = qualifier['User']

        ValueStateValues = {
            'NotPresenting':    'Not Presenting',
            'Not Presenting':   'Not Presenting',
            'Presenting':       'Presenting',
            'Waiting':          'Waiting',
            'UsrNotExist':      'User Does Not Exist'
        }

        if user:
            DisplayStatusCmdString = self.command.format('DisplayStatus', 'Get', user, '')
            res = self.__UpdateHelper('DisplayStatus', DisplayStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res.strip().split('|')[-1]]
                    self.WriteStatus('DisplayStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Display Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDisplayStatus')

    def SetDoNotDisturb(self, value, qualifier):

        user = qualifier['User']

        ValueStateValues = {
            'On':   'Set',
            'Off':  'UnSet'
        }

        if user and value in ValueStateValues:
            DoNotDisturbCmdString = self.command.format('DND', ValueStateValues[value], user, '')
            self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDoNotDisturb')

    def UpdateIPAddress(self, value, qualifier):

        IPAddressCmdString = self.command.format('IpInfo', '', '', '')
        res = self.__UpdateHelper('IPAddress', IPAddressCmdString, value, qualifier)
        if res:
            try:
                value = res.strip()[3:-1]
                self.WriteStatus('IPAddress', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['IP Address: Invalid/unexpected response'])

    def SetKickoff(self, value, qualifier):

        user = qualifier['User']

        if user:
            KickoffCmdString = self.command.format('KickOff', user, '', '')
            self.__SetHelper('Kickoff', KickoffCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKickoff')

    def SetPresentationMode(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            PresentationModeCmdString = self.command.format('PrsMode', 'Set', ValueStateValues[value], '')
            self.__SetHelper('PresentationMode', PresentationModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentationMode')

    def UpdatePresentationMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PresentationModeCmdString = self.command.format('PrsMode', 'Get', '', '')
        res = self.__UpdateHelper('PresentationMode', PresentationModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split('|')[-1]]
                self.WriteStatus('PresentationMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Presentation Mode: Invalid/unexpected response'])

    def SetReboot(self, value, qualifier):

        RebootCmdString = self.command.format('Reboot', '', '', '')
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetRestartApacheServer(self, value, qualifier):

        RestartApacheServerCmdString = self.command.format('RestartApache', '', '', '')
        self.__SetHelper('RestartApacheServer', RestartApacheServerCmdString, value, qualifier)

    def UpdateRoomCode(self, value, qualifier):

        RoomCodeCmdString = self.command.format('RCode', 'Get', 'Code', '')
        res = self.__UpdateHelper('RoomCode', RoomCodeCmdString, value, qualifier)
        if res:
            try:
                if 'Error21' in res:
                    value = ''
                else:   
                    value = res.strip().split('|')[-1]

                self.WriteStatus('RoomCode', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Room Code: Invalid/unexpected response'])

    def SetScreenshare(self, value, qualifier):

        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            ScreenshareCmdString = self.command.format('ScreenShare', value, '', '')
            self.__SetHelper('Screenshare', ScreenshareCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenshare')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = self.command.format('Vol', 'Set', value, '')
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.command.format('Vol', 'Get', '', '')
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res.strip().split('|')[-1])
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def SetWakeUp(self, value, qualifier):

        ValueStateValues = {
            'On':   '0',
            'Off':  '1'
        }

        if value in ValueStateValues:
            WakeUpCmdString = self.command.format('WakeUp', ValueStateValues[value], '', '')
            self.__SetHelper('WakeUp', WakeUpCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWakeUp')

    def SetWifiGuestMode(self, value, qualifier):

        ValueStateValues = {
            'Start':    '1',
            'Stop':     '0'
        }

        if value in ValueStateValues:
            WifiGuestModeCmdString = self.command.format('WifiGuestMode', ValueStateValues[value], '', '')
            self.__SetHelper('WifiGuestMode', WifiGuestModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWifiGuestMode')

    def UpdateWifiGuestMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Start',
            '0': 'Stop'
        }

        WifiGuestModeCmdString = self.command.format('WifiGuestMode', 'Status', '', '')
        res = self.__UpdateHelper('WifiGuestMode', WifiGuestModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.strip().split('|')[-1]]
                self.WriteStatus('WifiGuestMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Wifi Guest Mode: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'Error' in response:
            self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, response.strip())])
            if sourceCmdName != 'RoomCode':
                return ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        elif self.authenticated:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.authenticated:
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
                    
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.update_delirex[command])
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Send(self.command.format('Login', '', '', ''))

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.authenticated = False
        self.command = self.commandhead + self.commandbody + self.commandtail

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
        
        #check incoming data if it matched any expected data from device module
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

