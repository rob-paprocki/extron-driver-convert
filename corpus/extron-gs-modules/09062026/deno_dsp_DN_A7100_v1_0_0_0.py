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
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Surround': {'Status': {}},
            'TunerFrequency': {'Status': {}},
            'TunerMode': {'Status': {}},
            'TunerPreset': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'@AMT:(1|2)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'@SRC: (1|2|3|5|9|A|C|D|E|F|G|H)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'@PWR:(1|2)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'@SUR:(0|1|2|3|4|5|6|7|8|9|A|B|E|F|G|H|I|J|K|L|M|O|P|T|U)\r'), self.__MatchSurround, None)
            self.AddMatchString(re.compile(b'@TFQ:(1|2)\r'), self.__MatchTunerFrequency, None)
            self.AddMatchString(re.compile(b'@TMD:(0|1|2)\r'), self.__MatchTunerMode, None)
            self.AddMatchString(re.compile(b'@TPR:([0-9]{1,2})\r'), self.__MatchTunerPreset, None)
            self.AddMatchString(re.compile(b'@VMT:(1|2)\r'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(rb'@VOL:(-*\d+)\r'), self.__MatchVolume, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
            'Toggle': '0'
        }

        AudioMuteCmdString = '@AMT:' + ValueStateValues[value] + '\r'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '@AMT:?\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': '1',
            'DVD': '2',
            'VCR 1': '3',
            'VCR 2': '5',
            'AUX 1': '9',
            'AUX 2': 'A',
            'CD': 'C',
            'CD-R': 'D',
            'TAPE': 'E',
            'TUNER': 'F',
            'AM': 'G',
            'FM': 'H'
        }

        InputCmdString = '@SRC:' + ValueStateValues[value] + '\r'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '@SRC:?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '1': 'TV',
            '2': 'DVD',
            '3': 'VCR 1',
            '5': 'VCR 2',
            '9': 'AUX 1',
            'A': 'AUX 2',
            'C': 'CD',
            'D': 'CD-R',
            'E': 'TAPE',
            'F': 'TUNER',
            'H': 'AM',
            'G': 'FM'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
            'Toggle': '0'
        }

        PowerCmdString = '@PWR:' + ValueStateValues[value] + '\r'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '@PWR:?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSurround(self, value, qualifier):

        ValueStateValues = {
            'AUTO': '00',
            'STEREO': '01',
            'DOLBY': '02',
            'PL2x MOVIE': '03',
            'PL2 MOVIE': '04',
            'PL2x MUSIC': '05',
            'PL2 MUSIC': '06',
            'PL2x GAME': '07',
            'PL2 GAME': '08',
            'Dolby PROLOGIC': '09',
            'EX/ES': '0A',
            'VIRTUAL 6.1': '0B',
            'DTS ES': '0E',
            'NEO6 CINEMA': '0F',
            'NEO6 MUSIC': '0G',
            'Multi Ch STEREO': '0H',
            'CSII CINEMA': '0I',
            'CSII MUSIC': '0J',
            'CSII MONO': '0K',
            'VIRTUAL': '0L',
            'DTS': '0M',
            'DD+ PL2x MOVIE': '0O',
            'DD+ PL2x MUSIC': '0P',
            'SOURCE DIRECT': '0T',
            'PURE DIRECT': '0U',
            'UP': '1',
            'DOWN': '2'
        }

        SurroundCmdString = '@SUR:' + ValueStateValues[value] + '\r'
        if value != 'UP' and value != 'DOWN':
            self.__SetHelper('Surround', SurroundCmdString, value, qualifier)

    def UpdateSurround(self, value, qualifier):

        SurroundCmdString = '@SUR:?\r'
        self.__UpdateHelper('Surround', SurroundCmdString, value, qualifier)

    def __MatchSurround(self, match, tag):

        ValueStateValues = {
            '0': 'AUTO',
            '1': 'STEREO',
            '2': 'DOLBY',
            '3': 'PL2x MOVIE',
            '4': 'PL2 MOVIE',
            '5': 'PL2x MUSIC',
            '6': 'PL2 MUSIC',
            '7': 'PL2x GAME',
            '8': 'PL2 GAME',
            '9': 'Dolby PROLOGIC',
            'A': 'EX/ES',
            'B': 'VIRTUAL 6.1',
            'E': 'DTS ES',
            'F': 'NEO6 CINEMA',
            'G': 'NEO6 MUSIC',
            'H': 'Multi Ch STEREO',
            'I': 'CSII CINEMA',
            'J': 'CSII MUSIC',
            'K': 'CSII MONO',
            'L': 'VIRTUAL',
            'M': 'DTS',
            'O': 'DD+ PL2x MOVIE',
            'P': 'DD+ PL2x MUSIC',
            'T': 'SOURCE DIRECT',
            'U': 'PURE DIRECT'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Surround', value, None)

    def SetTunerFrequency(self, value, qualifier):

        ValueStateValues = {
            'Up': '1',
            'Down': '2'
        }

        TunerFrequencyCmdString = '@TFQ:' + ValueStateValues[value] + '\r'
        self.__SetHelper('TunerFrequency', TunerFrequencyCmdString, value, qualifier)

    def UpdateTunerFrequency(self, value, qualifier):

        TunerFrequencyCmdString = '@TFQ:?\r'
        self.__UpdateHelper('TunerFrequency', TunerFrequencyCmdString, value, qualifier)

    def __MatchTunerFrequency(self, match, tag):

        ValueStateValues = {
            '1': 'Up',
            '2': 'Down'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TunerFrequency', value, None)

    def SetTunerMode(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
            'None': '0'
        }

        TunerModeCmdString = '@TMD:' + ValueStateValues[value] + '\r'
        if value != 'None':
            self.__SetHelper('TunerMode', TunerModeCmdString, value, qualifier)

    def UpdateTunerMode(self, value, qualifier):

        TunerModeCmdString = '@TMD:?\r'
        self.__UpdateHelper('TunerMode', TunerModeCmdString, value, qualifier)

    def __MatchTunerMode(self, match, tag):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
            '0': 'None'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TunerMode', value, None)

    def SetTunerPreset(self, value, qualifier):

        value = value.zfill(2)
        TunerPresetCmdString = '@TPR:0' + value + '\r'
        self.__SetHelper('TunerPreset', TunerPresetCmdString, value, qualifier)

    def UpdateTunerPreset(self, value, qualifier):

        TunerPresetCmdString = '@TPR:?\r'
        self.__UpdateHelper('TunerPreset', TunerPresetCmdString, value, qualifier)

    def __MatchTunerPreset(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('TunerPreset', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1',
            'Toggle': '0'
        }

        VideoMuteCmdString = '@VMT:' + ValueStateValues[value] + '\r'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '@VMT:?\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -71,
            'Max': 18
            }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value == 0:
                VolumeCmdString = '@VOL:0 00\r'
            elif value < 0:
                VolumeCmdString = '@VOL:0{0:03d}\r'.format(value)
            elif 1 <= value:
                VolumeCmdString = '@VOL:0+{0:02d}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '@VOL:?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        self.WriteStatus('Volume', int(match.group(1).decode()), None)

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

