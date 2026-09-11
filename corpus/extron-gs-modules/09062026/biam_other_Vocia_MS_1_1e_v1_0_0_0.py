from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from Extron.exml.etree import ElementTree as ET


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
            'BackgroundAudioLevel': {'Parameters': ['Zone'], 'Status': {}},
            'BackgroundAudioMute': {'Parameters': ['Zone'], 'Status': {}},
            'BackgroundAudioSelection': {'Parameters': ['Zone', 'Bundle'], 'Status': {}},
            'PageInhibit': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneMute': {'Parameters': ['Zone'], 'Status': {}},
        }

        self.Authenticated = False
        self.AuthenticationErrorCount = 0
        self.BackgroundAudioLevelZone = None
        self.BackgroundAudioMuteZone = None
        self.BackgroundAudioSelectionZone = None
        self.PageInhibitZone = None
        self.ZoneMuteZone = None
        self.deviceUsername = None
        self.devicePassowrd = None

        if self.Unidirectional == 'False':
            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'Connection Accepted'), self.__MatchConnectionAccepted, None)
            self.AddMatchString(re.compile(b'AUTH_(SUCCESS|FAILURE|FAIL)'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'STATE_FAULT'), self.__MatchError, None)

    def __MatchConnectionAccepted(self, match, tag):
        self.SetAuthentication(None, None)

    def SetAuthentication(self, value, qualifier):

        if self.devicePassowrd is None:
            self.MissingCredentialsLog('Password')
        elif self.deviceUsername is None:
            self.MissingCredentialsLog('Username')
        else:
            self.Send('U {}\r'.format(self.deviceUsername))
            self.Send('P {}\r'.format(self.devicePassword))
            self.Send('A\r\n')

    def __MatchAuthentication(self, match, tag):

        if match.group(1).decode() == 'SUCCESS':
            self.Authenticated = True
        else:
            self.Authenticated = False
            self.Error('Invalid username and/or password supplied to the device.')

    def WriteAllStatusHandler(self, root):
        ValueStateValues = {
            'Y': 'On',
            'N': 'Off'
        }

        try:
            qualifier = {'Zone': root.attrib['id']}
            value = int(root.find('ZoneLevel').text)
            if 1 <= int(qualifier['Zone']) <= 200 and 0 <= value <= 100:
                self.WriteStatus('BackgroundAudioLevel', value, qualifier)
            else:
                self.Error(['Background Audio Level: Invalid/unexpected response'])
        except (KeyError, ValueError, AttributeError):
            self.Error(['Background Audio Level: Invalid/unexpected response'])

        try:
            qualifier = {'Zone': root.attrib['id']}
            if 1 <= int(qualifier['Zone']) <= 200:
                value = ValueStateValues[root.find('ZoneBackgroundMute').text]
                self.WriteStatus('BackgroundAudioMute', value, qualifier)
            else:
                self.Error(['Background Audio Mute: Invalid/unexpected response'])
        except (KeyError, ValueError, AttributeError):
            self.Error(['Background Audio Mute: Invalid/unexpected response'])

        try:
            qualifier = {'Zone': root.attrib['id'], 'Bundle': int(root.find('Bundle').text)}
            value = root.find('Channel').text
            if 1 <= int(qualifier['Zone']) <= 200 and 1 <= qualifier['Bundle'] <= 65279 and 1 <= int(value) <= 8:
                self.WriteStatus('BackgroundAudioSelection', value, qualifier)
            else:
                self.Error(['Background Audio Selection: Invalid/unexpected response'])
        except (KeyError, ValueError, AttributeError):
            self.Error(['Background Audio Selection: Invalid/unexpected response'])

        try:
            qualifier = {'Zone': root.attrib['id']}
            if 1 <= int(qualifier['Zone']) <= 200:
                value = ValueStateValues[root.find('ZonePageInhibit').text]
                self.WriteStatus('PageInhibit', value, qualifier)
            else:
                self.Error(['Page Inhibit: Invalid/unexpected response'])
        except (KeyError, ValueError, AttributeError):
            self.Error(['Page Inhibit: Invalid/unexpected response'])

        try:
            qualifier = {'Zone': root.attrib['id']}
            if 1 <= int(qualifier['Zone']) <= 200:
                value = ValueStateValues[root.find('ZoneMute').text]
                self.WriteStatus('ZoneMute', value, qualifier)
            else:
                self.Error(['Zone Mute: Invalid/unexpected response'])
        except (KeyError, ValueError, AttributeError):
            self.Error(['Zone Mute: Invalid/unexpected response'])

    def SetBackgroundAudioLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        zone = qualifier['Zone']
        if 1 <= int(zone) <= 200 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BackgroundAudioLevelCmdString = 'B L P {}\r\n'.format(value)
            if self.BackgroundAudioLevelZone != zone:
                self.BackgroundAudioLevelZone = zone
                self.__SetHelper('BackgroundAudioLevel', 'Z {}\r\n'.format(zone), value, qualifier)
            self.__SetHelper('BackgroundAudioLevel', BackgroundAudioLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackgroundAudioLevel')

    def UpdateBackgroundAudioLevel(self, value, qualifier):

        zone = qualifier['Zone']
        if 1 <= int(zone) <= 200:
            BackgroundAudioLevelCmdString = 'B Q {}\r\n'.format(zone)
            res = self.__UpdateHelper('BackgroundAudioLevel', BackgroundAudioLevelCmdString, value, qualifier)
            if res:
                self.WriteAllStatusHandler(ET.fromstring(res))
        else:
            self.Discard('Device Is Busy for UpdateBackgroundAudioLevel')

    def SetBackgroundAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        zone = qualifier['Zone']
        if 1 <= int(zone) <= 200:
            BackgroundAudioMuteCmdString = 'B M {}\r\n'.format(ValueStateValues[value])
            if self.BackgroundAudioMuteZone != zone:
                self.BackgroundAudioMuteZone = zone
                self.__SetHelper('BackgroundAudioMute', 'Z {}\r\n'.format(zone), value, qualifier)
            self.__SetHelper('BackgroundAudioMute', BackgroundAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackgroundAudioMute')

    def UpdateBackgroundAudioMute(self, value, qualifier):

        zone = qualifier['Zone']
        if 1 <= int(zone) <= 200:
            BackgroundAudioMuteCmdString = 'B Q {}\r\n'.format(zone)
            res = self.__UpdateHelper('BackgroundAudioMute', BackgroundAudioMuteCmdString, value, qualifier)
            if res:
                self.WriteAllStatusHandler(ET.fromstring(res))
        else:
            self.Discard('Device Is Busy for UpdateBackgroundAudioMute')

    def SetBackgroundAudioSelection(self, value, qualifier):

        zone = qualifier['Zone']
        if 1 <= int(zone) <= 200 and 1 <= qualifier['Bundle'] <= 65279 and 1 <= int(value) <= 8:
            BackgroundAudioSelectionCmdString = 'B S {} {}\r\n'.format(qualifier['Bundle'], value)
            if self.BackgroundAudioSelectionZone != zone:
                self.BackgroundAudioSelectionZone = zone
                self.__SetHelper('BackgroundAudioSelection', 'Z {}\r\n'.format(zone), value, qualifier)
            self.__SetHelper('BackgroundAudioSelection', BackgroundAudioSelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackgroundAudioSelection')

    def UpdateBackgroundAudioSelection(self, value, qualifier):

        if 1 <= int(qualifier['Zone']) <= 200 and 1 <= qualifier['Bundle'] <= 65279:
            BackgroundAudioSelectionCmdString = 'B Q {}\r\n'.format(qualifier['Zone'])
            res = self.__UpdateHelper('BackgroundAudioSelection', BackgroundAudioSelectionCmdString, value, qualifier)
            if res:
                self.WriteAllStatusHandler(ET.fromstring(res))
        else:
            self.Discard('Device Is Busy for UpdateBackgroundAudioSelection')

    def UpdateHeartbeat(self, value, qualifier):

        HeartbeatCmdString = 'Q C\r\n'
        self.__UpdateHelper('Heartbeat', HeartbeatCmdString, value, qualifier)

    def SetPageInhibit(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        zone = qualifier['Zone']
        if 1 <= int(zone) <= 200:
            PageInhibitCmdString = 'B I {}\r\n'.format(ValueStateValues[value])
            if self.PageInhibitZone != zone:
                self.PageInhibitZone = zone
                self.__SetHelper('PageInhibit', 'Z {}\r\n'.format(zone), value, qualifier)
            self.__SetHelper('PageInhibit', PageInhibitCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPageInhibit')

    def UpdatePageInhibit(self, value, qualifier):

        zone = qualifier['Zone']
        if 1 <= int(zone) <= 200:
            PageInhibitCmdString = 'B Q {}\r\n'.format(zone)
            res = self.__UpdateHelper('PageInhibit', PageInhibitCmdString, value, qualifier)
            if res:
                self.WriteAllStatusHandler(ET.fromstring(res))
        else:
            self.Discard('Device Is Busy for UpdatePageInhibit')

    def SetZoneMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        zone = qualifier['Zone']
        if 1 <= int(zone) <= 200:
            ZoneMuteCmdString = 'B Z {}\r\n'.format(ValueStateValues[value])
            if self.ZoneMuteZone != zone:
                self.ZoneMuteZone = zone
                self.__SetHelper('ZoneMute', 'Z {}\r\n'.format(zone), value, qualifier)
            self.__SetHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneMute')

    def UpdateZoneMute(self, value, qualifier):

        zone = qualifier['Zone']
        if 1 <= int(zone) <= 200:
            ZoneMuteCmdString = 'B Q {}\r\n'.format(zone)
            res = self.__UpdateHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)
            if res:
                self.WriteAllStatusHandler(ET.fromstring(res))
        else:
            self.Discard('Device Is Busy for UpdateZoneMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if '</Query>' not in response and '</ZoneStatus>' not in response:
                self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
                response = ''
            elif 'STATE_FAULT' in response:
                self.Error(['{}: An error occurred'.format(sourceCmdName)])
                response = ''
            elif 'AUTH_FAIL' in response:
                self.Authenticated = False
                self.Error('Invalid username and/or password supplied to the device.')  # send error message
        return response

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

        if self.Authenticated:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'</ZoneStatus>')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):
        self.Error(['An error occurred'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = False
        self.AuthenticationErrorCount = 0
        self.BackgroundAudioLevelZone = None
        self.BackgroundAudioMuteZone = None
        self.BackgroundAudioSelectionZone = None
        self.PageInhibitZone = None
        self.ZoneMuteZone = None

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
