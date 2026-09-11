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
            'CurrentTrackAlbum': { 'Status': {}},
            'CurrentTrackArtist': { 'Status': {}},
            'CurrentTrackTitle': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'DiscTray': { 'Status': {}},
            'ElapsedTime': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MediaStatus': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'RemainingTime': { 'Status': {}},
            'SlowSearch': { 'Status': {}},
            'TrackNumber': { 'Status': {}},
            'TrackTotal': { 'Status': {}},
            'Transport': { 'Status': {}},
            }

          
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'@0al([\S ]+)\r'), self.__MatchCurrentTrackAlbum, None)
            self.AddMatchString(re.compile(b'@0at([\S ]+)\r'), self.__MatchCurrentTrackArtist, None)
            self.AddMatchString(re.compile(b'@0ti([\S ]+)\r'), self.__MatchCurrentTrackTitle, None)
            self.AddMatchString(re.compile(b'@0ST(PL|PP|DVFR|DVFF)\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'@0ET(\d{3})(\d{2})(\d{2})\r'), self.__MatchElapsedTime, None)
            self.AddMatchString(re.compile(b'@0CD(NC|CI)\r'), self.__MatchMediaStatus, None)
            self.AddMatchString(re.compile(b'@0mt0(0|1)\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'@0PW0(0|1)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'@0RM(\d{3})(\d{2})(\d{2})\r'), self.__MatchRemainingTime, None)
            self.AddMatchString(re.compile(b'@0PCSLS(F|R)\r'), self.__MatchSlowSearch, None)
            self.AddMatchString(re.compile(b'@0Tr(\d{4}|UNKN)\r'), self.__MatchTrackNumber, None)
            self.AddMatchString(re.compile(b'@0Tt(\d{4}|UNKN)\r'), self.__MatchTrackTotal, None)
            self.AddMatchString(re.compile(b'@0BDERBUSY|\x15'), self.__MatchError, None)

    def UpdateCurrentTrackAlbum(self, value, qualifier):

        CurrentTrackAlbumCmdString = '@0?al\r'
        self.__UpdateHelper('CurrentTrackAlbum', CurrentTrackAlbumCmdString, value, qualifier)

    def __MatchCurrentTrackAlbum(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentTrackAlbum', value, None)

    def UpdateCurrentTrackArtist(self, value, qualifier):

        CurrentTrackArtistCmdString = '@0?at\r'
        self.__UpdateHelper('CurrentTrackArtist', CurrentTrackArtistCmdString, value, qualifier)

    def __MatchCurrentTrackArtist(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentTrackArtist', value, None)

    def UpdateCurrentTrackTitle(self, value, qualifier):

        CurrentTrackTitleCmdString = '@0?ti\r'
        self.__UpdateHelper('CurrentTrackTitle', CurrentTrackTitleCmdString, value, qualifier)

    def __MatchCurrentTrackTitle(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentTrackTitle', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '@0?ST\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            'PL'   : 'Play', 
            'PP'   : 'Pause',  
            'DVFR' : 'Fast Play Reverse', 
            'DVFF' : 'Fast Play Forward', 
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetDiscTray(self, value, qualifier):

        ValueStateValues = {
            'Open'  : '@0PCDTRYOP\r', 
            'Close' : '@0PCDTRYCL\r'
        }

        DiscTrayCmdString = ValueStateValues[value]
        self.__SetHelper('DiscTray', DiscTrayCmdString, value, qualifier)
    def UpdateElapsedTime(self, value, qualifier):

        ElapsedTimeCmdString = '@0?ET\r'
        self.__UpdateHelper('ElapsedTime', ElapsedTimeCmdString, value, qualifier)

    def __MatchElapsedTime(self, match, tag):

        value = match.group(1).decode() + ':' + match.group(2).decode() + ':' + match.group(3).decode()
        if value[0] == '0' and value[1] == '0':
            value = value[2:]
        elif value[0] == '0' and value[1] != '0':
            value = value[1:]
        self.WriteStatus('ElapsedTime', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : '@0PCTKEY0\r', 
            '1' : '@0PCTKEY1\r', 
            '2' : '@0PCTKEY2\r', 
            '3' : '@0PCTKEY3\r', 
            '4' : '@0PCTKEY4\r', 
            '5' : '@0PCTKEY5\r', 
            '6' : '@0PCTKEY6\r', 
            '7' : '@0PCTKEY7\r', 
            '8' : '@0PCTKEY8\r', 
            '9' : '@0PCTKEY9\r'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
    def UpdateMediaStatus(self, value, qualifier):

        MediaStatusCmdString = '@0?CD\r'
        self.__UpdateHelper('MediaStatus', MediaStatusCmdString, value, qualifier)

    def __MatchMediaStatus(self, match, tag):

        ValueStateValues = {
            'NC' : 'No Disc', 
            'CI' : 'Disc In'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MediaStatus', value, None)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '@0mt00\r', 
            'Off' : '@0mt01\r'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = '@0?mt\r'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '0' : 'On', 
            '1' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '@0PW00\r', 
            'Off' : '@0PW01\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '@0?PW\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '0' : 'On', 
            '1' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def UpdateRemainingTime(self, value, qualifier):

        RemainingTimeCmdString = '@0?RM\r'
        self.__UpdateHelper('RemainingTime', RemainingTimeCmdString, value, qualifier)

    def __MatchRemainingTime(self, match, tag):

        value = match.group(1).decode() + ':' + match.group(2).decode() + ':' + match.group(3).decode()
        if value[0] == '0' and value[1] == '0':
            value = value[2:]
        elif value[0] == '0' and value[1] != '0':
            value = value[1:]
        self.WriteStatus('RemainingTime', value, None)

    def SetSlowSearch(self, value, qualifier):

        ValueStateValues = {
            'Forward' : '@0PCSLSF\r', 
            'Reverse' : '@0PCSLSR\r'
        }

        SlowSearchCmdString = ValueStateValues[value]
        self.__SetHelper('SlowSearch', SlowSearchCmdString, value, qualifier)

    def UpdateSlowSearch(self, value, qualifier):

        SlowSearchCmdString = '@0?PCSLS\r'
        self.__UpdateHelper('SlowSearch', SlowSearchCmdString, value, qualifier)

    def __MatchSlowSearch(self, match, tag):

        ValueStateValues = {
            'F' : 'Forward', 
            'R' : 'Reverse'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SlowSearch', value, None)

    def SetTrackNumber(self, value, qualifier):

        if 1 <= value <= 2000:
            TrackNumberCmdString = '@0Tr{}\r'.format(str(value).zfill(4))
            self.__SetHelper('TrackNumber', TrackNumberCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackNumber')

    def UpdateTrackNumber(self, value, qualifier):

        TrackNumberCmdString = '@0?Tr\r'
        self.__UpdateHelper('TrackNumber', TrackNumberCmdString, value, qualifier)

    def __MatchTrackNumber(self, match, tag):

        value = match.group(1).decode()
        if value == 'UNKN':
            self.Error(['Unknown Track Number.'])
        else:
            self.WriteStatus('TrackNumber', int(value), None)

    def UpdateTrackTotal(self, value, qualifier):

        TrackTotalCmdString = '@0?Tt\r'
        self.__UpdateHelper('TrackTotal', TrackTotalCmdString, value, qualifier)

    def __MatchTrackTotal(self, match, tag):

        value = match.group(1).decode()
        if value == 'UNKN':
            self.Error(['Unknown Track Total.'])
        else:
            self.WriteStatus('TrackTotal', int(value), None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Stop'            : '@02354\r', 
            'Play'            : '@02353\r', 
            'Pause'           : '@02348\r', 
            'Track/Jump Next' : '@02332\r', 
            'Track/Jump Prev' : '@02333\r'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)
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

