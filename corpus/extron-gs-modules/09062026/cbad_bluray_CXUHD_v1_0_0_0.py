from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

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
        self.Models = {}
        self.InitnialCmd = True
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChapterStatus': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'PlaybackStatus': {'Status': {}},
            'Power': {'Status': {}},
            'Repeat': {'Status': {}},
            'TrackTitleStatus': {'Status': {}},
            'Transport': {'Status': {}},
            'TVSystemOutput': {'Status': {}},
            'Volume': {'Status': {}},
            }

    def UpdateChapterStatus(self, value, qualifier):

        ChapterStatusCmdString = '#QCH\r'
        res = self.__UpdateHelper('ChapterStatus', ChapterStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[4:-1]
                self.WriteStatus('ChapterStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Chapter Status: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Blu-Ray Player': '#SIS 0\r',
            'Front HDMI/MHL': '#SIS 1\r',
            'Back HDMI': '#SIS 2\r',
            'ARC HDMI Out 1': '#SIS 3\r',
            'ARC HDMI Out 2': '#SIS 4\r',
            'Optical': '#SIS 5\r',
            'Coaxial': '#SIS 6\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'Blu-Ray Player',
            '1': 'Front HDMI/MHL',
            '2': 'Back HDMI',
            '3': 'ARC HDMI Out 1',
            '4': 'ARC HDMI Out 2',
            '5': 'Optical',
            '6': 'Coaxial'
        }

        InputCmdString = '#QIS\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '#NU0\r',
            '1': '#NU1\r',
            '2': '#NU2\r',
            '3': '#NU3\r',
            '4': '#NU4\r',
            '5': '#NU5\r',
            '6': '#NU6\r',
            '7': '#NU7\r',
            '8': '#NU8\r',
            '9': '#NU9\r',
            'Clear': '#CLR\r'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Home Menu': '#HOM\r',
            'Page Up': '#PUP\r',
            'Page Down': '#PDN\r',
            'Top Menu': '#TTL\r',
            'Pop-up Menu': '#MNU\r',
            'Up': '#NUP\r',
            'Down': '#NDN\r',
            'Left': '#NLT\r',
            'Right': '#NRT\r',
            'Enter': '#SEL\r',
            'Setup Menu': '#SET\r',
            'Return': '#RET\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = '#MUT\r'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdatePlaybackStatus(self, value, qualifier):

        ValueStateValues = {
            'NO DISC': 'No Disc',
            'LOADING': 'Loading',
            'OPEN': 'Open',
            'CLOSE': 'Close',
            'PLAY': 'Play',
            'PAUSE': 'Pause',
            'STOP': 'Stop',
            'STEP': 'Step',
            'FREV': 'FREV',
            'FFWD': 'FFWD',
            'SFWD': 'SFWD',
            'SREV': 'SREV',
            'SETUP': 'Setup',
            'HOME MENU': 'Home Menu',
            'MEDIA CENTER': 'Media Center'
        }

        PlaybackStatusCmdString = '#QPL\r'
        res = self.__UpdateHelper('PlaybackStatus', PlaybackStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('PlaybackStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Playback Status: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '#PON\r',
            'Off': '#POF\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        PowerCmdString = '#QPW\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'Chapter': '#SRP CH\r',
            'Title': '#SRP TT\r',
            'All': '#SRP ALL\r',
            'Shuffle': '#SRP SHF\r',
            'Random': '#SRP RND\r',
            'Off': '#SRP OFF\r'
        }

        RepeatCmdString = ValueStateValues[value]
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def UpdateRepeat(self, value, qualifier):

        ValueStateValues = {
            '2': 'Chapter',
            '4': 'Title',
            '3': 'All',
            '5': 'Shuffle',
            '6': 'Random',
            '0': 'Off'
        }

        RepeatCmdString = '#QRP\r'
        res = self.__UpdateHelper('Repeat', RepeatCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Repeat', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Repeat: Invalid/unexpected response'])

    def UpdateTrackTitleStatus(self, value, qualifier):

        TrackTitleStatusCmdString = '#QTK\r'
        res = self.__UpdateHelper('TrackTitleStatus', TrackTitleStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[4:-1]
                self.WriteStatus('TrackTitleStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Track/Title Status: Invalid/unexpected response'])

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Stop': '#STP\r',
            'Play': '#PLA\r',
            'Pause': '#PAU\r',
            'Previous': '#PRE\r',
            'Next': '#NXT\r',
            'Fast Reverse': '#REV\r',
            'Fast Forward': '#FWD\r',
            'Eject Disc Tray': '#EJT\r'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetTVSystemOutput(self, value, qualifier):

        ValueStateValues = {
            'NTSC': '#SPN NTSC\r',
            'PAL': '#SPN PAL\r',
            'Auto': '#SPN AUTO\r'
        }

        TVSystemOutputCmdString = ValueStateValues[value]
        self.__SetHelper('TVSystemOutput', TVSystemOutputCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '#SVL {}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '#QVL\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if '@ER' in response:
            self.Error(['{0} has error response'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if self.InitnialCmd:
                self.SendAndWait('#SVM 0\r', .2, deliTag=b'\r')
                self.InitnialCmd = False

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            if self.InitnialCmd:
                self.SendAndWait('#SVM 0\r', .2, deliTag=b'\r')
                self.InitnialCmd = False

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.InitnialCmd = False
        
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

