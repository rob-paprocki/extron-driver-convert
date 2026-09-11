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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Power': {'Status': {}},
            'RadioMode': {'Status': {}},
            'RemoteEmulation': {'Status': {}},
            'TuneFM': {'Status': {}},
            'Volume': {'Status': {}},
            }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'#COMMAND: <GCV>[\s\S]*#RET: (on|off);(100|[1-9][0-9]|[0-9])[\s\S]*#OK', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'#COMMAND: <GCS>[\s\S]*#RET: (on|off)[\s\S]*#OK', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'#COMMAND: <MODE>[\s\S]*#RET: (1|2|3)[\s\S]*#OK', re.I), self.__MatchRadioMode, None)
            self.AddMatchString(re.compile(b'#COMMAND: <FM STATE>[\s\S]*#RET: 0;(?:TRUE|FALSE);(\d+);[\s\S]*#OK', re.I), self.__MatchTuneFM, None)
            self.AddMatchString(re.compile(b'#ERROR:([\s\S]+)'), self.__MatchError, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '<VOL OFF>',
            'Off': '<VOL ON>'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '<GCV>'
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

    def SetRadioMode(self, value, qualifier):

        ValueStateValues = {
            'Idle': '<IDLE MODE>',
            'FM': '<FM MODE>',
            'DAB': '<DAB MODE>'
        }

        RadioModeCmdString = ValueStateValues[value]
        self.__SetHelper('RadioMode', RadioModeCmdString, value, qualifier)

    def UpdateRadioMode(self, value, qualifier):

        RadioModeCmdString = '<MODE>'
        self.__UpdateHelper('RadioMode', RadioModeCmdString, value, qualifier)

    def __MatchRadioMode(self, match, tag):

        ValueStateValues = {
            '1': 'Idle',
            '2': 'FM',
            '3': 'DAB'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RadioMode', value, None)

    def SetRemoteEmulation(self, value, qualifier):

        ValueStateValues = {
            'On/Off': '<RMC 22>',
            '1': '<RMC 2>',
            '2': '<RMC 5>',
            '3': '<RMC 6>',
            '4': '<RMC 9>',
            '5': '<RMC 10>',
            '6': '<RMC 13>',
            '7': '<RMC 14>',
            '8': '<RMC 17>',
            '9': '<RMC 18>',
            '0': '<RMC 21>',
            'Mode': '<RMC 34>',
            'Radio/TV': '<RMC 37>',
            'Mute': '<RMC 38>',
            'Last': '<RMC 41>',
            'Up': '<RMC 25>',
            'Down': '<RMC 26>',
            'Left': '<RMC 29>',
            'Right': '<RMC 33>',
            'OK': '<RMC 30>',
            'Menu': '<RMC 42>',
            'Exit': '<RMC 45>',
            'Red (DVR/PVR)': '<RMC 58>',
            'Green (DVD / MOVIE)': '<RMC 61>',
            'Yellow (MP3/FPEG/MUSIC)': '<RMC 62>',
            'Blue (GAME/MEDIA)': '<RMC 65>',
            'Rewind Back': '<RMC 46>',
            'Play/Pause': '<RMC 49>',
            'Rewind Forward': '<RMC 50>',
            'Go Previous': '<RMC 53>',
            'Record/Stop': '<RMC 54>',
            'Go Next': '<RMC 57>',
            'Info': '<RMC 66>',
            'EPG': '<RMC 69>',
            'Timer': '<RMC 70>',
            'TXT': '<RMC 73>',
            'PIP': '<RMC 74>',
            'Search/Freeze': '<RMC 77>',
            'Tech. Info/Zoom': '<RMC 78>',
            'Audio/Video': '<RMC 81>'
        }

        RemoteEmulationCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteEmulation', RemoteEmulationCmdString, value, qualifier)

    def SetTuneFM(self, value, qualifier):

        ValueConstraints = {
            'Min': 87.00,
            'Max': 108.00
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TuneFMCmdString = '<FM TUNE F {}>'.format(int(value * 100))
            self.__SetHelper('TuneFM', TuneFMCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTuneFM')

    def UpdateTuneFM(self, value, qualifier):

        TuneFMCmdString = '<FM STATE>'
        self.__UpdateHelper('TuneFM', TuneFMCmdString, value, qualifier)

    def __MatchTuneFM(self, match, tag):

        value = int(match.group(1).decode()) / 100
        self.WriteStatus('TuneFM', value, None)

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

        self.Error([match.group(0).decode()])

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
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

