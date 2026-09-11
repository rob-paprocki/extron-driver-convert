from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
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
            'ChannelVolume': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MainZone': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'SurroundMode': {'Status': {}},
            'Volume': {'Status': {}},
            'Zone2Input': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'CV(FL|FR|C|SW|SL|SR|SBL|SBR) (\d{1,2})\x0D'), self.__MatchChannelVolume, None)
            self.AddMatchString(re.compile(b'SI(DVD|DOCK|BD|SAT|GAME1|GAME2|CD|MEDIA|BLUETOOTH|TV|TUNER)\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ZM(ON|OFF)\x0D'), self.__MatchMainZone, None)
            self.AddMatchString(re.compile(b'MU(ON|OFF)\x0D'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'PW(ON|STANDBY)\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'MSQUICK([1-4])'), self.__MatchPresetRecall, None)
            self.AddMatchString(re.compile(b'MS(DIRECT|STEREO|MOVIE|MUSIC|GAME|NEO6CINEMA|NEO6MUSIC|HALL|ROOM|STADIUM|THEATER)\x0D'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'MV(\d{1,2})\x0D'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Z2(DVD|DOCK|BD|SAT|CD|TUNER)\x0D'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'\x15|ERROR DECODE\x0D'), self.__MatchError, None)

        self.lastZone2Update = 0

    def SetChannelVolume(self, value, qualifier):

        ChannelStates = {
            'Front Left': 'FL',
            'Front Right': 'FR',
            'Center': 'C',
            'Subwoofer': 'SW',
            'Surround Left': 'SL',
            'Surround Right': 'SR',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR'
        }

        if -10 <= value <= 10:
            ChannelVolumeCmdString = 'CV{0} {1:02d}\x0D'.format(ChannelStates[qualifier['Channel']], value + 50)
            self.__SetHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelVolume')

    def UpdateChannelVolume(self, value, qualifier):

        ChannelStates = {
            'Front Left': 'FL',
            'Front Right': 'FR',
            'Center': 'C',
            'Subwoofer': 'SW',
            'Surround Left': 'SL',
            'Surround Right': 'SR',
            'Surround Back Left': 'SBL',
            'Surround Back Right': 'SBR'
        }

        ChannelVolumeCmdString = 'CV{0}\x3F\x0D'.format(ChannelStates[qualifier['Channel']])
        self.__UpdateHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)

    def __MatchChannelVolume(self, match, tag):

        ChannelStates = {
            'FL': 'Front Left',
            'FR': 'Front Right',
            'C': 'Center',
            'SW': 'Subwoofer',
            'SL': 'Surround Left',
            'SR': 'Surround Right',
            'SBL': 'Surround Back Left',
            'SBR': 'Surround Back Right'
        }

        value = int(match.group(2).decode()) - 50
        self.WriteStatus('ChannelVolume', value, {'Channel': ChannelStates[match.group(1).decode()]})

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Remote Control Lock On': 'SYREMOTE REMOTE LOCK ON\x0D',
            'Remote Control Lock Off': 'SYREMOTE REMOTE LOCK OFF\x0D',
            'Panel Lock With Volume': 'SYPANEL+V LOCK ON\x0D',
            'Panel Lock Without Volume': 'SYPANEL LOCK ON\x0D',
            'Off': 'SYPANEL LOCK OFF\x0D'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DVD': 'SIDVD\x0D',
            'Dock': 'SIDOCK\x0D',
            'BD': 'SIBD\x0D',
            'SAT': 'SISAT\x0D',
            'Game 1': 'SIGAME1\x0D',
            'Game 2': 'SIGAME2\x0D',
            'CD': 'SICD\x0D',
            'Media': 'SIMEDIA\x0D',
            'Bluetooth': 'SIBLUETOOTH\x0D',
            'TV': 'SITV\x0D',
            'Tuner': 'SITUNER\x0D'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SI\x3F\x0D'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'DVD': 'DVD',
            'DOCK': 'Dock',
            'BD': 'BD',
            'SAT': 'SAT',
            'GAME1': 'Game 1',
            'GAME2': 'Game 2',
            'CD': 'CD',
            'MEDIA': 'Media',
            'BLUETOOTH': 'Bluetooth',
            'TV': 'TV',
            'TUNER': 'Tuner'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMainZone(self, value, qualifier):

        ValueStateValues = {
            'On': 'ZMON\x0D',
            'Off': 'ZMOFF\x0D'
        }

        MainZoneCmdString = ValueStateValues[value]
        self.__SetHelper('MainZone', MainZoneCmdString, value, qualifier)

    def UpdateMainZone(self, value, qualifier):

        MainZoneCmdString = 'ZM\x3F\x0D'
        self.__UpdateHelper('MainZone', MainZoneCmdString, value, qualifier)

    def __MatchMainZone(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MainZone', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 'MNCUP\x0D',
            'Down': 'MNCDN\x0D',
            'Left': 'MNCLT\x0D',
            'Right': 'MNCRT\x0D',
            'Enter': 'MNENT\x0D'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUON\x0D',
            'Off': 'MUOFF\x0D'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'MU\x3F\x0D'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': 'MNMEN ON\x0D',
            'Off': 'MNMEN OFF\x0D'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PWON\x0D',
            'Standby': 'PWSTANDBY\x0D'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PW\x3F\x0D'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'STANDBY': 'Standby'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': 'MSQUICK1\x0D',
            '2': 'MSQUICK2\x0D',
            '3': 'MSQUICK3\x0D',
            '4': 'MSQUICK4\x0D'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def UpdatePresetRecall(self, value, qualifier):

        PresetRecallCmdString = 'MSQUICK\x3F\x0D'
        self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def __MatchPresetRecall(self, match, tag):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresetRecall', value, None)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': 'MSQUICK1 MEMORY\x0D',
            '2': 'MSQUICK2 MEMORY\x0D',
            '3': 'MSQUICK3 MEMORY\x0D',
            '4': 'MSQUICK4 MEMORY\x0D'
        }

        PresetSaveCmdString = ValueStateValues[value]

        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetSurroundMode(self, value, qualifier):

        ValueStateValues = {
            'Direct': 'MSDIRECT\x0D',
            'Stereo': 'MSSTEREO\x0D',
            'Movie': 'MSMOVIE\x0D',
            'Music': 'MSMUSIC\x0D',
            'Game': 'MSGAME\x0D',
            'Neo 6 Cinema': 'MSNEO6CINEMA\x0D',
            'Neo 6 Music': 'MSNEO6MUSIC\x0D',
            'Hall': 'MSHALL\x0D',
            'Room': 'MSROOM\x0D',
            'Stadium': 'MSSTADIUM\x0D',
            'Theater': 'MSTHEATER\x0D'
        }

        SurroundModeCmdString = ValueStateValues[value]
        self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS\x3F\x0D'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        ValueStateValues = {
            'DIRECT': 'Direct',
            'STEREO': 'Stereo',
            'MOVIE': 'Movie',
            'MUSIC': 'Music',
            'GAME': 'Game',
            'NEO6CINEMA': 'Neo 6 Cinema',
            'NEO6MUSIC': 'Neo 6 Music',
            'HALL': 'Hall',
            'ROOM': 'Room',
            'STADIUM': 'Stadium',
            'THEATER': 'Theater'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SurroundMode', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 90:
            VolumeCmdString = 'MV{0:02d}\x0D'.format(abs(value - 90))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'MV\x3F\x0D'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = abs(int(match.group(1).decode()) - 90)
        self.WriteStatus('Volume', value, None)

    def SetZone2Input(self, value, qualifier):

        ValueStateValues = {
            'DVD': 'Z2DVD\x0D',
            'Dock': 'Z2DOCK\x0D',
            'BD': 'Z2BD\x0D',
            'SAT/CBL': 'Z2SAT\x0D',
            'CD': 'Z2CD\x0D',
            'Tuner': 'Z2TUNER\x0D'
        }

        Zone2InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = 'Z2\x3F\x0D'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        ValueStateValues = {
            'DVD': 'DVD',
            'DOCK': 'Dock',
            'BD': 'BD',
            'SAT': 'SAT/CBL',
            'CD': 'CD',
            'TUNER': 'Tuner'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

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

        self.Error(['Device responded with an error.'])

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

