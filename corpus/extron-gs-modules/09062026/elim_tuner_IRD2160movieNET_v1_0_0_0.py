from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait


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
            'AudioMute': {'Status': {}},
            'CurrentChannel': {'Status': {}},
            'CurrentMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FrontPanelLock': {'Status': {}},
            'IRRemoteEmulation': {'Status': {}},
            'IRRemoteLock': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'RadioChannel': {'Status': {}},
            'RadioChannelCommand': {'Status': {}},
            'Record': {'Status': {}},
            'Transport': {'Status': {}},
            'TVChannel': {'Status': {}},
            'TVChannelCommand': {'Status': {}},
            'Volume': {'Status': {}},
            }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'#COMMAND: <VOL \?>[\s\S]*#RET: (on|off);(100|[1-9][0-9]|[0-9])[\s\S]*#OK', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'#COMMAND: <GCC>[\s\S]*#RET: (\d+)[\s\S]*#OK', re.I), self.__MatchCurrentChannel, None)
            self.AddMatchString(re.compile(b'#COMMAND: <GCM>[\s\S]*#RET: (Restart|Standby|Idle|TV|Radio|Time Shift|Media Player|Search|Firmware Update|HDD Format)[\s\S]*#OK', re.I), self.__MatchCurrentMode, None)
            self.AddMatchString(re.compile(b'#COMMAND: <LCK \?>[\s\S]*#RET: (on|off)[\s\S]*#OK', re.I), self.__MatchFrontPanelLock, None)
            self.AddMatchString(re.compile(b'#COMMAND: <LCI \?>[\s\S]*#RET: (on|off)[\s\S]*#OK', re.I), self.__MatchIRRemoteLock, None)
            self.AddMatchString(re.compile(b'#COMMAND: <GCS>[\s\S]*#RET: (on|off)[\s\S]*#OK', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'#COMMAND: <REC \?>[\s\S]*#RET: (on|off)[\s\S]*#OK', re.I), self.__MatchRecord, None)
            self.AddMatchString(re.compile(b'#ERROR:([\s\S]+)'), self.__MatchError, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '<VOL OFF>',
            'Off': '<VOL ON>'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '<VOL ?>'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            'OFF': 'On',
            'ON': 'Off'
        }
        aud_val = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('AudioMute', aud_val, None)

        vol_val = int(match.group(2).decode())
        self.WriteStatus('Volume', vol_val, None)

    def UpdateCurrentChannel(self, value, qualifier):

        CurrentChannelCmdString = '<GCC>'
        self.__UpdateHelper('CurrentChannel', CurrentChannelCmdString, value, qualifier)

    def __MatchCurrentChannel(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('CurrentChannel', value, None)

    def SetCurrentMode(self, value, qualifier):

        ValueStateValues = {
            'TV': '<TTT>',
            'Radio': '<TTR>'
        }

        CurrentModeCmdString = ValueStateValues[value]
        self.__SetHelper('CurrentMode', CurrentModeCmdString, value, qualifier)

    def UpdateCurrentMode(self, value, qualifier):

        CurrentModeCmdString = '<GCM>'
        self.__UpdateHelper('CurrentMode', CurrentModeCmdString, value, qualifier)
        
    def __MatchCurrentMode(self, match, tag):

        ValueStateValues = {
            'TV': 'TV',
            'RADIO': 'Radio'
        }

        DeviceStatusValues = {
            'RESTART': 'Booting Up',
            'STANDBY': 'Standby',
            'IDLE': 'Menu (Idle)',
            'TV': 'TV Program Playback',
            'RADIO': 'Radio Program Playback',
            'TIME SHIFT': 'Time Shifting Mode',
            'MEDIA PLAYER': 'Media Player Mode',
            'SEARCH': 'Searching for the Channels',
            'FIRMWARE UPDATE': 'Updating Firmware',
            'HDD FORMAT': 'Formatting HDD'
        }

        if match.group(1).decode().upper() in ValueStateValues:
            value = ValueStateValues[match.group(1).decode().upper()]
            self.WriteStatus('CurrentMode', value, None)
        else:
            self.WriteStatus('CurrentMode', 'Not in TV/Radio Mode', None)

        value = DeviceStatusValues[match.group(1).decode().upper()]
        self.WriteStatus('DeviceStatus', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        self.UpdateCurrentMode(None, qualifier)

    def SetFrontPanelLock(self, value, qualifier):

        ValueStateValues = {
            'On': '<LCK 1>',
            'Off': '<LCK 0>'
        }

        FrontPanelLockCmdString = ValueStateValues[value]
        self.__SetHelper('FrontPanelLock', FrontPanelLockCmdString, value, qualifier)

    def UpdateFrontPanelLock(self, value, qualifier):

        FrontPanelLockCmdString = '<LCK ?>'
        self.__UpdateHelper('FrontPanelLock', FrontPanelLockCmdString, value, qualifier)

    def __MatchFrontPanelLock(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('FrontPanelLock', value, None)

    def SetIRRemoteEmulation(self, value, qualifier):

        ValueStateValues = {
            '0': '<RMCC 21>',
            '1': '<RMCC 2>',
            '2': '<RMCC 5>',
            '3': '<RMCC 6>',
            '4': '<RMCC 9>',
            '5': '<RMCC 10>',
            '6': '<RMCC 13>',
            '7': '<RMCC 14>',
            '8': '<RMCC 17>',
            '9': '<RMCC 18>',
            'OK': '<RMCC 30>',
            'Exit': '<RMCC 45>',
            'Menu': '<RMCC 42>',
            'Up': '<RMCC 25>',
            'Down': '<RMCC 26>',
            'Right': '<RMCC 33>',
            'Left': '<RMCC 29>',
            'Text': '<RMCC 73>',
            'EPG': '<RMCC 69>',
            'Record / Stop': '<RMCC 54>',
            'Info': '<RMCC 66>',
            'Yellow (MP3/JPEG/Music)': '<RMCC 62>',
            'Red (DVR/PVR)': '<RMCC 58>',
            'Radio/TV': '<RMCC 37>',
            'Last': '<RMCC 41>',
            'On/Off': '<RMCC 22>',
            'Mute': '<RMCC 38>',
            'PIP': '<RMCC 74>',
            'Search/Freeze': '<RMCC 77>',
            'Tech Info/Zoom': '<RMCC 78>',
            'Audio Video': '<RMCC 81>',
            'Mode': '<RMCC 34>',
            'Green (Movie/DVD)': '<RMCC 61>',
            'Blue (Media/Game)': '<RMCC 65>',
            'Rewind': '<RMCC 46>',
            'Play/Pause': '<RMCC 49>',
            'Forward': '<RMCC 50>',
            'Previous': '<RMCC 53>',
            'Next': '<RMCC 57>',
            'Timer': '<RMCC 70>'
        }

        IRRemoteEmulationCmdString = ValueStateValues[value]
        self.__SetHelper('IRRemoteEmulation', IRRemoteEmulationCmdString, value, qualifier)

    def SetIRRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'On': '<LCI 1>',
            'Off': '<LCI 0>'
        }

        IRRemoteLockCmdString = ValueStateValues[value]
        self.__SetHelper('IRRemoteLock', IRRemoteLockCmdString, value, qualifier)

    def UpdateIRRemoteLock(self, value, qualifier):

        IRRemoteLockCmdString = '<LCI ?>'
        self.__UpdateHelper('IRRemoteLock', IRRemoteLockCmdString, value, qualifier)

    def __MatchIRRemoteLock(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('IRRemoteLock', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '<MNU>',
            'Exit': '<EXT>',
            'Select': '<CNF>',
            'Up': '<NAV U>',
            'Down': '<NAV D>',
            'Left': '<NAV L>',
            'Right': '<NAV R>'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '<ON>',
            'Off': '<OFF>'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '<GCS>'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Power', value, None)

    def SetRadioChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': '<PRR U>',
            'Down': '<PRR D>'
        }

        RadioChannelCmdString = ValueStateValues[value]
        self.__SetHelper('RadioChannel', RadioChannelCmdString, value, qualifier)

    def SetRadioChannelCommand(self, value, qualifier):

        channel_val = value
        if channel_val:
            RadioChannelCommandCmdString = '<PRR {0}>'.format(channel_val)
            self.__SetHelper('RadioChannelCommand', RadioChannelCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRadioChannelCommand')

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'Start': '<REC ON>',
            'Stop': '<REC OFF>'
        }

        RecordCmdString = ValueStateValues[value]
        self.__SetHelper('Record', RecordCmdString, value, qualifier)

    def UpdateRecord(self, value, qualifier):

        RecordCmdString = '<REC ?>'
        self.__UpdateHelper('Record', RecordCmdString, value, qualifier)

    def __MatchRecord(self, match, tag):

        ValueStateValues = {
            'ON': 'Start',
            'OFF': 'Stop'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Record', value, None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '<MPPLAY>',
            'Pause': '<MPPAUSE>',
            'Stop': '<MPSTOP>',
            'Fast Forward': '<MPFF>',
            'Rewind': '<MPRW>',
            'Start': '<MPSTA>',
            'Middle': '<MPMID>',
            'End': '<MPEND>'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetTVChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': '<PRT U>',
            'Down': '<PRT D>'
        }

        TVChannelCmdString = ValueStateValues[value]
        self.__SetHelper('TVChannel', TVChannelCmdString, value, qualifier)

    def SetTVChannelCommand(self, value, qualifier):

        channel_val = value
        if channel_val:
            TVChannelCommandCmdString = '<PRT {0}>'.format(channel_val)
            self.__SetHelper('TVChannelCommand', TVChannelCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTVChannelCommand')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '<VOL {0}>'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.UpdateAudioMute(None, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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
        self.counter = 0
        value = match.group(0).decode()
        self.Error([value])

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

