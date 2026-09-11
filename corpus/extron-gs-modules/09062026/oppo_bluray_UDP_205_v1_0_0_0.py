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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3D': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AudioMuteStatus': {'Status': {}},
            'AudioSelector': {'Status': {}},
            'CurrentChapter': {'Status': {}},
            'CurrentTitleTrack': {'Status': {}},
            'Dimmer': {'Status': {}},
            'Keypad': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PIP': {'Status': {}},
            'PlaybackStatus': {'Status': {}},
            'Power': {'Status': {}},
            'PureAudio': {'Status': {}},
            'Subtitle': {'Status': {}},
            'TimeElapsedChapter': {'Status': {}},
            'TimeElapsedTitleTrack': {'Status': {}},
            'TimeElapsedTotal': {'Status': {}},
            'TimeRemainingChapter': {'Status': {}},
            'TimeRemainingTitleTrack': {'Status': {}},
            'TimeRemainingTotal': {'Status': {}},
            'Transport': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStep': {'Status': {}},
			'Zoom': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'@QCH OK ([0-9]{1,3}/[0-9]{1,3})\r'), self.__MatchCurrentChapter, None)
            self.AddMatchString(re.compile(b'@QTK OK ([0-9]{1,3}/[0-9]{1,3})\r'), self.__MatchCurrentTitleTrack, None)
            self.AddMatchString(re.compile(b'@(UPL|QPL)( | OK )(DISC|LOAD|OPEN|CLOS|PLAY|PAUS|STOP|STPF|STPR|FFW([1-5]|D)|FRV[1-5]|SFW([1-4]|D)|SRV[0-5]|HOME|MCTR|NO DISC|LOADING|CLOSE|PAUSE|STEP|FREV|SREV|SETUP|HOME MENU|MEDIA CENTER)\r'), self.__MatchPlaybackStatus, None)
            self.AddMatchString(re.compile(b'@(UPW|QPW)( | OK )(0|1|ON|OFF)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'@QCE OK ([0-9]{2}:[0-9]{2}:[0-9]{2})\r'), self.__MatchTimeElapsedChapter, None)
            self.AddMatchString(re.compile(b'@QTE OK ([0-9]{2}:[0-9]{2}:[0-9]{2})\r'), self.__MatchTimeElapsedTitleTrack, None)
            self.AddMatchString(re.compile(b'@QEL OK ([0-9]{2}:[0-9]{2}:[0-9]{2})\r'), self.__MatchTimeElapsedTotal, None)
            self.AddMatchString(re.compile(b'@QCR OK ([0-9]{2}:[0-9]{2}:[0-9]{2})\r'), self.__MatchTimeRemainingChapter, None)
            self.AddMatchString(re.compile(b'@QTR OK ([0-9]{2}:[0-9]{2}:[0-9]{2})\r'), self.__MatchTimeRemainingTitleTrack, None)
            self.AddMatchString(re.compile(b'@QRE OK ([0-9]{2}:[0-9]{2}:[0-9]{2})\r'), self.__MatchTimeRemainingTotal, None)
            self.AddMatchString(re.compile(b'@QVL OK ([0-9]{1,3}|MUTE)\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'@([A-Z]{3}) ER [\s\S]*\r'), self.__MatchError, None)

    def SetVerbose(self, value, qualifier):

        self.Send('#SVM 2\r\n')

    def Set3D(self, value, qualifier):

        ThreeDCmdString = '#M3D\r\n'
        self.__SetHelper('3D', ThreeDCmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '#SZM AR\r\n',
            'Full Screen': '#SZM FS\r\n',
            'Underscan': '#SZM US\r\n',
            '1.2': '#SZM 1.2\r\n',
            '1.3': '#SZM 1.3\r\n',
            '1.5': '#SZM 1.5\r\n',
            '2': '#SZM 2\r\n',
            '1/2': '#SZM 1/2\r\n',
            '3': '#SZM 3\r\n',
            '4': '#SZM 4\r\n',
            '1/3': '#SZM 1/3\r\n',
            '1/4': '#SZM 1/4\r\n',
            '1': '#SZM 1\r\n'
        }
        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = '#MUT\r\n'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMuteStatus(self, value, qualifier):

        self.UpdateVolume(None, None)

    def SetAudioSelector(self, value, qualifier):

        AudioSelectorCmdString = '#AUD\r\n'
        self.__SetHelper('AudioSelector', AudioSelectorCmdString, value, qualifier)

    def UpdateCurrentChapter(self, value, qualifier):

        CurrentChapterCmdString = '#QCH\r\n'
        self.__UpdateHelper('CurrentChapter', CurrentChapterCmdString, value, qualifier)

    def __MatchCurrentChapter(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentChapter', value, None)

    def UpdateCurrentTitleTrack(self, value, qualifier):

        CurrentTitleTrackCmdString = '#QTK\r\n'
        self.__UpdateHelper('CurrentTitleTrack', CurrentTitleTrackCmdString, value, qualifier)

    def __MatchCurrentTitleTrack(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentTitleTrack', value, None)

    def SetDimmer(self, value, qualifier):

        DimmerCmdString = '#DIM\r\n'
        self.__SetHelper('Dimmer', DimmerCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Blu-Ray Player': '#SIS 0\r\n',
            'HDMI': '#SIS 1\r\n',
            'ARC-HDMI-OUT': '#SIS 2\r\n',
            'Optical': '#SIS 3\r\n',
            'Coaxial': '#SIS 4\r\n',
            'USB Audio': '#SIS 5\r\n'
            }
        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '#NU1\r\n',
            '2': '#NU2\r\n',
            '3': '#NU3\r\n',
            '4': '#NU4\r\n',
            '5': '#NU5\r\n',
            '6': '#NU6\r\n',
            '7': '#NU7\r\n',
            '8': '#NU8\r\n',
            '9': '#NU9\r\n',
            '0': '#NU0\r\n',
            'Clear': '#CLR\r\n'
        }
        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Home': '#HOM\r\n',
            'Page Up': '#PUP\r\n',
            'Page Down': '#PDN\r\n',
            'Top Menu': '#TTL\r\n',
            'Pop-Up Menu': '#MNU\r\n',
            'Return': '#RET\r\n',
            'Up': '#NUP\r\n',
            'Down': '#NDN\r\n',
            'Left': '#NLT\r\n',
            'Right': '#NRT\r\n',
            'Enter': '#SEL\r\n',
            'Option': '#OPT\r\n',
            'Setup': '#SET\r\n'
        }
        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = '#OSD\r\n'
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPIP(self, value, qualifier):

        PIPCmdString = '#PIP\r\n'
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePlaybackStatus(self, value, qualifier):

        PlaybackStatusCmdString = '#QPL\r\n'
        self.__UpdateHelper('PlaybackStatus', PlaybackStatusCmdString, value, qualifier)

    def __MatchPlaybackStatus(self, match, tag):

        ValueStateValues = {
            b'NO DISC': 'No Disc',
            b'DISC': 'No Disc',
            b'LOADING': 'Loading',
            b'LOAD': 'Loading',
            b'OPEN': 'Open',
            b'CLOSE': 'Close',
            b'CLOS': 'Close',
            b'PLAY': 'Play',
            b'PAUSE': 'Pause',
            b'PAUS': 'Pause',
            b'STOP': 'Stop',
            b'STEP': 'Step',
            b'STPF': 'Step Forward',
            b'STPR': 'Step Reverse',
            b'FREV': 'Fast Reverse',
            b'FRV1': 'Fast Reverse',
            b'FRV2': 'Fast Reverse',
            b'FRV3': 'Fast Reverse',
            b'FRV4': 'Fast Reverse',
            b'FRV5': 'Fast Reverse',
            b'FFWD': 'Fast Forward',
            b'FFW1': 'Fast Forward',
            b'FFW2': 'Fast Forward',
            b'FFW3': 'Fast Forward',
            b'FFW4': 'Fast Forward',
            b'FFW5': 'Fast Forward',
            b'SREV': 'Slow Reverse',
            b'SRV1': 'Slow Reverse',
            b'SRV2': 'Slow Reverse',
            b'SRV3': 'Slow Reverse',
            b'SRV4': 'Slow Reverse',
            b'SFWD': 'Slow Forward',
            b'SFW1': 'Slow Forward',
            b'SFW2': 'Slow Forward',
            b'SFW3': 'Slow Forward',
            b'SFW4': 'Slow Forward',
            b'SETUP': 'Setup',
            b'HOME MENU': 'Home Menu',
            b'HOME': 'Home Menu',
            b'MEDIA CENTER': 'Media Center',
            b'MCTR': 'Media Center'
        }
        value = ValueStateValues[match.group(3)]
        self.WriteStatus('PlaybackStatus', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '#PON\r\n',
            'Off': '#POF\r\n'
        }
        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '#QPW\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'ON': 'On',
            b'1': 'On',
            b'OFF': 'Off',
            b'0': 'Off'
        }
        value = ValueStateValues[match.group(3)]
        self.WriteStatus('Power', value, None)

    def SetPureAudio(self, value, qualifier):

        PureAudioCmdString = '#PUR\r\n'
        self.__SetHelper('PureAudio', PureAudioCmdString, value, qualifier)

    def SetSubtitle(self, value, qualifier):

        SubtitleCmdString = '#SUB\r\n'
        self.__SetHelper('Subtitle', SubtitleCmdString, value, qualifier)

    def UpdateTimeElapsedChapter(self, value, qualifier):

        TimeElapsedChapterCmdString = '#QCE\r\n'
        self.__UpdateHelper('TimeElapsedChapter', TimeElapsedChapterCmdString, value, qualifier)

    def __MatchTimeElapsedChapter(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TimeElapsedChapter', value, None)

    def UpdateTimeElapsedTitleTrack(self, value, qualifier):

        TimeElapsedTitleTrackCmdString = '#QTE\r\n'
        self.__UpdateHelper('TimeElapsedTitleTrack', TimeElapsedTitleTrackCmdString, value, qualifier)

    def __MatchTimeElapsedTitleTrack(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TimeElapsedTitleTrack', value, None)

    def UpdateTimeElapsedTotal(self, value, qualifier):

        TimeElapsedTotalCmdString = '#QEL\r\n'
        self.__UpdateHelper('TimeElapsedTotal', TimeElapsedTotalCmdString, value, qualifier)

    def __MatchTimeElapsedTotal(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TimeElapsedTotal', value, None)

    def UpdateTimeRemainingChapter(self, value, qualifier):

        TimeRemainingChapterCmdString = '#QCR\r\n'
        self.__UpdateHelper('TimeRemainingChapter', TimeRemainingChapterCmdString, value, qualifier)

    def __MatchTimeRemainingChapter(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TimeRemainingChapter', value, None)

    def UpdateTimeRemainingTitleTrack(self, value, qualifier):

        TimeRemainingTitleTrackCmdString = '#QTR\r\n'
        self.__UpdateHelper('TimeRemainingTitleTrack', TimeRemainingTitleTrackCmdString, value, qualifier)

    def __MatchTimeRemainingTitleTrack(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TimeRemainingTitleTrack', value, None)

    def UpdateTimeRemainingTotal(self, value, qualifier):

        TimeRemainingTotalCmdString = '#QRE\r\n'
        self.__UpdateHelper('TimeRemainingTotal', TimeRemainingTotalCmdString, value, qualifier)

    def __MatchTimeRemainingTotal(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TimeRemainingTotal', value, None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '#PLA\r\n',
            'Pause': '#PAU\r\n',
            'Stop': '#STP\r\n',
            'Previous': '#PRE\r\n',
            'Reverse': '#REV\r\n',
            'Forward': '#FWD\r\n',
            'Next': '#NXT\r\n',
            'Eject': '#EJT\r\n',
            'Repeat': '#RPT\r\n'
        }
        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '#SVL {0}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '#QVL\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        volume = match.group(1).decode()
        if volume == 'MUTE':
            self.WriteStatus('AudioMuteStatus', 'On', None)
        else:
            self.WriteStatus('AudioMuteStatus', 'Off', None)
            value = int(volume)
            if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                self.WriteStatus('Volume', value, None)
            else:
                self.Error(['Volume: Invalid/unexpected response'])

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': '#VUP\r\n',
            'Down': '#VDN\r\n'
        }
        VolumeStepCmdString = ValueStateValues[value]
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomCmdString = '#ZOM\r\n'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

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

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        value = match.group(1).decode()
        self.Error(['An error occured while executing command: ' + value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.SetVerbose( None, None)

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